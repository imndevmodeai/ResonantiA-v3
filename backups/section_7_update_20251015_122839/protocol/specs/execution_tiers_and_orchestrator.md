# Execution Tiers and Orchestrator (v3.5‑GP)

Scope
- Define ACO (fast path) vs RISE (deep path) handoff, IAR thresholds, and escalation rules.

Tiers
- Tier 0: No‑op/pass‑through (routing only)
- Tier 1: ACO (domain controllers, pattern cache)
- Tier 2: ACO+LLM (single‑tool expansions)
- Tier 3: RISE (multi‑step workflows)
- Tier 4: RISE+Vetting (High‑stakes vetting & SIRC)

Escalation Triggers
- `confidence < τ_conf` (default 0.65)
- multi‑tool requirements detected
- policy/ethics risk flagged
- repeated failure/loop detected

Handoff Contract
```json
{
  "from": "aco|rise",
  "to": "aco|rise",
  "reason": "string",
  "context": {"user_query": "...", "signals": {"confidence": 0.52}}
}
```

Files
- `Three_PointO_ArchE/adaptive_cognitive_orchestrator.py`
- `Three_PointO_ArchE/rise_orchestrator.py`

Autonomous SIRC (live integration)
- Trigger heuristics: complex intent (length/keywords), confidence volatility, repeated phase‑gate blocks.
- Intake: `Three_PointO_ArchE/sirc_autonomy.py` detects and invokes `sirc_intake_handler`.
- Output: context.sirc.finalized_objective + clarity_score; events `sirc.autorun.started/completed`.

Retrieval Weight Modulation & Prefetch
- Retrieval layer receives `initial_context.retrieval_modulation.pinned_policy_terms` to adjust scores.
- Prefetch manager derives `prefetch_queue` from context bundles; event `prefetch.queue.enqueued`.

IAR Policy
- ACO: lightweight envelope OK, must log controller and rationale.
- RISE: full envelope required per task.
