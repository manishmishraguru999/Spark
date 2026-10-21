"""Parse the script message sent from the phone.

Format (one field per line, field names are case-insensitive):

    TITLE: अगर चाँद गायब हो जाए तो?
    HOOK: सोचो... आज रात आसमान में चाँद ही नहीं!
    VO: पूरा narration, एक या कई lines में।
    SCENE: cinematic night sky without moon over Mumbai, 9:16
    SCENE: flat calm ocean, no tides, drone shot
    TALK: yes
    CAPTION: Instagram/Facebook caption
    TAGS: #whatif #science #hindi

Lines without a field name continue the previous field (handy for long VO).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

FIELD_RE = re.compile(r"^\s*(TITLE|HOOK|VO|SCENE|TALK|CAPTION|TAGS)\s*[:：]\s*(.*)$", re.IGNORECASE)


class ScriptError(ValueError):
    pass


@dataclass
class Script:
    title: str
    hook: str
    vo: str
    scenes: list[str] = field(default_factory=list)
    talk: bool = True
    caption: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def narration(self) -> str:
        """Text that is spoken: hook first, then VO."""
        return " ".join(p for p in (self.hook.strip(), self.vo.strip()) if p)

    def to_dict(self) -> dict:
        return {"title": self.title, "hook": self.hook, "vo": self.vo, "scenes": self.scenes,
                "talk": self.talk, "caption": self.caption, "tags": self.tags}

    @classmethod
    def from_dict(cls, d: dict) -> "Script":
        return cls(**d)


def parse_script(text: str, max_tags: int = 3) -> Script:
    text = re.sub(r"^\s*/new(@\w+)?\s*", "", text.strip(), flags=re.IGNORECASE)
    fields: dict[str, list[str]] = {}
    scenes: list[str] = []
    current: str | None = None
    for line in text.splitlines():
        m = FIELD_RE.match(line)
        if m:
            current = m.group(1).upper()
            value = m.group(2).strip()
            if current == "SCENE":
                scenes.append(value)
            else:
                fields.setdefault(current, []).append(value)
        elif current and line.strip():
            if current == "SCENE":
                scenes[-1] = (scenes[-1] + " " + line.strip()).strip()
            else:
                fields[current].append(line.strip())

    def joined(key: str) -> str:
        return " ".join(v for v in fields.get(key, []) if v).strip()

    title, vo = joined("TITLE"), joined("VO")
    if not title:
        raise ScriptError("TITLE: वाली line नहीं मिली")
    if not vo:
        raise ScriptError("VO: (narration) वाली line नहीं मिली")
    if not scenes:
        raise ScriptError("कम से कम एक SCENE: line चाहिए")
    tags = re.findall(r"#[\wऀ-ॿ]+", joined("TAGS"))[:max_tags]
    talk = joined("TALK").lower() not in {"no", "n", "false", "0", "नहीं"}
    return Script(title=title, hook=joined("HOOK"), vo=vo, scenes=scenes, talk=talk,
                  caption=joined("CAPTION"), tags=tags)
