"""Start the BEAST pipeline.

    python run_pipeline.py --config config.yaml          # normal: Telegram + worker loop
    python run_pipeline.py --config config.yaml --demo   # one demo video, no Telegram, no publishing
    python run_pipeline.py --config config.yaml --doctor # check the whole setup (Hindi fixes)
    python run_pipeline.py --new-project NAME --base X:/ # new venture: folders + config from template
    python run_pipeline.py --config config.yaml --benchmark  # voice / lip-sync / face comparison
"""
from __future__ import annotations

import argparse
import logging
import re
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from beast.config import JOB_SUBDIRS, load_config
from beast.doctor import report as doctor_report, run_checks
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


def new_project(name: str, base: str) -> int:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        print("Project name में सिर्फ़ A-Z, 0-9, _ और - रखें")
        return 1
    root = Path(base) / name
    if (root / "pipeline_config.yaml").exists():
        print(f"{root} पहले से मौजूद है")
        return 1
    for sub in JOB_SUBDIRS:
        (root / sub).mkdir(parents=True, exist_ok=True)
    template = (Path(__file__).parent / "config.example.yaml").read_text(encoding="utf-8")
    config = template.replace("X:/AI_INFLUENCER", root.as_posix())
    (root / "pipeline_config.yaml").write_text(config, encoding="utf-8")
    print(f"✅ Project {name} बना: {root}\nअगला कदम:\n  1. {root / 'pipeline_config.yaml'} edit करें"
          f" (नया Telegram bot, platforms)\n  2. python run_pipeline.py --config \"{root / 'pipeline_config.yaml'}\" --doctor")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--demo", action="store_true", help="make one demo video locally and exit")
    ap.add_argument("--doctor", action="store_true", help="check setup and exit")
    ap.add_argument("--benchmark", action="store_true", help="compare voices / lip-sync / faces and exit")
    ap.add_argument("--new-project", metavar="NAME")
    ap.add_argument("--base", default="X:/")
    args = ap.parse_args()

    if args.new_project:
        return new_project(args.new_project, args.base)
    cfg = load_config(args.config)
    if args.doctor:
        checks = run_checks(cfg)
        print(doctor_report(checks))
        return 0 if all(ok for ok, *_ in checks) else 1
    if args.benchmark:
        from beast.benchmark import run_benchmark
        res = run_benchmark(cfg)
        for r in res["rows"]:
            print(f"{'✅' if r['ok'] == 'yes' else '❌'} {r['test']:8s} {r['variant']:30s} {r['seconds']:>7s}s {r['error']}")
        print(f"\nResults: {res['dir']}\nGrid video: {res['grid'] or '(no lip-sync results)'}\nOrder: {res['order']}")
        return 0
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout),
                                  RotatingFileHandler(cfg.path("06_logs") / "pipeline.log", maxBytes=5_000_000,
                                                      backupCount=5, encoding="utf-8")])
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
