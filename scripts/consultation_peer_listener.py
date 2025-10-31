#!/usr/bin/env python3
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consultation_peer_listener")

OUTBOX_DIR = Path("consultation_outbox")
INBOX_DIR = Path("consultation_inbox")


def process_broadcast(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Very simple peer responder that suggests a resolution by echoing
    the abstracted intent and proposing a generic remediation.
    Replace with project-aware lookup or remote registry in production.
    """
    abstracted = payload.get("abstracted_intent", {})
    flawed = payload.get("flawed_map", {})

    suggestion = {
        "type": "consultation_response",
        "context_task_id": payload.get("context_task_id"),
        "proposed_fix": {
            "note": "Peer suggests verifying artifact existence and updating workflow registry.",
            "dissonance_kind": flawed.get("dissonance_kind"),
            "failed_artifact": flawed.get("failed_artifact"),
            "candidate_sprs": abstracted.get("primed_sprs", []),
        },
        "meta": {
            "confidence": 0.55,
            "source": "local_peer_listener_stub"
        }
    }
    return suggestion


def main() -> None:
    OUTBOX_DIR.mkdir(parents=True, exist_ok=True)
    INBOX_DIR.mkdir(parents=True, exist_ok=True)

    logger.info("Peer listener active. Watching %s", OUTBOX_DIR)
    seen: set[str] = set()
    while True:
        for p in sorted(OUTBOX_DIR.glob("consult_*.json")):
            if p.name in seen:
                continue
            try:
                with p.open("r", encoding="utf-8") as f:
                    payload = json.load(f)
                resp = process_broadcast(payload)
                # write response alongside
                resp_path = INBOX_DIR / p.name.replace("consult_", "response_")
                with resp_path.open("w", encoding="utf-8") as f:
                    json.dump(resp, f, indent=2)
                logger.info("Responded to %s -> %s", p.name, resp_path.name)
                seen.add(p.name)
            except Exception as e:
                logger.warning("Failed processing %s: %s", p, e, exc_info=True)
        time.sleep(1.0)


if __name__ == "__main__":
    main()


