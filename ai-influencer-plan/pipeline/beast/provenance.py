"""AI provenance labels inside the video file.

Always: MP4 metadata tags (title, comment, description) that say the content is AI-generated.
Optional: C2PA Content Credentials via the open-source `c2patool` with an IPTC digitalSourceType.
YouTube reports it keeps a permanent AI label when C2PA marks a file as AI-generated; many
upload paths strip metadata, so the in-app disclosure toggles stay mandatory.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .media import ffmpeg_bin, run

IPTC = "http://cv.iptc.org/newscodes/digitalsourcetype/"
SOURCE_TYPES = {"full": IPTC + "trainedAlgorithmicMedia",
                "composite": IPTC + "compositeWithTrainedAlgorithmicMedia"}


def tag_metadata(video: Path, title: str, note: str) -> Path:
    tmp = video.with_name(video.stem + "_tagged.mp4")
    run([ffmpeg_bin(), "-y", "-i", str(video), "-map", "0", "-c", "copy", "-movflags", "+faststart",
         "-metadata", f"title={title}", "-metadata", f"comment={note}", "-metadata", f"description={note}",
         str(tmp)])
    tmp.replace(video)
    return video


def c2pa_manifest(generator: str, source: str = "composite") -> dict:
    return {
        "claim_generator": generator,
        "assertions": [{"label": "c2pa.actions.v2", "data": {"actions": [
            {"action": "c2pa.created", "digitalSourceType": SOURCE_TYPES[source]}]}}],
    }


def sign_c2pa(video: Path, c2patool: str, generator: str, source: str = "composite",
              extra_args: list[str] | None = None) -> Path:
    manifest = video.with_suffix(".c2pa.json")
    manifest.write_text(json.dumps(c2pa_manifest(generator, source), indent=2), encoding="utf-8")
    signed = video.with_name(video.stem + "_c2pa.mp4")
    proc = subprocess.run([c2patool, str(video), "-m", str(manifest), "-o", str(signed), "-f", *(extra_args or [])],
                          capture_output=True, text=True)
    if proc.returncode != 0 or not signed.exists():
        raise RuntimeError(f"c2patool failed: {(proc.stderr or proc.stdout)[-400:]}")
    signed.replace(video)
    return video
