"""Minimal Telegram Bot API client (long polling, no webhook, so no open ports on the PC)."""
from __future__ import annotations

import json
from pathlib import Path

import requests


class Telegram:
    def __init__(self, token: str, session: requests.Session | None = None):
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN set नहीं है")
        self.base = f"https://api.telegram.org/bot{token}"
        self.http = session or requests.Session()

    def _call(self, method: str, timeout: float = 60, **kwargs) -> dict:
        r = self.http.post(f"{self.base}/{method}", timeout=timeout, **kwargs)
        data = r.json() if r.content else {}
        if not data.get("ok"):
            raise RuntimeError(f"Telegram {method} failed: {str(data)[:300]}")
        return data

    def get_updates(self, offset: int, timeout: int = 25) -> list[dict]:
        return self._call("getUpdates", timeout=timeout + 10,
                          data={"offset": offset, "timeout": timeout}).get("result", [])

    @staticmethod
    def keyboard(buttons: list[list[tuple[str, str]]]) -> str:
        return json.dumps({"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row]
                                               for row in buttons]}, ensure_ascii=False)

    def send_message(self, chat_id: int, text: str, buttons=None) -> dict:
        data = {"chat_id": chat_id, "text": text[:4000]}
        if buttons:
            data["reply_markup"] = self.keyboard(buttons)
        return self._call("sendMessage", data=data)

    def send_video(self, chat_id: int, path: Path, caption: str, buttons=None) -> dict:
        data = {"chat_id": chat_id, "caption": caption[:1000], "supports_streaming": "true"}
        if buttons:
            data["reply_markup"] = self.keyboard(buttons)
        with open(path, "rb") as fh:
            return self._call("sendVideo", timeout=300, data=data, files={"video": (path.name, fh, "video/mp4")})

    def answer_callback(self, callback_id: str, text: str = "") -> None:
        self._call("answerCallbackQuery", data={"callback_query_id": callback_id, "text": text[:190]})
