"""API publishers. Function name must be publish_<platform>(ctx) -> dict (see registry.py)."""
from __future__ import annotations

import shutil
import time
from urllib.parse import quote

import requests

from .meta import PublishError, _check, publish_facebook as _fb, publish_instagram as _ig
from .registry import PublishContext
from .youtube import publish_youtube as _yt

HTTP: requests.Session | None = None      # tests inject a fake session here


def _http() -> requests.Session:
    return HTTP or requests.Session()


def publish_youtube(ctx: PublishContext) -> dict:
    # youtube.py handles both its own manual sync folder and API mode
    return _yt(ctx.cfg, ctx.video, ctx.title, ctx.formatted_caption(), ctx.tags, ctx.job_id)


def publish_instagram(ctx: PublishContext) -> dict:
    return _ig(ctx.cfg, ctx.video, ctx.formatted_caption(), session=HTTP)


def publish_facebook(ctx: PublishContext) -> dict:
    return _fb(ctx.cfg, ctx.video, ctx.formatted_caption(), ctx.title, session=HTTP)


def publish_telegram_channel(ctx: PublishContext) -> dict:
    """Bot must be an admin of the channel. Bot API upload limit is 50 MB."""
    token, chat = ctx.cfg.get("bot_token"), ctx.cfg.get("channel_id")
    if not (token and chat):
        raise PublishError("telegram_channel bot_token/channel_id missing")
    if ctx.video.stat().st_size > 50 * 1024 * 1024:
        raise PublishError("video 50 MB से बड़ी है (Telegram bot limit)")
    with open(ctx.video, "rb") as fh:
        data = _check(_http().post(f"https://api.telegram.org/bot{token}/sendVideo", timeout=600,
                                   data={"chat_id": chat, "caption": ctx.formatted_caption()[:1024],
                                         "supports_streaming": "true"},
                                   files={"video": (ctx.video.name, fh, "video/mp4")}), "Telegram channel")
    if not data.get("ok"):
        raise PublishError(f"Telegram channel failed: {str(data)[:300]}")
    msg_id = data["result"]["message_id"]
    url = f"https://t.me/{str(chat).lstrip('@')}/{msg_id}" if str(chat).startswith("@") else ""
    return {"platform": "telegram_channel", "id": msg_id, "url": url}


def publish_threads(ctx: PublishContext, poll_sec: float = 5.0, timeout_sec: float = 900) -> dict:
    """Threads fetches the video from a public URL. Needs public_dir (a folder your web host or
    tunnel serves) and public_base_url. Without them the registry falls back to manual."""
    c = ctx.cfg
    pub_dir, base = c.get("public_dir"), (c.get("public_base_url") or "").rstrip("/")
    if not (pub_dir and base and c.get("user_id") and c.get("access_token")):
        raise PublishError("threads: public_dir/public_base_url/user_id/access_token चाहिए (या mode: manual)")
    name = f"{ctx.job_id}.mp4"
    shutil.copy2(ctx.video, f"{pub_dir}/{name}")
    host, ver, uid, tok = c.get("graph_host", "https://graph.threads.net").rstrip("/"), c.get("version", "v1.0"), \
        c["user_id"], c["access_token"]
    http = _http()
    created = _check(http.post(f"{host}/{ver}/{uid}/threads", timeout=60, data={
        "media_type": "VIDEO", "video_url": f"{base}/{quote(name)}", "text": ctx.formatted_caption(),
        "access_token": tok}), "Threads container")
    cid, deadline = created["id"], time.time() + timeout_sec
    while True:
        st = _check(http.get(f"{host}/{ver}/{cid}", timeout=30, params={"fields": "status,error_message",
                                                                     "access_token": tok}), "Threads status")
        if st.get("status") == "FINISHED":
            break
        if st.get("status") in ("ERROR", "EXPIRED") or time.time() > deadline:
            raise PublishError(f"Threads container {cid}: {st}")
        time.sleep(poll_sec)
    pub = _check(http.post(f"{host}/{ver}/{uid}/threads_publish", timeout=60,
                           data={"creation_id": cid, "access_token": tok}), "Threads publish")
    return {"platform": "threads", "id": pub.get("id"), "url": ""}


def publish_pinterest(ctx: PublishContext, poll_sec: float = 5.0, timeout_sec: float = 900) -> dict:
    """Register media → S3 upload → poll → create pin with video_id (Pinterest API v5)."""
    c = ctx.cfg
    tok, board = c.get("access_token"), c.get("board_id")
    if not (tok and board):
        raise PublishError("pinterest access_token/board_id missing")
    api, http = c.get("api_host", "https://api.pinterest.com").rstrip("/"), _http()
    auth = {"Authorization": f"Bearer {tok}"}
    reg = _check(http.post(f"{api}/v5/media", json={"media_type": "video"}, headers=auth, timeout=60),
                 "Pinterest register")
    with open(ctx.video, "rb") as fh:
        up = http.post(reg["upload_url"], data=reg.get("upload_parameters", {}),
                       files={"file": (ctx.video.name, fh, "video/mp4")}, timeout=1800)
    if up.status_code not in (200, 201, 204):
        raise PublishError(f"Pinterest S3 upload failed ({up.status_code})")
    media_id, deadline = reg["media_id"], time.time() + timeout_sec
    while True:
        st = _check(http.get(f"{api}/v5/media/{media_id}", headers=auth, timeout=30), "Pinterest status")
        if st.get("status") == "succeeded":
            break
        if st.get("status") == "failed" or time.time() > deadline:
            raise PublishError(f"Pinterest media {media_id}: {st}")
        time.sleep(poll_sec)
    pin = _check(http.post(f"{api}/v5/pins", headers=auth, timeout=60, json={
        "board_id": board, "title": ctx.title[:100], "description": ctx.formatted_caption(),
        "media_source": {"source_type": "video_id", "media_id": media_id,
                         "cover_image_key_frame_time": float(c.get("cover_frame_sec", 1))}}), "Pinterest pin")
    return {"platform": "pinterest", "id": pin.get("id"), "url": f"https://www.pinterest.com/pin/{pin.get('id')}/"}
