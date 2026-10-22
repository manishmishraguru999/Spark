"""Instagram Reels and Facebook Page Reels via Meta Graph API (resumable upload of a local file).

Instagram (official content-publishing doc):
  1. POST /{ig_user_id}/media  media_type=REELS, upload_type=resumable, caption
  2. POST rupload host /ig-api-upload/{version}/{container_id}  (headers: Authorization: OAuth, offset, file_size)
  3. GET  /{container_id}?fields=status_code  until FINISHED
  4. POST /{ig_user_id}/media_publish  creation_id
Facebook (Reels Publishing guide): video_reels start -> upload -> finish (video_state=PUBLISHED).
Limits: FB 30 API reels / 24h, 3–90 s; IG 100 posts / 24h (older docs say 50).
"""
from __future__ import annotations

import time
from pathlib import Path

import requests


class PublishError(RuntimeError):
    pass


def _check(r: requests.Response, what: str) -> dict:
    try:
        data = r.json()
    except ValueError:
        data = {}
    if r.status_code != 200 or "error" in data:
        raise PublishError(f"{what} failed ({r.status_code}): {str(data or r.text)[:400]}")
    return data


def _upload(http: requests.Session, url: str, token: str, video: Path) -> dict:
    data = video.read_bytes()
    r = http.post(url, data=data, timeout=1800, headers={
        "Authorization": f"OAuth {token}", "offset": "0", "file_size": str(len(data))})
    return _check(r, "upload")


def publish_instagram(cfg: dict, video: Path, caption: str, session: requests.Session | None = None,
                      poll_sec: float = 5.0, timeout_sec: float = 900) -> dict:
    http = session or requests.Session()
    host, ver, uid, token = cfg["graph_host"].rstrip("/"), cfg["version"], cfg["ig_user_id"], cfg["access_token"]
    if not (uid and token):
        raise PublishError("Instagram ig_user_id/access_token missing")
    params = {"media_type": "REELS", "upload_type": "resumable", "caption": caption,
              "share_to_feed": "true", "access_token": token}
    if cfg.get("thumb_offset_ms") is not None:          # cover frame position in the Reel
        params["thumb_offset"] = str(int(cfg["thumb_offset_ms"]))
    created = _check(http.post(f"{host}/{ver}/{uid}/media", timeout=60, data=params), "IG container")
    cid = created["id"]
    upload_url = created.get("uri") or f"{cfg['rupload_host'].rstrip('/')}/ig-api-upload/{ver}/{cid}"
    _upload(http, upload_url, token, video)
    deadline = time.time() + timeout_sec
    while True:
        st = _check(http.get(f"{host}/{ver}/{cid}", params={"fields": "status_code", "access_token": token},
                             timeout=30), "IG status")
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            raise PublishError(f"IG container {cid} status {code}")
        if time.time() > deadline:
            raise PublishError(f"IG container {cid} not ready after {timeout_sec}s")
        time.sleep(poll_sec)
    pub = _check(http.post(f"{host}/{ver}/{uid}/media_publish", timeout=60,
                           data={"creation_id": cid, "access_token": token}), "IG publish")
    return {"platform": "instagram", "id": pub.get("id"), "url": ""}


def publish_facebook(cfg: dict, video: Path, description: str, title: str = "",
                     session: requests.Session | None = None) -> dict:
    http = session or requests.Session()
    host, ver, page, token = cfg["graph_host"].rstrip("/"), cfg["version"], cfg["page_id"], cfg["page_access_token"]
    if not (page and token):
        raise PublishError("Facebook page_id/page_access_token missing")
    endpoint = f"{host}/{ver}/{page}/video_reels"
    start = _check(http.post(endpoint, timeout=60, data={"upload_phase": "start", "access_token": token}),
                   "FB start")
    vid = start["video_id"]
    upload_url = start.get("upload_url") or f"{cfg['rupload_host'].rstrip('/')}/video-upload/{ver}/{vid}"
    _upload(http, upload_url, token, video)
    _check(http.post(endpoint, timeout=60, data={
        "upload_phase": "finish", "video_id": vid, "video_state": "PUBLISHED",
        "description": description, "title": title, "access_token": token}), "FB finish")
    return {"platform": "facebook", "id": vid, "url": f"https://www.facebook.com/reel/{vid}"}


def refresh_instagram_token(cfg: dict, session: requests.Session | None = None) -> str:
    """Long-lived Instagram tokens last ~60 days; call this every ~50 days (Instagram Login)."""
    http = session or requests.Session()
    data = _check(http.get(f"{cfg['graph_host'].rstrip('/')}/refresh_access_token", timeout=30, params={
        "grant_type": "ig_refresh_token", "access_token": cfg["access_token"]}), "IG token refresh")
    return data["access_token"]
