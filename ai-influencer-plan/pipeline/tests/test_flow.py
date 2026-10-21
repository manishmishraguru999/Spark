"""End-to-end: phone message → render → preview → approve → scheduled → publish (dry run)."""
import json
from pathlib import Path

from beast.jobs import CANCELLED, PUBLISHED, REVIEW, RUNNING, SCHEDULED
from beast.media import duration, video_size
from beast.worker import Pipeline

MSG = """/new
TITLE: अगर चाँद गायब हो जाए तो?
HOOK: सोचो!
VO: लहरें थम जाएँगी। रातें अंधेरी होंगी।
SCENE: night sky without moon
SCENE: flat ocean
TAGS: #whatif #science
"""


class FakeTG:
    def __init__(self):
        self.sent = []

    def send_message(self, chat, text, buttons=None):
        self.sent.append(("msg", chat, text, buttons))

    def send_video(self, chat, path, caption, buttons=None):
        self.sent.append(("video", chat, str(path), buttons))

    def answer_callback(self, cid, text=""):
        pass


def msg(chat, text):
    return {"update_id": 1, "message": {"chat": {"id": chat}, "text": text}}


def press(chat, data):
    return {"update_id": 2, "callback_query": {"id": "c", "data": data, "message": {"chat": {"id": chat}}}}


def test_full_flow_dry_run(cfg, store):
    clock = {"t": 1_800_000_000.0}
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg, now=lambda: clock["t"])

    pipe.handle_update(msg(999, MSG))                       # stranger is ignored
    assert store.recent() == []

    pipe.handle_update(msg(42, MSG))
    job = store.recent()[0]
    assert job.status == RUNNING
    while pipe.step():
        pass
    job = store.get(job.id)
    assert job.status == REVIEW
    render = Path(job.results["render"])
    assert video_size(render) == (1080, 1920) and 1.0 < duration(render) <= 90
    assert any(kind == "video" for kind, *_ in tg.sent)     # preview reached the phone

    pipe.handle_update(press(42, f"approve:{job.id}"))
    job = store.get(job.id)
    assert job.status == SCHEDULED and job.scheduled_at > clock["t"]

    assert pipe.publish_due() is False                      # not yet time
    clock["t"] = job.scheduled_at + 1
    assert pipe.publish_due() is True
    job = store.get(job.id)
    assert job.status == PUBLISHED
    record = json.loads((cfg.path("05_published") / f"{job.id}.json").read_text(encoding="utf-8"))
    assert record["published"]["youtube"]["dry_run"] is True


def test_youtube_manual_handoff(cfg, store):
    cfg.data["publish"]["dry_run"] = False
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
    assert job.status == PUBLISHED and job.results["published"]["youtube"]["manual"] is True
    sync = Path(cfg.get("publish.youtube.manual_sync_dir"))
    assert (sync / f"{job.id}.mp4").exists()
    assert "Altered or synthetic content = YES" in (sync / f"{job.id}.txt").read_text(encoding="utf-8")


def test_redo_and_cancel(cfg, store):
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    seed = job.seed
    pipe.handle_update(press(42, f"redo_img:{job.id}"))
    job = store.get(job.id)
    assert job.status == RUNNING and job.stage == 1 and job.seed != seed
    pipe.handle_update(press(42, f"cancel:{job.id}"))
    assert store.get(job.id).status == CANCELLED


def test_bad_script_reports_error(cfg, store):
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, "/new\nTITLE: only title"))
    assert store.recent() == [] and "गलती" in tg.sent[-1][2]


def test_stage_failure_retries_then_fails(cfg, store, monkeypatch):
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, MSG))

    def boom(*a, **k):
        raise RuntimeError("GPU out of memory")
    monkeypatch.setattr(pipe, "stage_tts", boom)
    for _ in range(3):
        pipe.step()
    job = store.recent()[0]
    assert job.status == "failed" and "out of memory" in job.error
    assert "fail" in tg.sent[-1][2]
