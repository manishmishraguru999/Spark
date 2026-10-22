"""`python run_pipeline.py --benchmark` — the fair test from the research report (§6).

Same Hindi script, same face images, same duration for every option:
  • every voice option  → voice_<name>.wav  (time taken, ok/error)
  • every face × lip-sync option (with the first working voice) → ls_<face>_<tool>.mp4
  • grid.mp4: all lip-sync results side by side, plus results.csv with empty columns for
    your 1–5 ratings (pronunciation, lip-sync, realism). Measured numbers stay separate from ratings.
"""
from __future__ import annotations

import csv
import time
from pathlib import Path

from .config import Config
from .lipsync import cut_audio, lipsync
from .media import duration, ffmpeg_bin, run
from .tts import synthesize

DEFAULT_SCRIPT = ("नमस्ते दोस्तों! आज का सवाल: अगर क्षितिज के पार एक और धरती हो तो? "
                  "ज्ञान की इस श्रृंखला में WhatsApp और AI दोनों की बात करेंगे।")


def _voice(cfg: Config, opt: dict, text: str, out: Path) -> None:
    if opt.get("provider") == "silent":
        run([ffmpeg_bin(), "-y", "-f", "lavfi", "-i", f"sine=frequency=300:duration={max(3, len(text) / 14):.2f}",
             "-ar", "48000", "-ac", "1", str(out)])
        return
    # temporary overlay of this option's settings onto the main tts config
    original = dict(cfg.data.get("tts", {}))
    try:
        merged = dict(original)
        merged.update({k: v for k, v in opt.items() if k not in ("name", "sarvam")})
        if "sarvam" in opt:
            merged["sarvam"] = {**original.get("sarvam", {}), **opt["sarvam"]}
        cfg.data["tts"] = merged
        synthesize(cfg, text, out)
    finally:
        cfg.data["tts"] = original


def grid(videos: list[Path], out: Path, cell_w: int = 360, cell_h: int = 640, seconds: float = 10.0) -> Path:
    if not videos:
        raise ValueError("no videos for grid")
    ff = ffmpeg_bin()
    inputs, scales = [], []
    for i, v in enumerate(videos):
        inputs += ["-i", str(v)]
        scales.append(f"[{i}:v]scale={cell_w}:{cell_h}:force_original_aspect_ratio=decrease,"
                      f"pad={cell_w}:{cell_h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30[v{i}]")
    n = len(videos)
    cols = min(n, 3)
    layout = "|".join(f"{(i % cols) * cell_w}_{(i // cols) * cell_h}" for i in range(n))
    stack = "".join(f"[v{i}]" for i in range(n))
    vf = ";".join(scales) + (f";{stack}xstack=inputs={n}:layout={layout}:fill=black[out]" if n > 1 else ";[v0]copy[out]")
    run([ff, "-y", *inputs, "-filter_complex", vf, "-map", "[out]", "-map", "0:a?", "-t", f"{seconds:.2f}",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-c:a", "aac", str(out)])
    return out


def run_benchmark(cfg: Config, now: float | None = None) -> dict:
    b = cfg.get("benchmark", {}) or {}
    out_dir = cfg.root / "08_benchmark" / time.strftime("%Y%m%d-%H%M%S", time.localtime(now))
    out_dir.mkdir(parents=True, exist_ok=True)
    text = b.get("script") or DEFAULT_SCRIPT
    rows: list[dict] = []
    voices: list[tuple[str, Path]] = []

    for opt in b.get("voices", []) or []:
        name, path, t0 = opt.get("name", "voice"), out_dir / f"voice_{opt.get('name', 'voice')}.wav", time.time()
        try:
            _voice(cfg, opt, text, path)
            voices.append((name, path))
            rows.append({"test": "voice", "variant": name, "seconds": f"{time.time() - t0:.1f}", "ok": "yes",
                         "error": "", "file": path.name, "audio_sec": f"{duration(path):.1f}"})
        except Exception as exc:
            rows.append({"test": "voice", "variant": name, "seconds": f"{time.time() - t0:.1f}", "ok": "no",
                         "error": str(exc)[:200], "file": "", "audio_sec": ""})

    lip_videos: list[Path] = []
    if voices:
        talk_audio = cut_audio(voices[0][1], float(b.get("talk_seconds", 10)), out_dir / "talk_audio.wav")
        for face in b.get("faces", []) or []:
            face = Path(face)
            for tool in b.get("lipsync", []) or []:
                variant = f"{face.stem}__{tool.get('name', 'tool')}"
                out, t0 = out_dir / f"ls_{variant}.mp4", time.time()
                try:
                    lipsync(tool["command"], face, talk_audio, out, int(tool.get("timeout_sec", 3600)))
                    lip_videos.append(out)
                    rows.append({"test": "lipsync", "variant": variant, "seconds": f"{time.time() - t0:.1f}",
                                 "ok": "yes", "error": "", "file": out.name, "audio_sec": ""})
                except Exception as exc:
                    rows.append({"test": "lipsync", "variant": variant, "seconds": f"{time.time() - t0:.1f}",
                                 "ok": "no", "error": str(exc)[:200], "file": "", "audio_sec": ""})

    grid_path = grid(lip_videos, out_dir / "grid.mp4", seconds=float(b.get("talk_seconds", 10))) if lip_videos else None
    fields = ["test", "variant", "ok", "seconds", "audio_sec", "file", "error",
              "rating_pronunciation_1to5", "rating_lipsync_1to5", "rating_realism_1to5", "notes"]
    with open(out_dir / "results.csv", "w", newline="", encoding="utf-8-sig") as fh:   # BOM: opens cleanly in Excel
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    order = ", ".join(p.stem.replace("ls_", "") for p in lip_videos)
    (out_dir / "README.txt").write_text(
        f"Script: {text}\nGrid order (left→right, top→bottom): {order}\n"
        "हर option को 1–5 rating दें (3 लोगों से blind rating बेहतर)। Measured columns न बदलें.\n", encoding="utf-8")
    return {"dir": str(out_dir), "rows": rows, "grid": str(grid_path) if grid_path else "", "order": order}
