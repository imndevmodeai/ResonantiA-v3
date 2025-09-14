from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

try:
    from .sirc_intake_handler import SIRCIntakeHandler
    from .spr_manager import SPRManager
except Exception:  # pragma: no cover
    SIRCIntakeHandler = None  # type: ignore
    SPRManager = None  # type: ignore


COMPLEX_INTENT_KEYWORDS = {
    'strategy', 'roadmap', 'vision', 'architecture', 'design', 'framework',
    'orchestrator', 'autonomous', 'integration', 'protocol', 'resonance'
}


def _looks_complex_intent(text: str) -> bool:
    """Heuristic to detect complex intent for autonomous SIRC."""
    if not text:
        return False
    lower = text.lower()
    if len(lower.split()) >= 18:
        return True
    if any(k in lower for k in COMPLEX_INTENT_KEYWORDS):
        return True
    return False


def maybe_autorun_sirc(initial_context: Dict[str, Any], spr_manager: Any = None) -> Dict[str, Any]:
    """Detect complex intent and run SIRC intake autonomously.

    Adds a 'sirc' section to context with finalized_objective and clarity_score.
    No-op if SIRCIntakeHandler is unavailable or heuristics do not trigger.
    """
    try:
        if not initial_context.get('auto_sirc', True):
            return initial_context

        user_query = initial_context.get('user_query') or initial_context.get('prime_text') or ''
        if not _looks_complex_intent(user_query):
            return initial_context

        if SIRCIntakeHandler is None:
            logger.warning("SIRCIntakeHandler unavailable; skipping autonomous SIRC")
            return initial_context

        handler = SIRCIntakeHandler(spr_manager=spr_manager) if spr_manager else SIRCIntakeHandler()
        result = handler.process_directive(user_query)
        initial_context.setdefault('sirc', {})
        initial_context['sirc'].update({
            'finalized_objective': result.get('finalized_objective'),
            'clarity_score': result.get('clarity_score'),
            'clarification_needed': result.get('clarification_needed'),
            'bypass_reason': result.get('bypass_reason')
        })
        # Promote finalized objective to guide subsequent retrieval and planning
        if result.get('finalized_objective'):
            initial_context['refined_objective'] = result['finalized_objective']
        logger.info("[SIRC-AUTO] Finalized objective: %s", initial_context['sirc']['finalized_objective'])
        return initial_context
    except Exception as e:  # pragma: no cover
        logger.error("Autonomous SIRC failed: %s", e, exc_info=True)
        return initial_context


