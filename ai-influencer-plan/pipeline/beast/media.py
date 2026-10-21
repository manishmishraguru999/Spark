"""Thin ffmpeg/ffprobe helpers."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


class MediaError(RuntimeError):
    pass


def ffmpeg_bin(name: str = "ffmpeg") -> str:
    found = shutil.which(name)
    if not found:
        raise MediaError(f"{name} नहीं मिला। FFmpeg install करके PATH में जोड़ें।")
    return found


def run(cmd: list[str], cwd: Path | None = None) -> None:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise MediaError(f"Command failed ({proc.returncode}): {' '.join(cmd[:6])}...\n{proc.stderr[-1500:]}")


def probe(path: Path) -> dict:
    proc = subprocess.run([ffmpeg_bin("ffprobe"), "-v", "error", "-print_format", "json",
                           "-show_format", "-show_streams", str(path)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise MediaError(f"ffprobe failed for {path}: {proc.stderr[-500:]}")
    return json.loads(proc.stdout)


def duration(path: Path) -> float:
    return float(probe(path)["format"]["duration"])


def video_size(path: Path) -> tuple[int, int]:
    for s in probe(path)["streams"]:
        if s.get("codec_type") == "video":
            return int(s["width"]), int(s["height"])
    raise MediaError(f"No video stream in {path}")
