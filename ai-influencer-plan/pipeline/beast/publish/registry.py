"""Platform registry: one entry per social platform.

To add a platform:
  1. add a spec to PLATFORMS (limits + api status),
  2. write a function  publish_<name>(ctx: PublishContext) -> dict  (or rely on "manual"),
  3. add  publish.<name>:  enabled: true  (+ its settings) to config.yaml.
Platforms without a usable API use the generic manual hand-off: the final video and a
ready-to-paste caption land in 05_published/manual/<platform>/ and the phone gets a checklist.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from ..media import duration


@dataclass(frozen=True)
class Spec:
    label: str
    max_seconds: float
    max_caption: int
    max_hashtags: int
    api: str            # ready | needs_public_url | paid | business_only | manual | blocked_india
    notes: str = ""


# Limits are from official docs where available; see PLATFORMS.md for sources and status labels.
PLATFORMS: dict[str, Spec] = {
    "youtube":   Spec("YouTube Shorts", 180, 5000, 3, "ready", "API uploads private-locked until audit; manual mode default"),
    "instagram": Spec("Instagram Reels", 180, 2200, 5, "ready", "Instagram Login, own account in dev mode"),
    "facebook":  Spec("Facebook Reels", 90, 5000, 5, "ready", "video_reels API, 3–90 s, 30/day"),
    "threads":   Spec("Threads", 300, 500, 1, "needs_public_url", "Meta fetches video_url; 250 posts/day"),
    "pinterest": Spec("Pinterest Video Pin", 300, 500, 5, "ready", "trial apps post to own account only"),
    "telegram_channel": Spec("Telegram Channel", 600, 1000, 5, "ready", "bot must be channel admin; bot upload limit 50 MB"),
    "x":         Spec("X (Twitter)", 140, 280, 2, "paid", "pay-per-use API since Feb 2026; manual by default"),
    "bluesky":   Spec("Bluesky", 600, 300, 3, "manual", "video API exists; plugin not written yet"),
    "snapchat":  Spec("Snapchat Spotlight", 60, 160, 3, "business_only", "Public Profile API needs Business account"),
    "linkedin":  Spec("LinkedIn", 600, 3000, 3, "manual", "low fit for 16–30 entertainment"),
    "moj":       Spec("Moj", 60, 500, 5, "manual", "no public upload API found"),
    "sharechat": Spec("ShareChat", 60, 500, 5, "manual", "no public upload API found"),
    "josh":      Spec("Josh", 60, 500, 5, "manual", "no public upload API found"),
    "whatsapp_channel": Spec("WhatsApp Channel", 90, 1000, 0, "manual", "no posting API found for Channels"),
    "tiktok":    Spec("TikTok", 600, 2200, 5, "blocked_india", "banned in India since June 2020"),
}


@dataclass
class PublishContext:
    platform: str
    job_id: str
    video: Path
    title: str
    caption: str          # base caption (no hashtags, includes disclosure line)
    tags: list[str]
    cfg: dict             # publish.<platform> section
    root: Path            # pipeline root folder
    extras: dict = field(default_factory=dict)

    @property
    def spec(self) -> Spec:
        return PLATFORMS[self.platform]

    def formatted_caption(self) -> str:
        tags = self.tags[: self.spec.max_hashtags]
        text = self.caption + (("\n\n" + " ".join(tags)) if tags else "")
        if len(text) <= self.spec.max_caption:
            return text
        tag_part = (" " + " ".join(tags)) if tags else ""
        room = max(self.spec.max_caption - len(tag_part) - 1, 0)
        return (self.caption[:room].rstrip() + "…" + tag_part)[: self.spec.max_caption]


def manual_handoff(ctx: PublishContext) -> dict:
    dest = ctx.root / "05_published" / "manual" / ctx.platform
    dest.mkdir(parents=True, exist_ok=True)
    video = dest / f"{ctx.job_id}.mp4"
    shutil.copy2(ctx.video, video)
    (dest / f"{ctx.job_id}.txt").write_text(
        f"PLATFORM: {ctx.spec.label}\nTITLE: {ctx.title}\n\nCAPTION:\n{ctx.formatted_caption()}\n\n"
        "Checklist: AI/altered-content label ON · कोई दूसरा watermark नहीं · paid partnership हो तो disclose करें\n",
        encoding="utf-8")
    return {"platform": ctx.platform, "manual": True, "path": str(video), "url": ""}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", text.lower())


def resolve(platform: str, cfg: dict) -> Callable[[PublishContext], dict]:
    """Return the API plugin for a platform, or the manual hand-off when the platform has no
    plugin or its config says  mode: manual."""
    from . import plugins
    if PLATFORMS[platform].api == "blocked_india":
        raise ValueError(f"{PLATFORMS[platform].label} is blocked in India")
    plugin = getattr(plugins, f"publish_{_slug(platform)}", None)
    # YouTube handles its own manual mode (sync folder + upload checklist)
    if plugin is None or (cfg.get("mode") == "manual" and platform != "youtube"):
        return manual_handoff
    return plugin


def check_duration(ctx: PublishContext) -> str:
    secs = duration(ctx.video)
    if secs > ctx.spec.max_seconds:
        return f"video {secs:.0f}s > {ctx.spec.label} limit {ctx.spec.max_seconds:.0f}s"
    return ""
