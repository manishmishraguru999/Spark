"""Trend radar: daily inspiration from YouTube public data (Data API key, no OAuth).

• videos.list chart=mostPopular regionCode=IN  (1 quota unit)
• search.list for your watch keywords, last N days, by view count (100 units each)
Results go to the phone with "💡 Idea बनाओ" buttons. They are inspiration only — never copy
someone else's video; make your own angle.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests

API = "https://www.googleapis.com/youtube/v3"


def most_popular(api_key: str, region: str = "IN", limit: int = 10,
                 session: requests.Session | None = None) -> list[dict]:
    http = session or requests.Session()
    r = http.get(f"{API}/videos", timeout=30, params={"part": "snippet,statistics", "chart": "mostPopular",
                                                      "regionCode": region, "maxResults": limit, "key": api_key})
    r.raise_for_status()
    return [_item(i) for i in r.json().get("items", [])]


def keyword_hits(api_key: str, keyword: str, days: int = 3, region: str = "IN", language: str = "hi",
                 limit: int = 5, session: requests.Session | None = None, now: float | None = None) -> list[dict]:
    http = session or requests.Session()
    after = datetime.fromtimestamp(now or time.time(), timezone.utc) - timedelta(days=days)
    r = http.get(f"{API}/search", timeout=30, params={
        "part": "id", "q": keyword, "type": "video", "order": "viewCount", "regionCode": region,
        "relevanceLanguage": language, "publishedAfter": after.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maxResults": limit, "key": api_key})
    r.raise_for_status()
    ids = [i["id"]["videoId"] for i in r.json().get("items", []) if i.get("id", {}).get("videoId")]
    if not ids:
        return []
    v = http.get(f"{API}/videos", timeout=30, params={"part": "snippet,statistics", "id": ",".join(ids),
                                                      "key": api_key})
    v.raise_for_status()
    return [dict(_item(i), keyword=keyword) for i in v.json().get("items", [])]


def _item(i: dict) -> dict:
    return {"id": i["id"], "title": i["snippet"]["title"], "channel": i["snippet"].get("channelTitle", ""),
            "views": int(i.get("statistics", {}).get("viewCount", 0)),
            "url": f"https://youtube.com/watch?v={i['id']}"}


def digest(api_key: str, keywords: list[str], region: str = "IN", top: int = 5,
           session: requests.Session | None = None, now: float | None = None) -> list[dict]:
    seen, items = set(), []
    for kw in keywords[:3]:                     # 3 × 100 units keeps far below the 10,000/day default
        for it in keyword_hits(api_key, kw, region=region, session=session, now=now):
            if it["id"] not in seen:
                seen.add(it["id"]); items.append(it)
    for it in most_popular(api_key, region, 10, session=session):
        if it["id"] not in seen:
            seen.add(it["id"]); items.append(dict(it, keyword="trending"))
    return sorted(items, key=lambda x: x["views"], reverse=True)[:top]
