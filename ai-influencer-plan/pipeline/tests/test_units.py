import base64
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from beast.captions import split_caption_lines, timed_lines
from beast.comfy import ComfyClient, fill_template
from beast.publish.meta import PublishError, publish_facebook, publish_instagram
from beast.schedule import next_slot
from beast.script_parser import ScriptError, parse_script
from beast.tts import _chunks, sarvam_tts
from conftest import FakeResponse, FakeSession

SCRIPT = """/new
title: अगर सूरज गायब हो जाए तो?
HOOK: सोचो!
VO: पहले 8 मिनट कुछ पता नहीं चलेगा।
फिर अंधेरा।
SCENE: dark earth from space
SCENE: frozen city
TALK: no
TAGS: #whatif #science #hindi #extra
"""


def test_parse_script_fields_and_continuation():
    s = parse_script(SCRIPT)
    assert s.title.startswith("अगर सूरज")
    assert s.vo == "पहले 8 मिनट कुछ पता नहीं चलेगा। फिर अंधेरा।"
    assert s.scenes == ["dark earth from space", "frozen city"]
    assert s.talk is False
    assert s.tags == ["#whatif", "#science", "#hindi"]          # max 3 hashtags
    assert s.narration.startswith("सोचो!")


@pytest.mark.parametrize("bad", ["VO: x\nSCENE: y", "TITLE: t\nSCENE: y", "TITLE: t\nVO: x"])
def test_parse_script_missing_fields(bad):
    with pytest.raises(ScriptError):
        parse_script(bad)


def test_captions_split_and_timing():
    lines = split_caption_lines("एक दो तीन चार पाँच छह सात आठ नौ दस ग्यारह बारह", max_chars=12)
    assert all(len(l) <= 14 for l in lines) and len(lines) > 1
    timed = timed_lines("पहला वाक्य। दूसरा वाक्य।", 10.0)
    assert timed[0][0] == 0 and abs(timed[-1][1] - 10.0) < 1e-6


def test_tts_chunks_respect_limit():
    text = "यह एक वाक्य है। " * 50
    parts = _chunks(text, 100)
    assert all(len(p) <= 100 for p in parts) and "".join(parts).count("वाक्य") == 50


def test_fill_template_keeps_seed_int():
    wf = {"3": {"inputs": {"seed": "{{SEED}}", "text": "photo, {{PROMPT}}"}}}
    out = fill_template(wf, {"SEED": 7, "PROMPT": "moon"})
    assert out["3"]["inputs"] == {"seed": 7, "text": "photo, moon"}


def test_comfy_run_workflow(tmp_path):
    wf = tmp_path / "wf.json"
    wf.write_text(json.dumps({"1": {"inputs": {"text": "{{PROMPT}}"}}}), encoding="utf-8")
    outputs = {"9": {"images": [{"filename": "a.png", "subfolder": "", "type": "output"}]}}
    http = FakeSession([
        ("POST", "/prompt", FakeResponse({"prompt_id": "p1"})),
        ("GET", "/history/p1", FakeResponse({})),
        ("GET", "/history/p1", FakeResponse({"p1": {"outputs": outputs, "status": {"completed": True}}})),
        ("GET", "/view", FakeResponse(content=b"PNGDATA")),
    ])
    client = ComfyClient("http://127.0.0.1:8188", session=http, poll_sec=0)
    files = client.run_workflow(wf, {"PROMPT": "moon"}, tmp_path, "scene00")
    assert files[0].read_bytes() == b"PNGDATA"
    assert http.calls[0][2]["json"]["prompt"]["1"]["inputs"]["text"] == "moon"


def test_sarvam_tts_decodes_audio(cfg, tmp_path, monkeypatch):
    cfg.data["tts"]["sarvam"]["api_key"] = "k"
    wav = tmp_path / "src.wav"
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=duration=1", str(wav)], check=True)
    audio_b64 = base64.b64encode(wav.read_bytes()).decode()
    http = FakeSession([("POST", "text-to-speech", FakeResponse({"audios": [audio_b64]}), True)])
    out = sarvam_tts(cfg, "नमस्ते दुनिया।", tmp_path / "voice.wav", session=http)
    assert out.exists() and out.stat().st_size > 1000
    body = http.calls[0][2]["json"]
    assert body["target_language_code"] == "hi-IN" and http.calls[0][2]["headers"]["api-subscription-key"] == "k"


def test_instagram_resumable_flow(tmp_path):
    video = tmp_path / "v.mp4"
    video.write_bytes(b"x" * 10)
    cfg = {"graph_host": "https://graph.instagram.com", "rupload_host": "https://rupload.facebook.com",
           "version": "v25.0", "ig_user_id": "17", "access_token": "T"}
    http = FakeSession([
        ("POST", "/17/media_publish", FakeResponse({"id": "M1"})),
        ("POST", "/17/media", FakeResponse({"id": "C1"})),
        ("POST", "ig-api-upload/v25.0/C1", FakeResponse({"success": True})),
        ("GET", "/C1", FakeResponse({"status_code": "IN_PROGRESS"})),
        ("GET", "/C1", FakeResponse({"status_code": "FINISHED"})),
    ])
    res = publish_instagram(cfg, video, "caption", session=http, poll_sec=0)
    assert res["id"] == "M1"
    upload = [c for c in http.calls if "ig-api-upload" in c[1]][0]
    assert upload[2]["headers"]["file_size"] == "10" and upload[2]["headers"]["Authorization"] == "OAuth T"


def test_instagram_error_status(tmp_path):
    video = tmp_path / "v.mp4"; video.write_bytes(b"x")
    cfg = {"graph_host": "https://g", "rupload_host": "https://r", "version": "v1", "ig_user_id": "1",
           "access_token": "T"}
    http = FakeSession([("POST", "/1/media", FakeResponse({"id": "C"})), ("POST", "ig-api-upload", FakeResponse({})),
                        ("GET", "/C", FakeResponse({"status_code": "ERROR"}))])
    with pytest.raises(PublishError):
        publish_instagram(cfg, video, "c", session=http, poll_sec=0)


def test_facebook_reels_flow(tmp_path):
    video = tmp_path / "v.mp4"; video.write_bytes(b"abc")
    cfg = {"graph_host": "https://graph.facebook.com", "rupload_host": "https://rupload.facebook.com",
           "version": "v25.0", "page_id": "P", "page_access_token": "T"}
    http = FakeSession([
        ("POST", "/P/video_reels", FakeResponse({"video_id": "V", "upload_url": "https://rupload.facebook.com/video-upload/v25.0/V"})),
        ("POST", "video-upload/v25.0/V", FakeResponse({"success": True})),
        ("POST", "/P/video_reels", FakeResponse({"success": True})),
    ])
    res = publish_facebook(cfg, video, "desc", "title", session=http)
    assert res["id"] == "V"
    assert http.calls[0][2]["data"]["upload_phase"] == "start"
    assert http.calls[2][2]["data"]["video_state"] == "PUBLISHED"


def test_next_slot_skips_past_and_taken():
    tz = ZoneInfo("Asia/Kolkata")
    now = datetime(2026, 10, 21, 18, 50, tzinfo=tz).timestamp()
    first = next_slot(now, ["19:00"], [], min_gap_min=30)         # 19:00 too close → tomorrow
    assert datetime.fromtimestamp(first, tz).day == 22
    second = next_slot(now, ["19:00"], [first], min_gap_min=30)
    assert datetime.fromtimestamp(second, tz).day == 23
