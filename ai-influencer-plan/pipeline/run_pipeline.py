"""Start the BEAST pipeline.

    python run_pipeline.py --config config.yaml          # normal: Telegram + worker loop
    python run_pipeline.py --config config.yaml --demo   # one demo video, no Telegram, no publishing
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

from beast.config import load_config
from beast.jobs import JobStore, REVIEW
from beast.script_parser import parse_script
from beast.worker import Pipeline

DEMO_SCRIPT = """/new
TITLE: अगर चाँद गायब हो जाए तो?
HOOK: सोचो... आज रात आसमान में चाँद ही नहीं है!
VO: समुद्र की लहरें लगभग थम जाएँगी। रातें बहुत ज़्यादा अंधेरी होंगी। और धरती का झुकाव धीरे-धीरे बदलने लगेगा।
SCENE: night sky over Mumbai without the moon, cinematic, 9:16
SCENE: calm flat ocean at night, no waves
SCENE: earth from space slowly tilting
TALK: no
CAPTION: चाँद सिर्फ़ खूबसूरत नहीं, ज़रूरी भी है।
TAGS: #whatif #science #hindi
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--demo", action="store_true", help="make one demo video locally and exit")
    args = ap.parse_args()

    cfg = load_config(args.config)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout),
                                  logging.FileHandler(cfg.path("06_logs") / "pipeline.log", encoding="utf-8")])
    store = JobStore(cfg.path("06_logs") / "jobs.sqlite")

    if args.demo:
        pipe = Pipeline(cfg, store, tg=None)
        job = store.create(parse_script(DEMO_SCRIPT).to_dict())
        while pipe.step():
            pass
        job = store.get(job.id)
        if job.status != REVIEW:
            print(f"Demo failed: {job.status} {job.error}")
            return 1
        print(f"Demo OK\n  render : {job.results['render']}\n  preview: {job.results['preview']}")
        return 0

    from beast.telegram import Telegram
    tg = Telegram(cfg.get("telegram.bot_token", ""))
    pipe = Pipeline(cfg, store, tg=tg)
    pipe.notify("🟢 BEAST pipeline चालू है। /help")
    offset = int(store.kv_get("tg_offset", "0") or 0)
    while True:
        try:
            busy = bool(store.by_status("running"))
            for upd in tg.get_updates(offset, timeout=2 if busy else 25):
                offset = upd["update_id"] + 1
                store.kv_set("tg_offset", str(offset))
                pipe.handle_update(upd)
            pipe.step()
            pipe.publish_due()
            pipe.maintenance()
        except KeyboardInterrupt:
            return 0
        except Exception as exc:          # network hiccups: wait and continue
            logging.exception("Loop error: %s", exc)
            time.sleep(15)


if __name__ == "__main__":
    sys.exit(main())
