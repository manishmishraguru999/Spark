"""Load config.yaml. Values written as "ENV:NAME" are read from environment variables,
so tokens never have to live inside the config file."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

JOB_SUBDIRS = ("00_inbox", "01_assets", "02_jobs", "03_renders", "04_previews",
               "05_published", "06_logs", "07_secrets")


def _resolve(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("ENV:"):
        return os.environ.get(value[4:], "")
    if isinstance(value, dict):
        return {k: _resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve(v) for v in value]
    return value


@dataclass
class Config:
    data: dict
    root: Path

    def get(self, dotted: str, default: Any = None) -> Any:
        node: Any = self.data
        for part in dotted.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    def path(self, sub: str) -> Path:
        return self.root / sub

    def ensure_dirs(self) -> None:
        for sub in JOB_SUBDIRS:
            self.path(sub).mkdir(parents=True, exist_ok=True)


def load_config(path: str | Path) -> Config:
    with open(path, encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}
    data = _resolve(raw)
    root = Path(data.get("paths", {}).get("root", "./AI_INFLUENCER")).expanduser()
    cfg = Config(data=data, root=root)
    cfg.ensure_dirs()
    return cfg
