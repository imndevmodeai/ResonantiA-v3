from typing import Dict, Any, List
from datetime import datetime

def create_context_bundle(spr_def: Dict[str, Any], runtime_context: Dict[str, Any], initial_context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a superpositioned context bundle from an SPR definition and current contexts.

    The bundle is a compact, mergeable unit that references blueprint_details and
    captures minimal state to rehydrate relevant context on demand.
    """
    spr_id = spr_def.get("spr_id")
    bundle = {
        "spr_id": spr_id,
        "term": spr_def.get("term"),
        "blueprint_details": spr_def.get("blueprint_details"),
        "relationships": spr_def.get("relationships", {}),
        "created_at": datetime.utcnow().isoformat() + "Z",
        "hints": {
            "initial_keys": list((initial_context or {}).keys())[:20],
            "recent_tasks": [k for k in (runtime_context or {}).keys() if k not in ("initial_context", "workflow_definition", "workflow_run_id")][-10:]
        }
    }
    return bundle

def merge_bundles(bundles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple bundles into a composite structure for diffusion into prompts/tools."""
    composite = {
        "spr_index": [b.get("spr_id") for b in bundles],
        "blueprints": [b.get("blueprint_details") for b in bundles if b.get("blueprint_details")],
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    return composite


