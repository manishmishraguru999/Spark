"""Script safety gate — runs before any GPU time is spent.

1. Rule check (always on, free): blocked words stop the job; sensitive topics and length
   problems become warnings shown with the preview.
2. Optional local LLM review via Ollama (structured JSON output), still free and offline.
"""
from __future__ import annotations

import json
import re

import requests

from .script_parser import Script

DEFAULT_SENSITIVE = [  # health / finance / legal advice (YouTube flags AI personas on these topics)
    "इलाज", "दवा", "cure", "medicine", "diagnos", "invest", "निवेश", "शेयर बाज़ार", "stock tip", "loan",
    "guaranteed", "गारंटी", "crypto", "कानूनी सलाह", "legal advice",
]

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "risk": {"type": "string", "enum": ["low", "medium", "high"]},
        "issues": {"type": "array", "items": {"type": "string"}},
        "claims_to_verify": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["risk", "issues", "claims_to_verify"],
}

REVIEW_PROMPT = """You review a short Hindi/Hinglish video script for a 16-30 audience before it is produced.
The host is a fully synthetic AI character. Flag: false or doubtful factual claims, health/finance/legal
advice, fear-mongering, hate, sexual content, real people or brands named, misleading clickbait,
anything that pretends the host is a real human. Reply only with JSON matching the schema.

SCRIPT:
TITLE: {title}
NARRATION: {narration}
CAPTION: {caption}
"""


def _find(words: list[str], text: str) -> list[str]:
    low = text.lower()
    return [w for w in words if w and w.lower() in low]


def rule_check(script: Script, cfg_safety: dict) -> tuple[list[str], list[str]]:
    """Returns (blocking_errors, warnings)."""
    text = " ".join([script.title, script.narration, script.caption, " ".join(script.scenes)])
    errors = [f"blocked word: {w}" for w in _find(cfg_safety.get("blocked_words", []), text)]
    errors += [f"real person / brand: {w}" for w in _find(cfg_safety.get("blocked_names", []), text)]
    warnings = [f"sensitive topic: {w}" for w in _find(cfg_safety.get("sensitive_words", DEFAULT_SENSITIVE), text)]
    words = len(re.findall(r"\S+", script.narration))
    lo, hi = cfg_safety.get("min_words", 35), cfg_safety.get("max_words", 220)
    if words < lo:
        warnings.append(f"narration छोटा है ({words} words)")
    if words > hi:
        warnings.append(f"narration लंबा है ({words} words) — 90s से ऊपर जा सकता है")
    if len(script.title) > 60:
        warnings.append(f"title {len(script.title)} characters (60 से कम रखें)")
    if not re.search(r"(source|स्रोत|https?://)", script.caption, re.IGNORECASE):
        warnings.append("caption में source line नहीं है")
    return errors, warnings


def llm_review(script: Script, cfg_ollama: dict, session: requests.Session | None = None) -> dict:
    http = session or requests.Session()
    r = http.post(f"{cfg_ollama.get('url', 'http://127.0.0.1:11434').rstrip('/')}/api/generate", timeout=300, json={
        "model": cfg_ollama["model"], "stream": False, "format": REVIEW_SCHEMA,
        "options": {"temperature": 0},
        "prompt": REVIEW_PROMPT.format(title=script.title, narration=script.narration, caption=script.caption)})
    r.raise_for_status()
    raw = r.json().get("response", "")
    data = json.loads(raw) if isinstance(raw, str) else raw
    data.setdefault("issues", []); data.setdefault("claims_to_verify", [])
    return data
