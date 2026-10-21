"""Automatic quality check of the final render (runs before the preview reaches the phone).

Checks: resolution, fps, duration, audio present, black frames, silence, loudness.
Thresholds are starting points (see PLATFORMS.md / research notes) and can be changed in config `qc:`.
"""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .media import ffmpeg_bin, probe

PASS, WARN, FAIL = "pass", "warn", "fail"


@dataclass
class QCReport:
    checks: list[tuple[str, str, str]] = field(default_factory=list)   # (name, level, detail)

    def add(self, name: str, level: str, detail: str) -> None:
        self.checks.append((name, level, detail))

    @property
    def status(self) -> str:
        levels = {lvl for _, lvl, _ in self.checks}
        return FAIL if FAIL in levels else WARN if WARN in levels else PASS

    def summary(self) -> str:
        icon = {PASS: "✅", WARN: "⚠️", FAIL: "❌"}
        return "\n".join(f"{icon[l]} {n}: {d}" for n, l, d in self.checks if l != PASS) or "✅ QC: सब ठीक"


def _stderr(args: list[str]) -> str:
    proc = subprocess.run([ffmpeg_bin(), "-hide_banner", "-nostats", *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:          # fail closed: a broken analysis must not read as "0 problems"
        raise RuntimeError(f"QC analysis failed: {proc.stderr[-400:]}")
    return proc.stderr


def black_seconds(video: Path) -> float:
    err = _stderr(["-i", str(video), "-vf", "blackdetect=d=0.5:pix_th=0.10", "-an", "-f", "null", "-"])
    return sum(float(x) for x in re.findall(r"black_duration:(\d+\.?\d*)", err))


def silence_seconds(video: Path, noise_db: int = -35) -> float:
    err = _stderr(["-i", str(video), "-af", f"silencedetect=n={noise_db}dB:d=1", "-vn", "-f", "null", "-"])
    return sum(float(x) for x in re.findall(r"silence_duration: (\d+\.?\d*)", err))


def integrated_lufs(video: Path) -> float:
    err = _stderr(["-i", str(video), "-af", "ebur128", "-vn", "-f", "null", "-"])
    found = re.findall(r"I:\s+(-?\d+\.?\d*) LUFS", err)
    if not found:
        raise RuntimeError("loudness not found")
    return float(found[-1])


def run_qc(video: Path, q: dict, width: int, height: int, max_seconds: float) -> QCReport:
    rep = QCReport()
    info = probe(video)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    dur = float(info["format"]["duration"])
    if not v:
        rep.add("video", FAIL, "video stream नहीं है")
        return rep
    size_ok = (int(v["width"]), int(v["height"])) == (width, height)
    rep.add("resolution", PASS if size_ok else FAIL, f"{v['width']}x{v['height']}")
    rep.add("duration", PASS if dur <= max_seconds + 0.5 else FAIL, f"{dur:.1f}s (max {max_seconds:.0f}s)")
    rep.add("audio", PASS if a else FAIL, "audio stream" if a else "audio नहीं है")
    black = black_seconds(video) / max(dur, 0.1)
    rep.add("black frames", FAIL if black > q.get("max_black_ratio", 0.2) else PASS, f"{black:.0%}")
    if a:
        silent = silence_seconds(video) / max(dur, 0.1)
        rep.add("silence", WARN if silent > q.get("max_silence_ratio", 0.15) else PASS, f"{silent:.0%}")
        lufs = integrated_lufs(video)
        lo, hi = q.get("lufs_range", [-17.0, -11.0])
        rep.add("loudness", PASS if lo <= lufs <= hi else WARN, f"{lufs:.1f} LUFS (target {lo}..{hi})")
    return rep
