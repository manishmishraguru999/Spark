"""Build the final 9:16 video with ffmpeg: talking-head segment + scene segments
(video clips, or still images with a slow Ken Burns zoom), voice, optional music,
burned-in Devanagari captions. Also makes the small preview for the phone."""
from __future__ import annotations

from pathlib import Path

from .captions import timed_lines, write_ass
from .media import duration, ffmpeg_bin, run

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}


def _norm_filter(w: int, h: int, fps: int) -> str:
    return (f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"fps={fps},format=yuv420p,setsar=1")


def make_segment(src: Path, seconds: float, out: Path, w: int, h: int, fps: int) -> Path:
    ff = ffmpeg_bin()
    if src.suffix.lower() in VIDEO_EXT:
        run([ff, "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{seconds:.3f}", "-an",
             "-vf", _norm_filter(w, h, fps), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])
    else:
        frames = max(int(seconds * fps), 1)
        zoom = (f"scale={w * 2}:{h * 2}:force_original_aspect_ratio=increase,crop={w * 2}:{h * 2},"
                f"zoompan=z='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                f":d={frames}:s={w}x{h}:fps={fps},format=yuv420p,setsar=1")
        run([ff, "-y", "-loop", "1", "-i", str(src), "-t", f"{seconds:.3f}", "-vf", zoom,
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", str(out)])
    return out


def plan_segments(total: float, talk_clip: Path | None, talk_sec: float, scene_sources: list[Path]) -> list[tuple[Path, float]]:
    plan: list[tuple[Path, float]] = []
    remaining = total
    if talk_clip is not None:
        t = min(talk_sec, total, duration(talk_clip))
        plan.append((talk_clip, t))
        remaining -= t
    if remaining > 0.05 and scene_sources:
        each = remaining / len(scene_sources)
        plan.extend((src, each) for src in scene_sources)
    elif not plan and scene_sources:
        plan.append((scene_sources[0], total))
    return plan


def assemble(job_dir: Path, voice: Path, scene_sources: list[Path], out: Path, *, caption_text: str,
             talk_clip: Path | None = None, talk_sec: float = 12.0, music: Path | None = None,
             music_volume: float = 0.12, width: int = 1080, height: int = 1920, fps: int = 30,
             font: str = "Nirmala UI", font_size: int = 80, max_seconds: float = 90.0,
             caption_events: list[tuple[float, float, str]] | None = None) -> Path:
    ff = ffmpeg_bin()
    total = min(duration(voice), max_seconds)
    seg_dir = job_dir / "segments"
    seg_dir.mkdir(exist_ok=True)
    segments = [make_segment(src, sec, seg_dir / f"seg{i:02d}.mp4", width, height, fps)
                for i, (src, sec) in enumerate(plan_segments(total, talk_clip, talk_sec, scene_sources))]
    (seg_dir / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in segments), encoding="utf-8")
    run([ff, "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "visual.mp4"], cwd=seg_dir)

    events = caption_events if caption_events else timed_lines(caption_text, total)
    write_ass(events, job_dir / "captions.ass", width, height, font, font_size)
    inputs = [ff, "-y", "-i", str(seg_dir / "visual.mp4"), "-i", str(voice)]
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]
        audio = (f"[2:a]volume={music_volume}[m];[1:a][m]amix=inputs=2:duration=first:dropout_transition=0,"
                 f"loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    else:
        audio = "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    # Run inside job_dir and use the relative name, so Windows drive letters never break the filter.
    run(inputs + ["-filter_complex", f"[0:v]subtitles=captions.ass[v];{audio}", "-map", "[v]", "-map", "[a]",
                  "-t", f"{total:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                  "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out.resolve())],
        cwd=job_dir)
    return out


def make_cover(src: Path, out: Path) -> Path:
    """Pick a representative, non-blurry frame (ffmpeg thumbnail filter) as the cover image."""
    run([ffmpeg_bin(), "-y", "-i", str(src), "-vf", "thumbnail=90", "-frames:v", "1", "-q:v", "2", str(out)])
    return out


def make_preview(src: Path, out: Path) -> Path:
    run([ffmpeg_bin(), "-y", "-i", str(src), "-vf", "scale=480:-2", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "30", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", str(out)])
    return out
