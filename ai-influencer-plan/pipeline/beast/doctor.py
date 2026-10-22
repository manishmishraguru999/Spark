"""`python run_pipeline.py --doctor` — checks the whole setup and says in Hindi what to fix.
Also used by the Telegram /health command."""
from __future__ import annotations

import os
import subprocess
import sys
from zoneinfo import ZoneInfo

import requests

from .config import Config
from .housekeeping import free_gb
from .publish.registry import PLATFORMS

REQUIRED_FILTERS = ("subtitles", "zoompan", "loudnorm", "ebur128", "blackdetect", "silencedetect")
CREDENTIALS = {
    "instagram": ("ig_user_id", "access_token"), "facebook": ("page_id", "page_access_token"),
    "telegram_channel": ("bot_token", "channel_id"), "threads": ("user_id", "access_token"),
    "pinterest": ("access_token", "board_id"),
}


def run_checks(cfg: Config, network: bool = True, session: requests.Session | None = None) -> list[tuple[bool, str, str]]:
    """Returns (ok, check, fix-hint) tuples."""
    http = session or requests.Session()
    out: list[tuple[bool, str, str]] = []

    def add(ok: bool, name: str, fix: str = "") -> None:
        out.append((ok, name, "" if ok else fix))

    add(sys.version_info >= (3, 11), f"Python {sys.version.split()[0]}", "Python 3.11+ install करें")
    try:
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        missing = [f for f in REQUIRED_FILTERS if f" {f} " not in filters]
        add(not missing, "FFmpeg filters", f"FFmpeg का full build चाहिए (missing: {', '.join(missing)}) — winget install Gyan.FFmpeg")
    except FileNotFoundError:
        add(False, "FFmpeg", "winget install Gyan.FFmpeg, फिर नया terminal खोलें")
    try:
        ZoneInfo(cfg.get("schedule.timezone", "Asia/Kolkata"))
        add(True, "Timezone")
    except Exception:
        add(False, "Timezone", "pip install tzdata")
    probe = cfg.root / "06_logs" / ".write_test"
    try:
        probe.write_text("ok"); probe.unlink()
        add(True, f"Folder writable: {cfg.root}")
    except OSError:
        add(False, f"Folder writable: {cfg.root}", "paths.root का folder बनाएँ / permissions देखें")
    gb = free_gb(cfg.root)
    need = float(cfg.get("housekeeping.min_free_gb", 30))
    add(gb >= need, f"Free disk {gb:.0f} GB", f"कम से कम {need:.0f} GB खाली रखें (पुराने renders हटाएँ)")

    tts = cfg.get("tts.provider", "sarvam")
    if tts == "sarvam":
        add(bool(cfg.get("tts.sarvam.api_key")), "Sarvam API key", "setx SARVAM_API_KEY \"...\"")
    add(bool(cfg.get("telegram.bot_token")), "Telegram bot token", "setx TELEGRAM_BOT_TOKEN \"...\" (@BotFather)")
    ids = [i for i in (cfg.get("telegram.allowed_chat_ids") or []) if int(i) != 123456789]   # example placeholder
    add(bool(ids), "Allowed chat IDs", "config में अपना असली chat ID भरें (README Step 6)")
    if cfg.get("character.face_image") and cfg.get("lipsync.enabled"):
        from pathlib import Path
        add(Path(cfg.get("character.face_image")).exists(), "Character face image", "character.face_image का path सही करें")

    for p in PLATFORMS:
        c = cfg.get(f"publish.{p}", {}) or {}
        if not c.get("enabled"):
            continue
        if PLATFORMS[p].api == "blocked_india":
            add(False, f"{PLATFORMS[p].label}", "India में blocked है — enabled: false करें")
            continue
        if c.get("mode") == "manual" or p not in CREDENTIALS:
            add(True, f"{PLATFORMS[p].label} (manual/own flow)")
            continue
        missing = [k for k in CREDENTIALS[p] if not c.get(k)]
        add(not missing, f"{PLATFORMS[p].label} credentials", f"publish.{p}: {', '.join(missing)} भरें")

    if network:
        if cfg.get("comfyui.enabled"):
            try:
                ok = http.get(f"{cfg.get('comfyui.url').rstrip('/')}/system_stats", timeout=5).status_code == 200
            except requests.RequestException:
                ok = False
            add(ok, "ComfyUI चालू है", "ComfyUI start करें (127.0.0.1:8188)")
        if cfg.get("safety.ollama.enabled"):
            try:
                ok = http.get(f"{cfg.get('safety.ollama.url', 'http://127.0.0.1:11434').rstrip('/')}/api/tags",
                              timeout=5).status_code == 200
            except requests.RequestException:
                ok = False
            add(ok, "Ollama चालू है", "Ollama app start करें, model pull करें")
        token = cfg.get("telegram.bot_token")
        if token:
            try:
                ok = http.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10).json().get("ok", False)
            except (requests.RequestException, ValueError):
                ok = False
            add(ok, "Telegram token valid", "BotFather से नया token लें")
    if cfg.get("captions.mode") == "words":
        try:
            import faster_whisper  # noqa: F401
            add(True, "faster-whisper (word captions)")
        except ImportError:
            add(False, "faster-whisper (word captions)", "venv\\Scripts\\pip install faster-whisper (या captions.mode: lines)")
    if cfg.get("backup.dest"):
        from pathlib import Path as _P
        add(_P(cfg.get("backup.dest")).anchor != cfg.root.anchor or not cfg.root.anchor,
            f"Backup दूसरी drive पर: {cfg.get('backup.dest')}", "Backup दूसरी drive पर रखें (एक drive खराब होने पर दोनों न जाएँ)")
    if cfg.get("provenance.c2patool"):
        add(os.path.exists(cfg.get("provenance.c2patool")), "c2patool", "provenance.c2patool का path सही करें")
    return out


def report(checks: list[tuple[bool, str, str]]) -> str:
    lines = [("✅ " if ok else "❌ ") + name + ("" if ok else f"\n   ➜ {fix}") for ok, name, fix in checks]
    bad = sum(1 for ok, *_ in checks if not ok)
    lines.append("\nसब ठीक है ✅" if not bad else f"\n{bad} चीज़ें ठीक करनी हैं")
    return "\n".join(lines)
