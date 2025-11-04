from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

try:
    from .causal_inference_tool import perform_causal_inference
except Exception:  # pragma: no cover
    def perform_causal_inference(operation: str, data=None, **kwargs):  # type: ignore
        return {"error": "causal tool unavailable"}

try:
    from .causal_parameter_extractor import extract_causal_parameters
except Exception:  # pragma: no cover
    def extract_causal_parameters(query=None, data=None, **kwargs):  # type: ignore
        return {"treatment": "unknown_treatment", "outcome": "unknown_outcome", "confidence": 0.1}


def build_flux_annotated_digest(raw_events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a flux-annotated digest from raw ThoughtTraiL or logs.

    This preserves causal links by estimating treatment->outcome effects
    across observed variables, then encodes them alongside a compact
    narrative digest suitable for session_state facts_ledger.
    """
    try:
        # Extract simple tabular data if present
        rows: List[Dict[str, Any]] = []
        for ev in raw_events[:500]:  # cap for safety
            row = {}
            ref = ev.get('iar_reflection') or {}
            out = ev.get('outputs') or {}
            if isinstance(out, dict):
                for k, v in out.items():
                    if isinstance(v, (int, float)):
                        row[k] = v
            if 'confidence' in ref and isinstance(ref['confidence'], (int, float)):
                row['iar_confidence'] = ref['confidence']
            if row:
                rows.append(row)

        digest = {
            'summary': f"digested {len(raw_events)} events; numeric_rows={len(rows)}",
            'events_sample': [e.get('task_id') for e in raw_events[:10]],
        }

        if len(rows) >= 10:
            # Try a simple causal estimate if we have enough numeric rows
            data = {}
            # flatten numeric columns into arrays per key
            keys = set().union(*[r.keys() for r in rows])
            for k in keys:
                data[k] = [r.get(k) for r in rows if k in r]

            # Dynamic extraction: Use universal abstraction to extract treatment/outcome
            # This replaces the hardcoded heuristic with query-relative extraction
            num_keys = [k for k in keys if k != 'iar_confidence']
            if len(num_keys) >= 2:
                # Extract causal parameters from data structure
                # The extractor will intelligently identify treatment/outcome from the data
                causal_params = extract_causal_parameters(data=data)
                
                treatment = causal_params.get('treatment', num_keys[0] if num_keys else 'unknown')
                outcome = causal_params.get('outcome', num_keys[1] if len(num_keys) > 1 else 'unknown')
                confounders = causal_params.get('confounders', [])
                
                # If extraction didn't provide confounders, use remaining keys
                if not confounders and len(num_keys) > 2:
                    confounders = [k for k in num_keys[2:5] if k not in [treatment, outcome]]
                
                ci_res = perform_causal_inference(
                    operation='estimate_effect',
                    data=data,
                    treatment=treatment,
                    outcome=outcome,
                    confounders=confounders
                )
                digest['causal'] = {
                    'treatment': treatment,
                    'outcome': outcome,
                    'effect': ci_res.get('causal_effect'),
                    'ci': ci_res.get('confidence_intervals'),
                    'p_value': ci_res.get('p_value')
                }

        return digest
    except Exception as e:  # pragma: no cover
        logger.error("Failed to build flux-annotated digest: %s", e, exc_info=True)
        return {'summary': 'digest_failed', 'error': str(e)}


