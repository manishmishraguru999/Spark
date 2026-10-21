"""Keeps an always-on PC healthy: disk guard and cleanup of old working folders."""
from __future__ import annotations

import shutil
import time
from pathlib import Path


def free_gb(path: Path) -> float:
    return shutil.disk_usage(path).free / 1024 ** 3


def cleanup_job_dirs(jobs_dir: Path, finished_ids: set[str], older_than_days: float, now: float | None = None) -> list[str]:
    """Delete 02_jobs/<id>/ for finished jobs older than N days. Final renders and
    05_published records are kept."""
    now = now or time.time()
    removed = []
    for d in jobs_dir.iterdir() if jobs_dir.exists() else []:
        if d.is_dir() and d.name in finished_ids and now - d.stat().st_mtime > older_than_days * 86400:
            shutil.rmtree(d, ignore_errors=True)
            removed.append(d.name)
    return removed
