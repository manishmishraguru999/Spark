"""v3: word-pop captions, cover frame, benchmark mode, trend radar, backup."""
import sqlite3
import subprocess
from pathlib import Path

import pytest

from beast import captions, trends
from beast.backup import run_backup
from beast.benchmark import run_benchmark
from beast.jobs import REVIEW
from beast.publish.meta import publish_instagram
from beast.worker import Pipeline
from conftest import FakeResponse, FakeSession
from test_flow import MSG, FakeTG, msg, press

WORDS = [(0.0, 0.4, "सोचो"), (0.4, 0.9, "अगर"), (0.9, 1.3, "चाँद"), (1.3, 1.8, "गायब"), (1.8, 2.4, "हो।"),
         (2.6, 3.0, "फिर?")]


def test_group_and_pop_events():
    groups = captions.group_words(WORDS, max_words=3)
    assert [len(g) for g in groups] == [3, 2, 1]                  # sentence end "हो।" closes a group
    ev = captions.pop_events(WORDS)
    assert len(ev) == len(WORDS)
    assert r"{\c&H00E5FF&" in ev[0][2] and ev[0][2].count("{\\r}") == 1
    assert ev[0][1] == WORDS[1][0]                                # held until the next word starts


def test_word_captions_used_in_render(cfg, store, monkeypatch):
    cfg.data["captions"]["mode"] = "words"
    monkeypatch.setattr(captions, "transcribe_words", lambda *a, **k: WORDS)
    pipe = Pipeline(cfg, store, tg=FakeTG())
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    assert job.status == REVIEW
    ass = (cfg.path("02_jobs") / job.id / "captions.ass").read_text(encoding="utf-8")
    assert r"\c&H00E5FF&" in ass
    assert Path(job.results["cover"]).exists()


def test_word_captions_fallback_without_package(cfg, store, monkeypatch):
    cfg.data["captions"]["mode"] = "words"

    def missing(*a, **k):
        raise ImportError("No module named 'faster_whisper'")
    monkeypatch.setattr(captions, "transcribe_words", missing)
    pipe = Pipeline(cfg, store, tg=FakeTG())
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    assert job.status == REVIEW and any("word captions" in w for w in job.results["warnings"])


def test_instagram_thumb_offset(tmp_path):
    video = tmp_path / "v.mp4"; video.write_bytes(b"x")
    http = FakeSession([("POST", "/1/media_publish", FakeResponse({"id": "M"})),
                        ("POST", "/1/media", FakeResponse({"id": "C"})),
                        ("POST", "ig-api-upload", FakeResponse({})),
                        ("GET", "/C", FakeResponse({"status_code": "FINISHED"}))])
    cfg = {"graph_host": "https://g", "rupload_host": "https://r", "version": "v1", "ig_user_id": "1",
           "access_token": "T", "thumb_offset_ms": 1500}
    publish_instagram(cfg, video, "c", session=http, poll_sec=0)
    assert http.calls[0][2]["data"]["thumb_offset"] == "1500"


def test_benchmark_with_local_tools(cfg, tmp_path):
    faces = []
    for name, color in (("face_A", "red"), ("face_B", "blue")):
        f = tmp_path / f"{name}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=540x960:d=1",
                        "-frames:v", "1", str(f)], check=True)
        faces.append(str(f))
    fake_lipsync = 'ffmpeg -v error -y -loop 1 -i "{face}" -i "{audio}" -shortest -c:v libx264 -pix_fmt yuv420p "{out}"'
    cfg.data["benchmark"] = {"talk_seconds": 3, "faces": faces,
                             "voices": [{"name": "toneA", "provider": "silent"},
                                        {"name": "broken", "provider": "command", "command": "exit 1"}],
                             "lipsync": [{"name": "fake1", "command": fake_lipsync},
                                         {"name": "bad", "command": "exit 3"}]}
    res = run_benchmark(cfg)
    oks = {(r["test"], r["variant"]): r["ok"] for r in res["rows"]}
    assert oks[("voice", "toneA")] == "yes" and oks[("voice", "broken")] == "no"
    assert oks[("lipsync", "face_A__fake1")] == "yes" and oks[("lipsync", "face_B__bad")] == "no"
    assert Path(res["grid"]).exists() and "face_A__fake1" in res["order"]
    csv_text = (Path(res["dir"]) / "results.csv").read_text(encoding="utf-8-sig")
    assert "rating_lipsync_1to5" in csv_text


def test_trend_digest_and_idea_button(cfg, store):
    vids = lambda ids: FakeResponse({"items": [
        {"id": i, "snippet": {"title": f"Video {i}", "channelTitle": "C"}, "statistics": {"viewCount": str(v)}}
        for i, v in ids]})
    http = FakeSession([
        ("GET", "/search", FakeResponse({"items": [{"id": {"videoId": "kw1"}}]})),
        ("GET", "/videos", vids([("kw1", 500)])),
        ("GET", "/videos", vids([("pop1", 9000), ("kw1", 500)])),
    ])
    items = trends.digest("K", ["what if hindi"], session=http, now=1_800_000_000)
    assert [i["id"] for i in items] == ["pop1", "kw1"] and items[1]["keyword"] == "what if hindi"
    search_params = http.calls[0][2]["params"]
    assert search_params["regionCode"] == "IN" and search_params["publishedAfter"].endswith("Z")

    cfg.data["reports"]["youtube_api_key"] = "K"
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    real = trends.digest
    trends.digest = lambda *a, **k: items
    try:
        pipe.handle_update(msg(42, "/trends"))
    finally:
        trends.digest = real
    assert "Trend radar" in tg.sent[-1][2] and tg.sent[-1][3][0][0][1] == "trend:0"
    pipe.handle_update(press(42, "trend:1"))
    assert "Video kw1" in store.ideas()[0][1]


def test_backup_copies_and_refuses_inside(cfg, store, tmp_path):
    (cfg.path("03_renders") / "a.mp4").write_bytes(b"video")
    store.create({"title": "x"})
    dest = tmp_path / "BACKUP"
    counts = run_backup(cfg.root, dest, cfg.path("06_logs") / "jobs.sqlite")
    assert counts["03_renders"] == 1 and (dest / "03_renders" / "a.mp4").exists()
    assert run_backup(cfg.root, dest, cfg.path("06_logs") / "jobs.sqlite")["03_renders"] == 0   # incremental
    with sqlite3.connect(str(dest / "06_logs" / "jobs.sqlite")) as db:
        assert db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1
    with pytest.raises(ValueError):
        run_backup(cfg.root, cfg.root / "inside", cfg.path("06_logs") / "jobs.sqlite")


def test_weekly_backup_schedule(cfg, store, tmp_path):
    cfg.data["backup"] = {"dest": str(tmp_path / "BK"), "every_days": 7}
    t = {"now": 1_800_000_000.0}
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg, now=lambda: t["now"])
    pipe.do_backup(); pipe.do_backup()
    assert sum("Backup" in m[2] for m in tg.sent) == 1
    t["now"] += 8 * 86400
    pipe.do_backup()
    assert sum("Backup" in m[2] for m in tg.sent) == 2
