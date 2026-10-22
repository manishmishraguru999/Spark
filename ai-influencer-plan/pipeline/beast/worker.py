"""The pipeline brain: turns phone messages into jobs, runs one stage at a time,
sends previews for approval, and publishes approved videos at their slot."""
from __future__ import annotations

import json
import logging
import time
import traceback
from pathlib import Path

from . import assemble as asm
from . import captions, provenance, qc, safety, stats, trends
from .backup import run_backup
from .comfy import ComfyClient
from .config import Config
from .doctor import report as doctor_report, run_checks
from .housekeeping import cleanup_job_dirs, free_gb
from .jobs import (CANCELLED, FAILED, PUBLISHED, PUBLISHING, REVIEW, RUNNING, SCHEDULED, STAGES, Job,
                   JobStore)
from .lipsync import cut_audio, lipsync
from .media import ffmpeg_bin, run
from .publish.meta import refresh_instagram_token
from .publish.registry import PLATFORMS, PublishContext, check_duration, resolve
from .schedule import fmt, next_slot
from .script_parser import Script, ScriptError, parse_script
from .tts import synthesize

log = logging.getLogger("beast")
MAX_ATTEMPTS = 3

HELP = """BEAST pipeline commands
/new + script     → नया Reel (format: TITLE/HOOK/VO/SCENE/TALK/CAPTION/TAGS)
/status           → चल रहे और pending jobs
/cancel <id>      → job रद्द
/idea <text>      → idea bank में जोड़ें
/ideas            → बचे हुए ideas
/used <n>         → idea नंबर n हो गया
/yt <id> <link>   → YouTube link जोड़ें (views report के लिए)
/report           → views + queue report अभी
/trends           → आज के trending ideas (YouTube API key चाहिए)
/backup           → अभी backup
/health           → PC और setup की जाँच
/help             → यह message"""


class Pipeline:
    def __init__(self, cfg: Config, store: JobStore, tg=None, comfy: ComfyClient | None = None, now=time.time):
        self.cfg, self.store, self.tg, self.now = cfg, store, tg, now
        self.comfy = comfy
        if self.comfy is None and cfg.get("comfyui.enabled", False):
            self.comfy = ComfyClient(cfg.get("comfyui.url", "http://127.0.0.1:8188"))
        self.allowed = {int(x) for x in cfg.get("telegram.allowed_chat_ids", []) or []}
        self.tz = cfg.get("schedule.timezone", "Asia/Kolkata")

    # ---------- phone side ----------
    def notify(self, text: str, video: Path | None = None, buttons=None) -> None:
        log.info("notify: %s", text.splitlines()[0] if text else "")
        if not self.tg:
            return
        for chat in self.allowed:
            try:
                if video:
                    self.tg.send_video(chat, video, text, buttons)
                else:
                    self.tg.send_message(chat, text, buttons)
            except Exception as exc:  # never let a notification crash the pipeline
                log.warning("Telegram send failed: %s", exc)

    def handle_update(self, upd: dict) -> None:
        if "callback_query" in upd:
            cq = upd["callback_query"]
            if int(cq["message"]["chat"]["id"]) not in self.allowed:
                return
            self.tg and self.tg.answer_callback(cq["id"], "OK")
            action, _, job_id = cq.get("data", "").partition(":")
            self.handle_action(action, job_id)
            return
        msg = upd.get("message") or {}
        chat = int(msg.get("chat", {}).get("id", 0))
        text = (msg.get("text") or "").strip()
        if chat not in self.allowed:
            log.warning("Ignored message from chat %s (not in allowed_chat_ids)", chat)
            return
        if text.lower().startswith("/new"):
            try:
                script = parse_script(text, int(self.cfg.get("publish.max_hashtags", 3)))
            except ScriptError as exc:
                self.notify(f"❌ Script में गलती: {exc}\n\n{HELP}")
                return
            job = self.store.create(script.to_dict())
            self.notify(f"✅ Job {job.id} बना: {script.title}\n{len(script.scenes)} scenes · rendering शुरू")
        elif text.lower().startswith("/status"):
            self.notify(self.status_text())
        elif text.lower().startswith("/cancel"):
            parts = text.split()
            self.handle_action("cancel", parts[1] if len(parts) > 1 else "")
        elif text.lower().startswith("/ideas"):
            ideas = self.store.ideas()
            self.notify("\n".join(f"{i}. {t}" for i, t, _ in ideas) or "Idea bank खाली है। /idea से जोड़ें।")
        elif text.lower().startswith("/idea"):
            body = text[5:].strip()
            if body:
                self.notify(f"💡 Idea #{self.store.add_idea(body)} saved")
        elif text.lower().startswith("/used"):
            parts = text.split()
            if len(parts) > 1 and parts[1].isdigit():
                self.store.mark_idea(int(parts[1]))
                self.notify(f"✔️ Idea #{parts[1]} used")
        elif text.lower().startswith("/yt"):
            self.attach_youtube(text.split()[1:])
        elif text.lower().startswith("/report"):
            self.notify(self.report_text())
        elif text.lower().startswith("/trends"):
            self.send_trends()
        elif text.lower().startswith("/backup"):
            self.do_backup(force=True)
        elif text.lower().startswith("/health"):
            self.notify(doctor_report(run_checks(self.cfg)))
        else:
            self.notify(HELP)

    def handle_action(self, action: str, job_id: str) -> None:
        if action == "trend":
            self.trend_to_idea(job_id)
            return
        job = self.store.get(job_id)
        if not job:
            self.notify(f"Job {job_id} नहीं मिला")
            return
        if action == "approve" and job.status == REVIEW:
            taken = [j.scheduled_at for j in self.store.by_status(SCHEDULED) if j.scheduled_at]
            job.scheduled_at = next_slot(self.now(), self.cfg.get("schedule.publish_times", ["19:00"]), taken, self.tz)
            job.status = SCHEDULED
            self.store.save(job)
            self.notify(f"📅 {job.id} approved · publish: {fmt(job.scheduled_at, self.tz)}")
        elif action in ("redo_img", "redo_voice") and job.status in (REVIEW, FAILED):
            job.stage = STAGES.index("images") if action == "redo_img" else 0
            job.seed += 1000
            job.status, job.error, job.attempts = RUNNING, "", 0
            self.store.save(job)
            self.notify(f"🔁 {job.id} दोबारा बन रहा है ({'images' if action == 'redo_img' else 'voice से'})")
        elif action == "cancel" and job.status not in (PUBLISHED, PUBLISHING):
            job.status = CANCELLED
            self.store.save(job)
            self.notify(f"🗑️ {job.id} cancelled")

    def status_text(self) -> str:
        jobs = self.store.recent(10)
        if not jobs:
            return "कोई job नहीं है। /new से शुरू करें।"
        lines = []
        for j in jobs:
            extra = f" · {fmt(j.scheduled_at, self.tz)}" if j.status == SCHEDULED and j.scheduled_at else ""
            stage = f" [{j.stage_name}]" if j.status == RUNNING else ""
            lines.append(f"{j.id} · {j.status}{stage}{extra} · {j.script.get('title', '')[:40]}")
        return "\n".join(lines)

    # ---------- render side ----------
    def job_dir(self, job: Job) -> Path:
        d = self.cfg.path("02_jobs") / job.id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def step(self) -> bool:
        """Run one stage of the oldest running job. Returns True if work was done."""
        running = self.store.by_status(RUNNING)
        if not running:
            return False
        min_gb = float(self.cfg.get("housekeeping.min_free_gb", 30))
        if free_gb(self.cfg.root) < min_gb:
            last = float(self.store.kv_get("disk_alert", "0") or 0)
            if self.now() - last > 6 * 3600:
                self.store.kv_set("disk_alert", str(self.now()))
                self.notify(f"💾 Disk {free_gb(self.cfg.root):.0f} GB बचा है (< {min_gb:.0f} GB)। Rendering रोकी गई है।")
            return False
        job = running[0]
        stage = STAGES[job.stage]
        try:
            getattr(self, f"stage_{stage}")(job, Script.from_dict(job.script), self.job_dir(job))
            if job.status == RUNNING:
                job.stage += 1
            job.attempts = 0
        except Exception as exc:
            job.attempts += 1
            job.error = f"{stage}: {exc}"
            log.error("Job %s stage %s failed: %s\n%s", job.id, stage, exc, traceback.format_exc())
            if job.attempts >= MAX_ATTEMPTS:
                job.status = FAILED
                self.notify(f"⚠️ {job.id} fail ({stage}): {str(exc)[:300]}",
                            buttons=[[("🔁 Images फिर से", f"redo_img:{job.id}"),
                                      ("🎙️ Voice से", f"redo_voice:{job.id}")]])
        self.store.save(job)
        return True

    def stage_check(self, job: Job, script: Script, d: Path) -> None:
        errors, warnings = safety.rule_check(script, self.cfg.get("safety", {}) or {})
        if errors:
            job.status = FAILED
            job.error = "; ".join(errors)
            self.notify(f"🛑 {job.id} रोका गया (safety): {job.error}\nScript ठीक करके /new फिर भेजें।")
            return
        ollama = self.cfg.get("safety.ollama", {}) or {}
        if ollama.get("enabled") and ollama.get("model"):
            try:
                review = safety.llm_review(script, ollama)
                job.results["review"] = review
                if review.get("risk") in ("medium", "high"):
                    warnings.append(f"AI review risk: {review['risk']} — " + "; ".join(review.get("issues", [])[:3]))
            except Exception as exc:          # review is advisory; never block on it
                warnings.append(f"AI review नहीं चला: {str(exc)[:80]}")
        job.results["warnings"] = warnings

    def stage_tts(self, job: Job, script: Script, d: Path) -> None:
        provider = self.cfg.get("tts.provider", "sarvam")
        voice = d / "voice.wav"
        if provider == "silent":                      # demo/test: tone sized to the text
            secs = max(3.0, len(script.narration) / 14.0)
            run([ffmpeg_bin(), "-y", "-f", "lavfi", "-i", f"sine=frequency=220:duration={secs:.2f}",
                 "-ar", "48000", "-ac", "1", str(voice)])
        else:
            synthesize(self.cfg, script.narration, voice)
        job.results["voice"] = str(voice)

    def stage_images(self, job: Job, script: Script, d: Path) -> None:
        images = []
        style = self.cfg.get("comfyui.style_prefix", "")
        negative = self.cfg.get("comfyui.negative", "")
        for i, scene in enumerate(script.scenes):
            target = d / f"scene{i:02d}"
            if self.comfy and self.cfg.get("comfyui.image_workflow"):
                files = self.comfy.run_workflow(Path(self.cfg.get("comfyui.image_workflow")),
                                                {"PROMPT": f"{style} {scene}".strip(), "NEGATIVE": negative,
                                                 "SEED": job.seed + i, "PREFIX": f"{job.id}_s{i}"},
                                                d, target.name, float(self.cfg.get("comfyui.timeout_sec", 1800)))
                images.append(str(files[0]))
            else:                                     # placeholder card so the rest of the pipeline still runs
                out = target.with_suffix(".png")
                hue = (job.seed + i * 47) % 360
                run([ffmpeg_bin(), "-y", "-f", "lavfi", "-i", "color=c=0x223344:s=1080x1920:d=1",
                     "-vf", f"hue=h={hue}", "-frames:v", "1", str(out)])
                images.append(str(out))
        job.results["images"] = images

    def stage_clips(self, job: Job, script: Script, d: Path) -> None:
        clips: dict[str, str] = {}
        wf = self.cfg.get("comfyui.clip_workflow")
        if self.comfy and wf and self.cfg.get("comfyui.clips_enabled", False):
            limit = int(self.cfg.get("comfyui.max_clips", 2))
            for i, img in enumerate(job.results.get("images", [])[:limit]):
                name = self.comfy.upload_image(Path(img))
                files = self.comfy.run_workflow(Path(wf), {"IMAGE": name, "PROMPT": script.scenes[i],
                                                           "SEED": job.seed + i, "PREFIX": f"{job.id}_c{i}"},
                                                d, f"clip{i:02d}", float(self.cfg.get("comfyui.timeout_sec", 1800)))
                videos = [f for f in files if f.suffix.lower() in asm.VIDEO_EXT]
                if videos:
                    clips[str(i)] = str(videos[0])
        job.results["clips"] = clips

    def stage_lipsync(self, job: Job, script: Script, d: Path) -> None:
        job.results["talk_clip"] = ""
        cmd, face = self.cfg.get("lipsync.command"), self.cfg.get("character.face_image")
        if not (script.talk and self.cfg.get("lipsync.enabled", False) and cmd and face):
            return
        secs = float(self.cfg.get("lipsync.talk_seconds", 12))
        audio = cut_audio(Path(job.results["voice"]), secs, d / "talk_audio.wav")
        out = lipsync(cmd, Path(face), audio, d / "talk.mp4", int(self.cfg.get("lipsync.timeout_sec", 3600)))
        job.results["talk_clip"] = str(out)

    def stage_assemble(self, job: Job, script: Script, d: Path) -> None:
        clips = job.results.get("clips", {})
        sources = [Path(clips.get(str(i), img)) for i, img in enumerate(job.results["images"])]
        out = self.cfg.path("03_renders") / f"{job.id}.mp4"
        v = self.cfg.get("video", {}) or {}
        music = v.get("music")
        talk = job.results.get("talk_clip")
        events = self.word_captions(job, d)
        asm.assemble(d, Path(job.results["voice"]), sources, out, caption_text=script.narration,
                     caption_events=events,
                     talk_clip=Path(talk) if talk else None, talk_sec=float(self.cfg.get("lipsync.talk_seconds", 12)),
                     music=Path(music) if music else None, music_volume=float(v.get("music_volume", 0.12)),
                     width=int(v.get("width", 1080)), height=int(v.get("height", 1920)), fps=int(v.get("fps", 30)),
                     font=v.get("font", "Nirmala UI"), font_size=int(v.get("font_size", 80)),
                     max_seconds=float(v.get("max_seconds", 90)))
        job.results["render"] = str(out)

    def word_captions(self, job: Job, d: Path):
        """captions.mode: words → faster-whisper word timing + pop style; falls back to line captions."""
        c = self.cfg.get("captions", {}) or {}
        if c.get("mode", "lines") != "words":
            return None
        cache = d / "words.json"
        try:
            if cache.exists():
                words = [tuple(w) for w in json.loads(cache.read_text(encoding="utf-8"))]
            else:
                words = captions.transcribe_words(Path(job.results["voice"]), c.get("model", "large-v3"),
                                                  c.get("device", "cuda"), c.get("compute_type", "float16"),
                                                  c.get("language", "hi"))
                cache.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
            return captions.pop_events(words, c.get("highlight", "&H00E5FF"), int(c.get("max_words", 3)),
                                       int(c.get("max_chars", 18))) or None
        except Exception as exc:                     # missing package / model → plain captions
            job.results.setdefault("warnings", []).append(f"word captions नहीं बने ({str(exc)[:60]}), line captions लगे")
            return None

    def stage_label(self, job: Job, script: Script, d: Path) -> None:
        render = Path(job.results["render"])
        job.results["cover"] = str(asm.make_cover(render, self.cfg.path("03_renders") / f"{job.id}_cover.jpg"))
        note = self.cfg.get("provenance.note", "AI-generated content (synthetic presenter). Made with AI tools.")
        provenance.tag_metadata(render, script.title, note)
        tool = self.cfg.get("provenance.c2patool")
        if tool:
            provenance.sign_c2pa(render, tool, self.cfg.get("provenance.generator", "BEAST pipeline"),
                                 self.cfg.get("provenance.source_type", "composite"))
            job.results["c2pa"] = True

    def stage_qc(self, job: Job, script: Script, d: Path) -> None:
        v = self.cfg.get("video", {}) or {}
        report = qc.run_qc(Path(job.results["render"]), self.cfg.get("qc", {}) or {}, int(v.get("width", 1080)),
                           int(v.get("height", 1920)), float(v.get("max_seconds", 90)))
        job.results["qc"] = {"status": report.status, "checks": report.checks}
        if report.status == qc.FAIL:
            job.status = FAILED
            job.error = "QC fail"
            self.notify(f"❌ {job.id} QC fail\n{report.summary()}", buttons=[
                [("🔁 Images फिर से", f"redo_img:{job.id}"), ("🎙️ Voice से", f"redo_voice:{job.id}")]])

    def review_notes(self, job: Job) -> str:
        notes = list(job.results.get("warnings", []))
        q = job.results.get("qc")
        if q:
            notes += [f"QC {n}: {d}" for n, lvl, d in q["checks"] if lvl != "pass"]
        claims = (job.results.get("review") or {}).get("claims_to_verify", [])
        notes += [f"Verify: {c}" for c in claims[:3]]
        return ("\n⚠️ " + "\n⚠️ ".join(notes)) if notes else "\n✅ Safety + QC ठीक"

    def stage_preview(self, job: Job, script: Script, d: Path) -> None:
        prev = asm.make_preview(Path(job.results["render"]), self.cfg.path("04_previews") / f"{job.id}.mp4")
        job.results["preview"] = str(prev)
        job.status = REVIEW
        self.notify(f"👀 Review: {script.title}{self.review_notes(job)}\n\n{self.caption(script)}", video=prev, buttons=[
            [("✅ Approve", f"approve:{job.id}")],
            [("🔁 नई images", f"redo_img:{job.id}"), ("🎙️ नई voice", f"redo_voice:{job.id}")],
            [("❌ Cancel", f"cancel:{job.id}")]])

    # ---------- publish side ----------
    def base_caption(self, script: Script) -> str:
        disclosure = self.cfg.get("publish.disclosure_line", "")
        return "\n\n".join(p for p in (script.caption or script.title, disclosure) if p)

    def caption(self, script: Script) -> str:
        return "\n\n".join(p for p in (self.base_caption(script), " ".join(script.tags)) if p)

    def platform_cfg(self, key: str) -> dict:
        c = dict(self.cfg.get(f"publish.{key}", {}) or {})
        stored = self.store.kv_get("ig_token") if key == "instagram" else ""
        if stored:
            c["access_token"] = stored
        return c

    def enabled_platforms(self) -> list[str]:
        return [p for p in PLATFORMS if self.cfg.get(f"publish.{p}.enabled", False)]

    def publish_due(self) -> bool:
        did = False
        for job in self.store.by_status(SCHEDULED, PUBLISHING):
            if job.scheduled_at and job.scheduled_at > self.now():
                continue
            did = True
            job.status = PUBLISHING
            self.store.save(job)
            script, video = Script.from_dict(job.script), Path(job.results["render"])
            done = job.results.setdefault("published", {})
            dry = bool(self.cfg.get("publish.dry_run", True))
            errors, skipped = [], []
            for p in [p for p in self.enabled_platforms() if p not in done]:
                ctx = PublishContext(platform=p, job_id=job.id, video=video, title=script.title,
                                     caption=self.base_caption(script), tags=script.tags,
                                     cfg=self.platform_cfg(p), root=self.cfg.root)
                try:
                    too_long = check_duration(ctx)
                    if too_long:
                        done[p] = {"platform": p, "skipped": too_long}
                        skipped.append(f"{PLATFORMS[p].label}: {too_long}")
                    elif dry:
                        done[p] = {"platform": p, "dry_run": True}
                    else:
                        done[p] = resolve(p, ctx.cfg)(ctx)
                except Exception as exc:
                    errors.append(f"{p}: {exc}")
            if skipped:
                self.notify("⏭️ Skip: " + "; ".join(skipped))
            if errors:
                job.attempts += 1
                job.error = "; ".join(errors)
                if job.attempts >= MAX_ATTEMPTS:
                    job.status = FAILED
                    self.notify(f"⚠️ Publish fail {job.id}: {job.error[:400]}")
                else:
                    job.status, job.scheduled_at = SCHEDULED, self.now() + 600   # retry in 10 min
            else:
                job.status = PUBLISHED
                record = self.cfg.path("05_published") / f"{job.id}.json"
                record.write_text(json.dumps({"id": job.id, "script": job.script, "published": done},
                                             ensure_ascii=False, indent=2), encoding="utf-8")
                self.notify(f"🚀 Published {job.id}\n" + "\n".join(self.describe(k, v) for k, v in done.items()))
            self.store.save(job)
        return did

    @staticmethod
    def describe(platform: str, res: dict) -> str:
        label = PLATFORMS[platform].label
        if res.get("skipped"):
            return f"• {label}: skipped"
        if res.get("dry_run"):
            return f"• {label}: dry-run"
        if res.get("manual"):
            return f"• {label}: 📲 phone से post करें ({Path(res['path']).name})"
        return f"• {label}: {res.get('url') or res.get('id')}"

    # ---------- reports ----------
    def attach_youtube(self, args: list[str]) -> None:
        if len(args) < 2 or not (job := self.store.get(args[0])):
            self.notify("Use: /yt <job_id> <youtube link>")
            return
        vid = stats.youtube_id(args[1])
        if not vid:
            self.notify("YouTube link पहचान नहीं आया")
            return
        job.results.setdefault("published", {}).setdefault("youtube", {}).update(
            {"id": vid, "url": f"https://youtube.com/shorts/{vid}"})
        self.store.save(job)
        self.notify(f"🔗 {job.id} ↔ YouTube {vid}")

    def report_text(self, days: int = 7) -> str:
        since = self.now() - days * 86400
        recent = [j for j in self.store.by_status(PUBLISHED) if j.created_at >= since]
        yt_key = self.cfg.get("reports.youtube_api_key", "")
        yt_ids = {j.id: j.results.get("published", {}).get("youtube", {}).get("id") for j in recent}
        yt = stats.youtube_views(yt_key, [v for v in yt_ids.values() if v]) if yt_key else {}
        ig_cfg = self.platform_cfg("instagram")
        lines = [f"📊 पिछले {days} दिन: {len(recent)} published"]
        for j in recent:
            parts = []
            if yt_ids.get(j.id) in yt:
                parts.append(f"YT {yt[yt_ids[j.id]]:,}")
            ig_id = j.results.get("published", {}).get("instagram", {}).get("id")
            if ig_id and ig_cfg.get("access_token"):
                views = stats.instagram_views(ig_cfg, ig_id)
                if views is not None:
                    parts.append(f"IG {views:,}")
            lines.append(f"• {j.script.get('title', '')[:35]} — {' · '.join(parts) or 'views: link/API नहीं'}")
        queue = {st: len(self.store.by_status(st)) for st in (RUNNING, REVIEW, SCHEDULED, FAILED)}
        lines.append("Queue: " + " · ".join(f"{k} {v}" for k, v in queue.items()))
        lines.append(f"💾 Free disk: {free_gb(self.cfg.root):.0f} GB · 💡 Ideas: {len(self.store.ideas())}")
        return "\n".join(lines)

    def maintenance(self) -> None:
        self.daily_tasks()
        self.refresh_token()

    def daily_tasks(self) -> None:
        """Once a day after reports.time: report to phone + cleanup of old working folders."""
        from datetime import datetime
        from zoneinfo import ZoneInfo
        now = datetime.fromtimestamp(self.now(), ZoneInfo(self.tz))
        hh, mm = (int(x) for x in str(self.cfg.get("reports.time", "09:00")).split(":"))
        today = now.strftime("%Y-%m-%d")
        if (now.hour, now.minute) < (hh, mm) or self.store.kv_get("daily_done") == today:
            return
        self.store.kv_set("daily_done", today)
        finished = {j.id for j in self.store.by_status(PUBLISHED, CANCELLED)}
        removed = cleanup_job_dirs(self.cfg.path("02_jobs"), finished,
                                   float(self.cfg.get("housekeeping.keep_job_days", 14)), self.now())
        if self.cfg.get("reports.enabled", True):
            extra = f"\n🧹 {len(removed)} पुराने job folders साफ़" if removed else ""
            self.notify(self.report_text() + extra)
        if self.cfg.get("trends.enabled", False):
            self.send_trends()
        self.do_backup()

    # ---------- trend radar ----------
    def send_trends(self) -> None:
        key = self.cfg.get("reports.youtube_api_key", "")
        if not key:
            self.notify("Trend radar के लिए reports.youtube_api_key (YOUTUBE_API_KEY) चाहिए")
            return
        try:
            items = trends.digest(key, self.cfg.get("trends.keywords", []) or [], self.cfg.get("trends.region", "IN"),
                                  int(self.cfg.get("trends.top", 5)), now=self.now())
        except Exception as exc:
            self.notify(f"⚠️ Trend radar fail: {str(exc)[:200]}")
            return
        if not items:
            self.notify("आज कोई trend नहीं मिला")
            return
        self.store.kv_set("trend_candidates", json.dumps(items, ensure_ascii=False))
        lines = [f"{i + 1}. {it['title'][:70]} · {it['views']:,} views · [{it['keyword']}]" for i, it in enumerate(items)]
        self.notify("🔥 Trend radar (सिर्फ़ inspiration — copy नहीं, अपना angle):\n" + "\n".join(lines),
                    buttons=[[(f"💡 {i + 1}", f"trend:{i}") for i in range(len(items))]])

    def trend_to_idea(self, index: str) -> None:
        items = json.loads(self.store.kv_get("trend_candidates", "[]") or "[]")
        if not index.isdigit() or int(index) >= len(items):
            self.notify("Trend नहीं मिला, /trends फिर चलाएँ")
            return
        it = items[int(index)]
        n = self.store.add_idea(f"{it['title']} — अपना what-if angle सोचें (ref: {it['url']})")
        self.notify(f"💡 Idea #{n} saved")

    # ---------- backup ----------
    def do_backup(self, force: bool = False) -> None:
        dest = self.cfg.get("backup.dest", "")
        if not dest:
            if force:
                self.notify("backup.dest config में set नहीं है")
            return
        last = float(self.store.kv_get("backup_done", "0") or 0)
        if not force and self.now() - last < float(self.cfg.get("backup.every_days", 7)) * 86400:
            return
        try:
            counts = run_backup(self.cfg.root, Path(dest), self.cfg.path("06_logs") / "jobs.sqlite")
            self.store.kv_set("backup_done", str(self.now()))
            self.notify(f"🗄️ Backup हो गया → {dest} ({sum(counts.values())} files)")
        except Exception as exc:
            self.notify(f"⚠️ Backup fail: {str(exc)[:200]}")

    def refresh_token(self) -> None:
        """Refresh the Instagram long-lived token every ~50 days (Instagram Login only)."""
        ig = self.platform_cfg("instagram")
        if not (self.cfg.get("publish.instagram.enabled") and self.cfg.get("publish.instagram.auto_refresh_token")
                and ig.get("access_token")):
            return
        last = float(self.store.kv_get("ig_token_refreshed", "0") or 0)
        if self.now() - last < 50 * 86400:
            return
        try:
            self.store.kv_set("ig_token", refresh_instagram_token(ig))
            self.store.kv_set("ig_token_refreshed", str(self.now()))
            self.notify("🔑 Instagram token refresh हो गया")
        except Exception as exc:
            self.notify(f"⚠️ Instagram token refresh fail: {exc}")
            self.store.kv_set("ig_token_refreshed", str(self.now() - 49 * 86400))  # retry tomorrow
