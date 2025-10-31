import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def _extract_candidates_from_bundle(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Heuristically extract prefetch candidates from a single context bundle.

    Returns a list of candidate descriptors, e.g., file refs or keyword topics.
    """
    candidates: List[Dict[str, Any]] = []
    if not isinstance(bundle, dict):
        return candidates

    # Blueprint details may include module paths or conceptual anchors
    bp = bundle.get("blueprint_details") or ""
    if isinstance(bp, str) and bp:
        # Simple heuristics: file-like paths and keywords
        if ".py" in bp or "/" in bp:
            candidates.append({"type": "file_ref", "target": bp})
        # Add term/topic from bundle
        term = bundle.get("term") or bundle.get("spr_id")
        if term:
            candidates.append({"type": "topic", "keyword": str(term)})

    # Relationships may hint at related artifacts
    rel = bundle.get("relationships") or {}
    if isinstance(rel, dict):
        for k, v in rel.items():
            try:
                if isinstance(v, list):
                    for item in v:
                        candidates.append({"type": "relationship", "key": k, "value": str(item)})
                else:
                    candidates.append({"type": "relationship", "key": k, "value": str(v)})
            except Exception:
                continue

    return candidates


def prefetch_from_bundles(context_bundles: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Derive a prefetch queue from merged context bundles."""
    queue: List[Dict[str, Any]] = []
    if not isinstance(context_bundles, dict):
        return queue

    # The merged structure may contain an index and/or embedded bundles
    bundles = []
    if isinstance(context_bundles.get("bundles"), list):
        bundles = context_bundles.get("bundles")
    # Fallback: treat the structure itself as a single bundle if keys exist
    elif any(k in context_bundles for k in ("spr_id", "term", "blueprint_details")):
        bundles = [context_bundles]

    for b in bundles:
        queue.extend(_extract_candidates_from_bundle(b))

    return queue


def trigger_predictive_prefetch(session_state: Dict[str, Any], initial_context: Dict[str, Any]) -> None:
    """Populate session_state.prefetch_queue based on current context.

    Non-blocking heuristic: we only compute candidates and enqueue them. Actual
    retrieval/downloading is left to dedicated actions to avoid blocking the engine.
    """
    try:
        context_bundles = initial_context.get("context_bundles") or {}
        queue = prefetch_from_bundles(context_bundles)
        if not queue:
            return
        # Merge into session_state queue
        ss_queue = session_state.setdefault("prefetch_queue", [])
        # Deduplicate by tuple signature
        seen = {tuple(sorted((k, str(v)) for k, v in item.items())) for item in ss_queue}
        for item in queue:
            sig = tuple(sorted((k, str(v)) for k, v in item.items()))
            if sig not in seen:
                ss_queue.append(item)
                seen.add(sig)
        session_state["prefetch_queue_updated"] = True
        logger.debug(f"Predictive prefetch queued {len(queue)} candidates (total {len(ss_queue)}).")
    except Exception as e:
        logger.warning(f"Predictive prefetch failed to enqueue candidates: {e}")


