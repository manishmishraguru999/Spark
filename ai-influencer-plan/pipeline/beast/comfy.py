"""ComfyUI HTTP client.

Export your workflow from ComfyUI with "Export (API)". Put these placeholders inside
the exported JSON wherever the value should change per job:

    "{{PROMPT}}"    positive prompt text
    "{{NEGATIVE}}"  negative prompt text
    "{{SEED}}"      seed (replaced by an integer)
    "{{IMAGE}}"     input image filename (image-to-video workflows)
    "{{PREFIX}}"    filename prefix for SaveImage / video save nodes

ComfyUI has no password by default: keep it on 127.0.0.1, never expose port 8188.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

import requests

MEDIA_KEYS = ("images", "gifs", "videos", "video", "files")


class ComfyError(RuntimeError):
    pass


def fill_template(node, values: dict):
    if isinstance(node, dict):
        return {k: fill_template(v, values) for k, v in node.items()}
    if isinstance(node, list):
        return [fill_template(v, values) for v in node]
    if isinstance(node, str):
        for key, val in values.items():
            token = "{{" + key + "}}"
            if node == token:
                return val                      # keep int type for SEED
            if token in node:
                node = node.replace(token, str(val))
    return node


class ComfyClient:
    def __init__(self, base_url: str, session: requests.Session | None = None, poll_sec: float = 2.0):
        self.base = base_url.rstrip("/")
        self.http = session or requests.Session()
        self.poll_sec = poll_sec
        self.client_id = uuid.uuid4().hex

    def upload_image(self, path: Path) -> str:
        with open(path, "rb") as fh:
            r = self.http.post(f"{self.base}/upload/image", files={"image": (path.name, fh, "image/png")},
                               data={"overwrite": "true"}, timeout=120)
        if r.status_code != 200:
            raise ComfyError(f"upload failed {r.status_code}: {r.text[:200]}")
        return r.json().get("name", path.name)

    def queue(self, workflow: dict) -> str:
        r = self.http.post(f"{self.base}/prompt", json={"prompt": workflow, "client_id": self.client_id},
                           timeout=60)
        if r.status_code != 200:
            raise ComfyError(f"/prompt failed {r.status_code}: {r.text[:300]}")
        return r.json()["prompt_id"]

    def wait(self, prompt_id: str, timeout_sec: float) -> dict:
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            r = self.http.get(f"{self.base}/history/{prompt_id}", timeout=30)
            if r.status_code == 200:
                entry = r.json().get(prompt_id)
                if entry:
                    status = entry.get("status", {})
                    if status.get("status_str") == "error":
                        raise ComfyError(f"Workflow error: {json.dumps(status)[:400]}")
                    if entry.get("outputs") and status.get("completed", True):
                        return entry["outputs"]
            time.sleep(self.poll_sec)
        raise ComfyError(f"Timeout after {timeout_sec}s (prompt {prompt_id})")

    def download_outputs(self, outputs: dict, dest_dir: Path, stem: str) -> list[Path]:
        files: list[Path] = []
        for node_out in outputs.values():
            for key in MEDIA_KEYS:
                for item in node_out.get(key, []) or []:
                    if not isinstance(item, dict) or "filename" not in item:
                        continue
                    params = {"filename": item["filename"], "subfolder": item.get("subfolder", ""),
                              "type": item.get("type", "output")}
                    r = self.http.get(f"{self.base}/view", params=params, timeout=300)
                    if r.status_code != 200:
                        raise ComfyError(f"/view failed for {item['filename']}")
                    dest = dest_dir / f"{stem}_{len(files)}{Path(item['filename']).suffix}"
                    dest.write_bytes(r.content)
                    files.append(dest)
        if not files:
            raise ComfyError("Workflow ने कोई output file नहीं दी")
        return files

    def run_workflow(self, template_path: Path, values: dict, dest_dir: Path, stem: str,
                     timeout_sec: float = 1800) -> list[Path]:
        workflow = json.loads(Path(template_path).read_text(encoding="utf-8"))
        prompt_id = self.queue(fill_template(workflow, values))
        return self.download_outputs(self.wait(prompt_id, timeout_sec), dest_dir, stem)
