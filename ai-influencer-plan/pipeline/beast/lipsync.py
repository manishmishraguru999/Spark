"""Lip-sync via any local tool (MuseTalk, LatentSync 1.5, ...).

lipsync.command in config.yaml gets {face}, {audio}, {out}. Example for a wrapper script:
    X:\\tools\\musetalk\\venv\\Scripts\\python.exe X:\\tools\\run_musetalk.py --face "{face}" --audio "{audio}" --out "{out}"
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from .media import ffmpeg_bin, run


class LipSyncError(RuntimeError):
    pass


def cut_audio(voice: Path, seconds: float, out: Path) -> Path:
    run([ffmpeg_bin(), "-y", "-i", str(voice), "-t", f"{seconds:.3f}", "-ar", "16000", "-ac", "1", str(out)])
    return out


def lipsync(command_template: str, face: Path, audio: Path, out: Path, timeout_sec: int = 3600) -> Path:
    cmd = command_template.format(face=str(face), audio=str(audio), out=str(out))
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        raise LipSyncError(f"Lip-sync timeout ({timeout_sec}s)") from exc
    if proc.returncode != 0 or not out.exists():
        raise LipSyncError(f"Lip-sync failed: {(proc.stderr or proc.stdout)[-600:]}")
    return out
