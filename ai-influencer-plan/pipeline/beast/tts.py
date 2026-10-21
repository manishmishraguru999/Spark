"""Voice generation.

provider "sarvam": Sarvam Bulbul API (cloud, pay per character).
provider "command": any local TTS you run yourself (e.g. Indic Parler-TTS). The command
template gets {text_file} and {out}; it must write a WAV/MP3 to {out}.
"""
from __future__ import annotations

import base64
import subprocess
from pathlib import Path

import requests

from .config import Config
from .media import ffmpeg_bin, run


class TTSError(RuntimeError):
    pass


def _chunks(text: str, limit: int) -> list[str]:
    """Split on sentence ends so each request stays under the API character limit."""
    parts, cur = [], ""
    for sentence in text.replace("।", "।\n").replace("?", "?\n").replace("!", "!\n").splitlines():
        sentence = sentence.strip()
        if not sentence:
            continue
        while len(sentence) > limit:            # very long sentence: hard split
            parts.append(sentence[:limit]); sentence = sentence[limit:]
        if len(cur) + len(sentence) + 1 > limit:
            parts.append(cur); cur = sentence
        else:
            cur = f"{cur} {sentence}".strip()
    if cur:
        parts.append(cur)
    return parts


def sarvam_tts(cfg: Config, text: str, out: Path, session: requests.Session | None = None) -> Path:
    s = cfg.get("tts.sarvam", {})
    if not s.get("api_key"):
        raise TTSError("SARVAM_API_KEY set नहीं है")
    http = session or requests.Session()
    pieces: list[Path] = []
    for i, chunk in enumerate(_chunks(text, int(s.get("max_chars", 2400)))):
        body = {"text": chunk, s.get("language_field", "target_language_code"): s.get("language", "hi-IN"),
                "model": s.get("model", "bulbul:v3")}
        for key in ("speaker", "pace", "speech_sample_rate"):
            if s.get(key) is not None:
                body[key] = s[key]
        r = http.post(s.get("url", "https://api.sarvam.ai/text-to-speech"), json=body,
                      headers={"api-subscription-key": s["api_key"]}, timeout=120)
        if r.status_code != 200:
            raise TTSError(f"Sarvam error {r.status_code}: {r.text[:300]}")
        audios = r.json().get("audios") or []
        if not audios:
            raise TTSError("Sarvam response में audio नहीं मिला")
        piece = out.with_name(f"{out.stem}_part{i}.wav")
        piece.write_bytes(base64.b64decode(audios[0]))
        pieces.append(piece)
    concat_audio(pieces, out)
    return out


def concat_audio(pieces: list[Path], out: Path) -> None:
    if len(pieces) == 1:
        run([ffmpeg_bin(), "-y", "-i", str(pieces[0]), "-ar", "48000", "-ac", "1", str(out)])
        return
    listing = out.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.name}'\n" for p in pieces), encoding="utf-8")
    run([ffmpeg_bin(), "-y", "-f", "concat", "-safe", "0", "-i", listing.name, "-ar", "48000", "-ac", "1",
         out.name], cwd=out.parent)


def command_tts(cfg: Config, text: str, out: Path) -> Path:
    template = cfg.get("tts.command")
    if not template:
        raise TTSError("tts.command config में नहीं है")
    text_file = out.with_suffix(".txt")
    text_file.write_text(text, encoding="utf-8")
    cmd = template.format(text_file=str(text_file), out=str(out))
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if proc.returncode != 0 or not out.exists():
        raise TTSError(f"Local TTS failed: {proc.stderr[-500:]}")
    return out


def synthesize(cfg: Config, text: str, out: Path) -> Path:
    provider = cfg.get("tts.provider", "sarvam")
    if provider == "sarvam":
        return sarvam_tts(cfg, text, out)
    if provider == "command":
        return command_tts(cfg, text, out)
    raise TTSError(f"Unknown tts.provider: {provider}")
