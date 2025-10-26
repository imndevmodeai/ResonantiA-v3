import json
import os
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from pathlib import Path
from typing import Dict, Any

try:
    from .config import get_config
except Exception:  # pragma: no cover - fallback for standalone
    def get_config():
        class _P:
            class paths:
                project_root = Path(os.getcwd())
        return _P()


def _state_path() -> Path:
    cfg = get_config()
    return Path(getattr(cfg.paths, "project_root", Path(os.getcwd()))) / "session_state.json"


def load_session_state() -> Dict[str, Any]:
    """Load session_state.json, ensuring required keys exist."""
    path = _state_path()
    if not path.exists():
        return {"facts_ledger": [], "updated_at": now_iso() + "Z"}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("facts_ledger", [])
    data["updated_at"] = now_iso() + "Z"
    return data


def save_session_state(state: Dict[str, Any]) -> None:
    """Persist the provided state to session_state.json safely."""
    path = _state_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception:
        # Best-effort persistence; do not throw inside engine
        pass


def append_fact(state: Dict[str, Any], fact: Dict[str, Any]) -> None:
    """Append an atomic fact into facts_ledger with timestamp."""
    if not isinstance(state.get("facts_ledger"), list):
        state["facts_ledger"] = []
    entry = {**fact}
    entry.setdefault("ts", now_iso() + "Z")
    state["facts_ledger"].append(entry)
    state["updated_at"] = now_iso() + "Z"


