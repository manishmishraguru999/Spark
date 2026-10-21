"""Devanagari captions as an ASS subtitle file (burned in by ffmpeg/libass).

Timing is proportional to text length across the voice duration, which is good enough
for short narrated Reels. Windows ships "Nirmala UI", which renders Devanagari.
"""
from __future__ import annotations

import re
from pathlib import Path


def split_caption_lines(text: str, max_chars: int = 26) -> list[str]:
    words = re.sub(r"\s+", " ", text).strip().split(" ")
    lines, cur = [], ""
    for w in words:
        if cur and (len(cur) + 1 + len(w) > max_chars or re.search(r"[।?!.,]$", cur)):
            lines.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def _ts(sec: float) -> str:
    cs = int(round(sec * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def timed_lines(text: str, total_sec: float, start: float = 0.0, max_chars: int = 26) -> list[tuple[float, float, str]]:
    lines = split_caption_lines(text, max_chars)
    weights = [max(len(l), 4) for l in lines]
    total_w = sum(weights) or 1
    out, t = [], start
    for line, w in zip(lines, weights):
        dur = (total_sec - start) * w / total_w
        out.append((t, t + dur, line))
        t += dur
    return out


def write_ass(lines: list[tuple[float, float, str]], out: Path, width: int = 1080, height: int = 1920,
              font: str = "Nirmala UI", size: int = 64, margin_v: int = 420) -> Path:
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,5,2,2,60,60,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = "".join(f"Dialogue: 0,{_ts(a)},{_ts(b)},Cap,,0,0,0,,{t.replace(chr(10), ' ')}\n"
                     for a, b, t in lines)
    out.write_text(header + events, encoding="utf-8")
    return out
