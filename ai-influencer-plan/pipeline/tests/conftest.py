import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from beast.config import load_config  # noqa: E402
from beast.jobs import JobStore  # noqa: E402


class FakeResponse:
    def __init__(self, data=None, status=200, content=b""):
        self._data, self.status_code = data, status
        self.content = content or (json.dumps(data).encode() if data is not None else b"")
        self.text = self.content.decode(errors="replace")

    def json(self):
        if self._data is None:
            raise ValueError("no json")
        return self._data


class FakeSession:
    """Records calls; responds from a list of (method, url_substring, response) rules, first match wins
    and is consumed unless sticky."""

    def __init__(self, rules):
        self.rules, self.calls = list(rules), []

    def _match(self, method, url, **kw):
        self.calls.append((method, url, kw))
        for i, (m, part, resp, *sticky) in enumerate(self.rules):
            if m == method and part in url:
                if not sticky:
                    self.rules.pop(i)
                return resp
        raise AssertionError(f"Unexpected {method} {url}")

    def post(self, url, **kw):
        return self._match("POST", url, **kw)

    def get(self, url, **kw):
        return self._match("GET", url, **kw)


@pytest.fixture
def cfg(tmp_path):
    data = yaml.safe_load((Path(__file__).resolve().parents[1] / "config.example.yaml").read_text(encoding="utf-8"))
    data["paths"]["root"] = str(tmp_path / "AI")
    data["tts"]["provider"] = "silent"
    data["telegram"]["allowed_chat_ids"] = [42]
    data["video"]["font"] = "DejaVu Sans"
    data["publish"]["youtube"]["manual_sync_dir"] = str(tmp_path / "AI" / "yt_sync")
    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return load_config(p)


@pytest.fixture
def store(cfg):
    return JobStore(cfg.path("06_logs") / "jobs.sqlite")
