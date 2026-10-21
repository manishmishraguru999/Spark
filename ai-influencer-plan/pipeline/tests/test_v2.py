"""Tests for v2 hardening: safety gate, QC, provenance, housekeeping, reports, doctor, projects."""
import json
import os
import subprocess
import time
from pathlib import Path

import pytest

from beast import provenance, qc, safety, stats
from beast.doctor import report, run_checks
from beast.housekeeping import cleanup_job_dirs
from beast.jobs import FAILED, PUBLISHED, REVIEW
from beast.media import probe
from beast.script_parser import parse_script
from beast.worker import Pipeline
from conftest import FakeResponse, FakeSession
from test_flow import MSG, FakeTG, msg


def make_video(path: Path, seconds: float, color="black", audio="sine") -> Path:
    a = ["-f", "lavfi", "-i", f"{audio}=duration={seconds}"] if audio == "sine" else \
        ["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=mono", "-t", str(seconds)]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={color}:s=1080x1920:d={seconds}",
                    *a, "-shortest", "-c:v", "libx264", "-c:a", "aac", str(path)], check=True)
    return path


# ---------- safety ----------
def test_rule_check_blocks_and_warns():
    s = parse_script("TITLE: t\nVO: यह दवा हर बीमारी का इलाज है guaranteed\nSCENE: x\nCAPTION: c")
    errors, warnings = safety.rule_check(s, {"blocked_names": ["Shah Rukh"], "blocked_words": ["guaranteed"]})
    assert errors == ["blocked word: guaranteed"]
    assert any("sensitive" in w for w in warnings) and any("source" in w for w in warnings)


def test_llm_review_parses_json():
    s = parse_script(MSG)
    body = json.dumps({"risk": "medium", "issues": ["claim unclear"], "claims_to_verify": ["tides stop"]})
    http = FakeSession([("POST", "/api/generate", FakeResponse({"response": body}))])
    out = safety.llm_review(s, {"model": "m"}, session=http)
    assert out["risk"] == "medium" and http.calls[0][2]["json"]["format"]["required"]


def test_safety_stage_stops_job_before_gpu(cfg, store):
    cfg.data["safety"]["blocked_words"] = ["थम"]
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    assert job.status == FAILED and "blocked word" in job.error and "voice" not in job.results
    assert "safety" in tg.sent[-1][2]


# ---------- QC ----------
def test_qc_fails_black_video(tmp_path):
    v = make_video(tmp_path / "black.mp4", 3)
    rep = qc.run_qc(v, {}, 1080, 1920, 90)
    assert rep.status == qc.FAIL and "black" in rep.summary()


def test_qc_warns_on_silence_and_wrong_size(tmp_path):
    v = make_video(tmp_path / "silent.mp4", 3, color="0x445566", audio="silent")
    rep = qc.run_qc(v, {}, 720, 1280, 90)
    names = {n: lvl for n, lvl, _ in rep.checks}
    assert names["resolution"] == qc.FAIL and names["silence"] == qc.WARN


def test_full_flow_has_qc_and_label(cfg, store):
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, MSG))
    while pipe.step():
        pass
    job = store.recent()[0]
    assert job.status == REVIEW and job.results["qc"]["status"] == "pass"
    tags = probe(Path(job.results["render"]))["format"].get("tags", {})
    assert "AI-generated" in tags.get("comment", "")
    video_msgs = [m for m in tg.sent if m[0] == "video"]
    assert video_msgs


# ---------- provenance ----------
def test_c2pa_manifest_uses_iptc_source_type():
    m = provenance.c2pa_manifest("BEAST", "full")
    action = m["assertions"][0]["data"]["actions"][0]
    assert action["digitalSourceType"].endswith("/trainedAlgorithmicMedia")


# ---------- housekeeping ----------
def test_cleanup_only_old_finished(tmp_path):
    jobs = tmp_path / "02_jobs"
    for name in ("old_done", "new_done", "old_running"):
        (jobs / name).mkdir(parents=True)
    old = time.time() - 30 * 86400
    for name in ("old_done", "old_running"):
        os.utime(jobs / name, (old, old))
    removed = cleanup_job_dirs(jobs, {"old_done", "new_done"}, 14)
    assert removed == ["old_done"] and (jobs / "old_running").exists()


def test_disk_guard_pauses_rendering(cfg, store):
    cfg.data["housekeeping"]["min_free_gb"] = 10 ** 9
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, MSG))
    assert pipe.step() is False and "Disk" in tg.sent[-1][2]
    assert pipe.step() is False and sum("Disk" in m[2] for m in tg.sent) == 1   # alert not repeated


# ---------- ideas, reports ----------
def test_idea_bank_commands(cfg, store):
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.handle_update(msg(42, "/idea अगर धरती घूमना बंद कर दे"))
    pipe.handle_update(msg(42, "/ideas"))
    assert "1. अगर धरती" in tg.sent[-1][2]
    pipe.handle_update(msg(42, "/used 1"))
    assert store.ideas() == []


def test_youtube_link_and_report(cfg, store):
    cfg.data["reports"]["youtube_api_key"] = "K"
    tg = FakeTG()
    pipe = Pipeline(cfg, store, tg=tg, now=lambda: time.time())
    job = store.create(parse_script(MSG).to_dict())
    job.status = PUBLISHED
    store.save(job)
    pipe.handle_update(msg(42, f"/yt {job.id} https://youtube.com/shorts/abcdefghijk"))
    assert store.get(job.id).results["published"]["youtube"]["id"] == "abcdefghijk"
    stats_http = FakeSession([("GET", "googleapis.com/youtube/v3/videos",
                               FakeResponse({"items": [{"id": "abcdefghijk", "statistics": {"viewCount": "1234"}}]}))])
    real = stats.requests.Session
    stats.requests.Session = lambda: stats_http
    try:
        text = pipe.report_text()
    finally:
        stats.requests.Session = real
    assert "YT 1,234" in text and "Queue" in text


def test_daily_report_runs_once_per_day(cfg, store):
    tg = FakeTG()
    t = {"now": 1_800_000_000.0}                       # 2027-01-15 13:30 IST, after 09:00
    pipe = Pipeline(cfg, store, tg=tg, now=lambda: t["now"])
    pipe.daily_tasks(); pipe.daily_tasks()
    assert sum("📊" in m[2] for m in tg.sent) == 1


def test_youtube_id_parsing():
    assert stats.youtube_id("https://youtube.com/shorts/abcdefghijk") == "abcdefghijk"
    assert stats.youtube_id("https://www.youtube.com/watch?v=abcdefghijk&t=1") == "abcdefghijk"
    assert stats.youtube_id("not a link") is None


# ---------- doctor, new project ----------
def test_doctor_reports_missing_items(cfg):
    cfg.data["publish"]["instagram"]["enabled"] = True
    cfg.data["publish"]["tiktok"] = {"enabled": True}
    checks = run_checks(cfg, network=False)
    text = report(checks)
    assert "FFmpeg filters" in text and "Instagram Reels credentials" in text and "India में blocked" in text


def test_new_project_creates_structure(tmp_path):
    import run_pipeline
    assert run_pipeline.new_project("SecondVenture", str(tmp_path)) == 0
    root = tmp_path / "SecondVenture"
    assert (root / "02_jobs").is_dir() and str(root.as_posix()) in (root / "pipeline_config.yaml").read_text(encoding="utf-8")
    assert run_pipeline.new_project("SecondVenture", str(tmp_path)) == 1          # no overwrite
    assert run_pipeline.new_project("bad name!", str(tmp_path)) == 1
