import subprocess
from pathlib import Path

import pytest

from beast.jobs import PUBLISHED, SCHEDULED
from beast.publish import plugins
from beast.publish.registry import PLATFORMS, PublishContext, check_duration, manual_handoff, resolve
from beast.worker import Pipeline
from conftest import FakeResponse, FakeSession
from test_flow import MSG, FakeTG, msg


def make_video(path: Path, seconds: float) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=64x112:d={seconds}",
                    "-f", "lavfi", "-i", f"sine=duration={seconds}", "-shortest", "-c:v", "libx264", "-c:a", "aac",
                    str(path)], check=True)
    return path


@pytest.fixture
def video(tmp_path):
    return make_video(tmp_path / "v.mp4", 2)


def ctx(platform, video, tmp_path, cfg=None, caption="कैप्शन", tags=("#a", "#b", "#c")):
    return PublishContext(platform=platform, job_id="J1", video=video, title="Title", caption=caption,
                          tags=list(tags), cfg=cfg or {}, root=tmp_path)


def test_every_platform_has_sane_spec():
    for name, spec in PLATFORMS.items():
        assert spec.max_seconds > 0 and spec.max_caption > 0, name
        assert spec.api in {"ready", "needs_public_url", "paid", "business_only", "manual", "blocked_india"}


def test_caption_respects_platform_limits(video, tmp_path):
    c = ctx("x", video, tmp_path, caption="अ" * 400)
    text = c.formatted_caption()
    assert len(text) <= 280 and text.endswith("#a #b")          # X: 2 hashtags max, 280 chars
    assert ctx("threads", video, tmp_path).formatted_caption().endswith("#a")


def test_resolve_manual_and_blocked():
    assert resolve("moj", {}) is manual_handoff                   # no API plugin
    assert resolve("threads", {"mode": "manual"}) is manual_handoff
    assert resolve("pinterest", {}) is plugins.publish_pinterest
    assert resolve("youtube", {"mode": "manual"}) is plugins.publish_youtube   # YouTube keeps its own manual flow
    with pytest.raises(ValueError):
        resolve("tiktok", {})


def test_manual_handoff_writes_video_and_caption(video, tmp_path):
    res = manual_handoff(ctx("sharechat", video, tmp_path))
    assert res["manual"] and Path(res["path"]).exists()
    txt = (tmp_path / "05_published" / "manual" / "sharechat" / "J1.txt").read_text(encoding="utf-8")
    assert "ShareChat" in txt and "AI/altered-content label ON" in txt


def test_duration_check(tmp_path):
    long_video = make_video(tmp_path / "long.mp4", 95)
    assert "limit" in check_duration(ctx("facebook", long_video, tmp_path))
    assert check_duration(ctx("youtube", long_video, tmp_path)) == ""


def test_telegram_channel(video, tmp_path, monkeypatch):
    http = FakeSession([("POST", "/sendVideo", FakeResponse({"ok": True, "result": {"message_id": 7}}))])
    monkeypatch.setattr(plugins, "HTTP", http)
    res = plugins.publish_telegram_channel(ctx("telegram_channel", video, tmp_path,
                                               {"bot_token": "B", "channel_id": "@mychan"}))
    assert res["url"] == "https://t.me/mychan/7"
    assert http.calls[0][2]["data"]["chat_id"] == "@mychan"


def test_threads_flow(video, tmp_path, monkeypatch):
    pub = tmp_path / "public"; pub.mkdir()
    http = FakeSession([
        ("POST", "/U/threads_publish", FakeResponse({"id": "T9"})),
        ("POST", "/U/threads", FakeResponse({"id": "C1"})),
        ("GET", "/C1", FakeResponse({"status": "IN_PROGRESS"})),
        ("GET", "/C1", FakeResponse({"status": "FINISHED"})),
    ])
    monkeypatch.setattr(plugins, "HTTP", http)
    cfg = {"user_id": "U", "access_token": "T", "public_dir": str(pub), "public_base_url": "https://cdn.example/v"}
    res = plugins.publish_threads(ctx("threads", video, tmp_path, cfg), poll_sec=0)
    assert res["id"] == "T9" and (pub / "J1.mp4").exists()
    assert http.calls[0][2]["data"]["video_url"] == "https://cdn.example/v/J1.mp4"


def test_pinterest_flow(video, tmp_path, monkeypatch):
    http = FakeSession([
        ("POST", "/v5/media", FakeResponse({"media_id": "M", "upload_url": "https://s3.example/up",
                                            "upload_parameters": {"key": "k"}})),
        ("POST", "s3.example", FakeResponse(status=204, content=b" ")),
        ("GET", "/v5/media/M", FakeResponse({"status": "processing"})),
        ("GET", "/v5/media/M", FakeResponse({"status": "succeeded"})),
        ("POST", "/v5/pins", FakeResponse({"id": "P1"})),
    ])
    monkeypatch.setattr(plugins, "HTTP", http)
    res = plugins.publish_pinterest(ctx("pinterest", video, tmp_path, {"access_token": "T", "board_id": "B"}),
                                    poll_sec=0)
    assert res["id"] == "P1"
    pin_body = http.calls[-1][2]["json"]
    assert pin_body["media_source"]["media_id"] == "M" and pin_body["board_id"] == "B"


def test_worker_publishes_to_many_platforms(cfg, store):
    cfg.data["publish"]["dry_run"] = False
    for p in ("instagram", "facebook"):
        cfg.data["publish"][p]["enabled"] = False
    cfg.data["publish"]["moj"] = {"enabled": True, "mode": "manual"}
    cfg.data["publish"]["sharechat"] = {"enabled": True, "mode": "manual"}
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg, now=lambda: 2_000_000_000.0)
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    job.status, job.scheduled_at = SCHEDULED, 1.0
    store.save(job)
    pipe.publish_due()
    job = store.get(job.id)
    assert job.status == PUBLISHED
    assert set(job.results["published"]) == {"youtube", "moj", "sharechat"}
    assert "phone से post करें" in tg.sent[-1][2]
