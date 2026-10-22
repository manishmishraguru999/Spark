"""Weekly backup of what cannot be re-made: assets, final renders, publish records, job database.
Working folders (02_jobs) and previews are skipped — they can be regenerated."""
from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

BACKUP_DIRS = ("01_assets", "03_renders", "05_published", "00_inbox")


def copy_newer(src: Path, dst: Path) -> int:
    copied = 0
    for f in src.rglob("*") if src.exists() else []:
        if not f.is_file():
            continue
        target = dst / f.relative_to(src)
        if target.exists() and target.stat().st_mtime >= f.stat().st_mtime and target.stat().st_size == f.stat().st_size:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
        copied += 1
    return copied


def run_backup(root: Path, dest: Path, db_path: Path) -> dict:
    if dest.resolve() == root.resolve() or root.resolve() in dest.resolve().parents:
        raise ValueError("Backup destination must be outside the project folder (दूसरी drive बेहतर)")
    dest.mkdir(parents=True, exist_ok=True)
    counts = {d: copy_newer(root / d, dest / d) for d in BACKUP_DIRS}
    if db_path.exists():                       # consistent copy even while the pipeline is running
        (dest / "06_logs").mkdir(exist_ok=True)
        src, dst = sqlite3.connect(str(db_path)), sqlite3.connect(str(dest / "06_logs" / db_path.name))
        try:
            src.backup(dst)
        finally:
            src.close(); dst.close()
        counts["database"] = 1
    return counts
