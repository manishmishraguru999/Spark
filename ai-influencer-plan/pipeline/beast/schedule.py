"""Publish-slot scheduling in local time (default Asia/Kolkata)."""
from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def next_slot(now_ts: float, slots: list[str], taken: list[float], tz: str = "Asia/Kolkata",
              min_gap_min: int = 30) -> float:
    """Earliest future slot ("HH:MM") not already used by another scheduled job."""
    zone = ZoneInfo(tz)
    now = datetime.fromtimestamp(now_ts, zone)
    times = sorted(tuple(int(x) for x in s.split(":")) for s in slots) or [(19, 0)]
    for day in range(0, 60):
        base = (now + timedelta(days=day)).date()
        for hh, mm in times:
            cand = datetime(base.year, base.month, base.day, hh, mm, tzinfo=zone)
            if cand.timestamp() < now_ts + min_gap_min * 60:
                continue
            if any(abs(cand.timestamp() - t) < 60 for t in taken):
                continue
            return cand.timestamp()
    raise RuntimeError("No free slot in the next 60 days")


def fmt(ts: float, tz: str = "Asia/Kolkata") -> str:
    return datetime.fromtimestamp(ts, ZoneInfo(tz)).strftime("%d %b %H:%M")
