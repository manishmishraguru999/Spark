"""View counts for the daily report.

YouTube: public statistics via Data API key (no OAuth needed): videos.list part=statistics.
Instagram: media insights metric "views" (current metric; video_views/plays are deprecated).
"""
from __future__ import annotations

import re

import requests

YT_ID = re.compile(r"(?:shorts/|v=|youtu\.be/)([A-Za-z0-9_-]{11})")


def youtube_id(url_or_id: str) -> str | None:
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id
    m = YT_ID.search(url_or_id)
    return m.group(1) if m else None


def youtube_views(api_key: str, ids: list[str], session: requests.Session | None = None) -> dict[str, int]:
    if not (api_key and ids):
        return {}
    http, out = session or requests.Session(), {}
    for i in range(0, len(ids), 50):
        r = http.get("https://www.googleapis.com/youtube/v3/videos", timeout=30,
                     params={"part": "statistics", "id": ",".join(ids[i:i + 50]), "key": api_key})
        if r.status_code == 200:
            for item in r.json().get("items", []):
                out[item["id"]] = int(item.get("statistics", {}).get("viewCount", 0))
    return out


def instagram_views(cfg: dict, media_id: str, session: requests.Session | None = None) -> int | None:
    http = session or requests.Session()
    r = http.get(f"{cfg['graph_host'].rstrip('/')}/{cfg['version']}/{media_id}/insights", timeout=30,
                 params={"metric": "views", "access_token": cfg["access_token"]})
    if r.status_code != 200:
        return None
    for m in r.json().get("data", []):
        if m.get("name") == "views":
            vals = m.get("values") or [{}]
            return int(vals[0].get("value", 0))
    return None
