"""YouTube Shorts.

mode "manual" (default, recommended until your API project passes Google's audit):
  copies the final file + a .txt with title/description to a folder that syncs to the phone
  (Google Drive / OneDrive). Upload from the YouTube app and switch on "altered content".
mode "api": videos.insert with status.containsSyntheticMedia=true. Uploads from an
  unverified API project are locked PRIVATE by Google until the project is audited.
"""
from __future__ import annotations

import shutil
from pathlib import Path


class YouTubeError(RuntimeError):
    pass


def manual_handoff(cfg: dict, video: Path, title: str, description: str, job_id: str) -> dict:
    dest_dir = Path(cfg.get("manual_sync_dir", ""))
    if not str(dest_dir):
        raise YouTubeError("youtube.manual_sync_dir set नहीं है")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{job_id}.mp4"
    shutil.copy2(video, dest)
    (dest_dir / f"{job_id}.txt").write_text(
        f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\n"
        "Upload करते समय: Altered or synthetic content = YES, Made for kids = NO\n", encoding="utf-8")
    return {"platform": "youtube", "path": str(dest), "url": "", "manual": True}


def upload_api(cfg: dict, video: Path, title: str, description: str, tags: list[str]) -> dict:
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as exc:
        raise YouTubeError("pip install google-api-python-client google-auth-oauthlib") from exc

    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    token_file = Path(cfg["token_file"])
    creds = Credentials.from_authorized_user_file(str(token_file), scopes) if token_file.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cfg["client_secrets"], scopes)
        creds = flow.run_local_server(port=0)          # first run only, on the PC
    token_file.write_text(creds.to_json(), encoding="utf-8")

    yt = build("youtube", "v3", credentials=creds)
    body = {
        "snippet": {"title": title[:100], "description": description[:4900], "tags": [t.lstrip("#") for t in tags],
                    "categoryId": str(cfg.get("category_id", "24"))},
        "status": {"privacyStatus": cfg.get("privacy", "public"),
                   "selfDeclaredMadeForKids": bool(cfg.get("made_for_kids", False)),
                   "containsSyntheticMedia": bool(cfg.get("contains_synthetic_media", True))},
    }
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    return {"platform": "youtube", "id": resp["id"], "url": f"https://youtube.com/shorts/{resp['id']}"}


def publish_youtube(cfg: dict, video: Path, title: str, description: str, tags: list[str], job_id: str) -> dict:
    if cfg.get("mode", "manual") == "api":
        return upload_api(cfg, video, title, description, tags)
    return manual_handoff(cfg, video, title, description, job_id)
