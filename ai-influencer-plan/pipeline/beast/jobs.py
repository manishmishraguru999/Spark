"""SQLite job store. Every job moves through STAGES; progress is saved after each stage,
so a crash or reboot resumes where it stopped."""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

STAGES = ("check", "tts", "images", "clips", "lipsync", "assemble", "label", "qc", "preview")

# status values
RUNNING, REVIEW, SCHEDULED, PUBLISHING, PUBLISHED, FAILED, CANCELLED = (
    "running", "review", "scheduled", "publishing", "published", "failed", "cancelled")


@dataclass
class Job:
    id: str
    created_at: float
    status: str
    stage: int
    script: dict
    seed: int
    results: dict = field(default_factory=dict)
    error: str = ""
    scheduled_at: float | None = None
    attempts: int = 0

    @property
    def stage_name(self) -> str:
        return STAGES[self.stage] if self.stage < len(STAGES) else "done"


class JobStore:
    def __init__(self, db_path: Path):
        self.db = sqlite3.connect(str(db_path))
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, created_at REAL, status TEXT, stage INTEGER,
                script TEXT, seed INTEGER, results TEXT, error TEXT,
                scheduled_at REAL, attempts INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS ideas (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at REAL,
                text TEXT, used INTEGER DEFAULT 0);
        """)

    def create(self, script: dict, seed: int | None = None) -> Job:
        job = Job(id=time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:4],
                  created_at=time.time(), status=RUNNING, stage=0, script=script,
                  seed=seed if seed is not None else int(uuid.uuid4().int % 2**31))
        self.save(job)
        return job

    def save(self, job: Job) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (job.id, job.created_at, job.status, job.stage, json.dumps(job.script, ensure_ascii=False),
             job.seed, json.dumps(job.results, ensure_ascii=False), job.error, job.scheduled_at,
             job.attempts))
        self.db.commit()

    def _row(self, r: sqlite3.Row) -> Job:
        return Job(id=r["id"], created_at=r["created_at"], status=r["status"], stage=r["stage"],
                   script=json.loads(r["script"]), seed=r["seed"], results=json.loads(r["results"] or "{}"),
                   error=r["error"] or "", scheduled_at=r["scheduled_at"], attempts=r["attempts"] or 0)

    def get(self, job_id: str) -> Job | None:
        r = self.db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        return self._row(r) if r else None

    def by_status(self, *statuses: str) -> list[Job]:
        q = f"SELECT * FROM jobs WHERE status IN ({','.join('?' * len(statuses))}) ORDER BY created_at"
        return [self._row(r) for r in self.db.execute(q, statuses)]

    def recent(self, limit: int = 10) -> list[Job]:
        return [self._row(r) for r in
                self.db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))]

    def kv_get(self, key: str, default: str = "") -> str:
        r = self.db.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return r["value"] if r else default

    def kv_set(self, key: str, value: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO kv VALUES (?,?)", (key, value))
        self.db.commit()

    # ---------- idea bank ----------
    def add_idea(self, text: str) -> int:
        cur = self.db.execute("INSERT INTO ideas (created_at, text) VALUES (?, ?)", (time.time(), text))
        self.db.commit()
        return int(cur.lastrowid)

    def ideas(self, include_used: bool = False) -> list[tuple[int, str, int]]:
        q = "SELECT id, text, used FROM ideas" + ("" if include_used else " WHERE used=0") + " ORDER BY id"
        return [(r["id"], r["text"], r["used"]) for r in self.db.execute(q)]

    def mark_idea(self, idea_id: int, used: bool = True) -> None:
        self.db.execute("UPDATE ideas SET used=? WHERE id=?", (int(used), idea_id))
        self.db.commit()
