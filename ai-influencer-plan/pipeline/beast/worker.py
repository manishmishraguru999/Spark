"""The pipeline brain: turns phone messages into jobs, runs one stage at a time,
sends previews for approval, and publishes approved videos at their slot."""
from __future__ import annotations

import json
import logging
import time
import traceback
from pathlib import Path

from . import assemble as asm
from .comfy import ComfyClient
from .config import Config
from .jobs import (CANCELLED, FAILED, PUBLISHED, PUBLISHING, REVIEW, RUNNING, SCHEDULED, STAGES, Job,
                   JobStore)
from .lipsync import cut_audio, lipsync
from .media import ffmpeg_bin, run
from .publish.meta import publish_facebook, publish_instagram, refresh_instagram_token
from .publish.youtube import publish_youtube
from .schedule import fmt, next_slot
from .script_parser import Script, ScriptError, parse_script
from .tts import synthesize

log = logging.getLogger("beast")
MAX_ATTEMPTS = 3

HELP = """BEAST pipeline commands
/new + script  → नया Reel (format: TITLE/HOOK/VO/SCENE/TALK/CAPTION/TAGS)
/status        → चल रहे और pending jobs
/cancel <id>   → job रद्द
/help          → यह message"""


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
        else:
            self.notify(HELP)

    def handle_action(self, action: str, job_id: str) -> None:
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
        asm.assemble(d, Path(job.results["voice"]), sources, out, caption_text=script.narration,
                     talk_clip=Path(talk) if talk else None, talk_sec=float(self.cfg.get("lipsync.talk_seconds", 12)),
                     music=Path(music) if music else None, music_volume=float(v.get("music_volume", 0.12)),
                     width=int(v.get("width", 1080)), height=int(v.get("height", 1920)), fps=int(v.get("fps", 30)),
                     font=v.get("font", "Nirmala UI"), font_size=int(v.get("font_size", 80)),
                     max_seconds=float(v.get("max_seconds", 90)))
        job.results["render"] = str(out)

    def stage_preview(self, job: Job, script: Script, d: Path) -> None:
        prev = asm.make_preview(Path(job.results["render"]), self.cfg.path("04_previews") / f"{job.id}.mp4")
        job.results["preview"] = str(prev)
        job.status = REVIEW
        self.notify(f"👀 Review: {script.title}\n\n{self.caption(script)}", video=prev, buttons=[
            [("✅ Approve", f"approve:{job.id}")],
            [("🔁 नई images", f"redo_img:{job.id}"), ("🎙️ नई voice", f"redo_voice:{job.id}")],
            [("❌ Cancel", f"cancel:{job.id}")]])

    # ---------- publish side ----------
    def caption(self, script: Script) -> str:
        parts = [script.caption or script.title]
        disclosure = self.cfg.get("publish.disclosure_line", "")
        if disclosure:
            parts.append(disclosure)
        if script.tags:
            parts.append(" ".join(script.tags))
        return "\n\n".join(parts)

    def meta_cfg(self, key: str) -> dict:
        c = dict(self.cfg.get(f"publish.{key}", {}) or {})
        stored = self.store.kv_get("ig_token") if key == "instagram" else ""
        if stored:
            c["access_token"] = stored
        return c

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
            caption, dry = self.caption(script), bool(self.cfg.get("publish.dry_run", True))
            targets = [p for p in ("youtube", "instagram", "facebook")
                       if self.cfg.get(f"publish.{p}.enabled", False) and p not in done]
            errors = []
            for p in targets:
                try:
                    if dry:
                        done[p] = {"platform": p, "dry_run": True}
                    elif p == "youtube":
                        done[p] = publish_youtube(self.cfg.get("publish.youtube"), video, script.title, caption,
                                                  script.tags, job.id)
                    elif p == "instagram":
                        done[p] = publish_instagram(self.meta_cfg("instagram"), video, caption)
                    else:
                        done[p] = publish_facebook(self.meta_cfg("facebook"), video, caption, script.title)
                except Exception as exc:
                    errors.append(f"{p}: {exc}")
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
                links = "\n".join(f"• {k}: {v.get('url') or v.get('path') or ('dry-run' if v.get('dry_run') else v.get('id'))}"
                                  for k, v in done.items())
                manual = " (YouTube: phone से upload करें)" if done.get("youtube", {}).get("manual") else ""
                self.notify(f"🚀 Published {job.id}{manual}\n{links}")
            self.store.save(job)
        return did

    def maintenance(self) -> None:
        """Refresh the Instagram long-lived token every ~50 days (Instagram Login only)."""
        ig = self.meta_cfg("instagram")
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
