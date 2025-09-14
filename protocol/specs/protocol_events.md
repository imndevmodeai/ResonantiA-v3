# Protocol Events (v3.5‑GP)

Purpose
- Define standard events emitted by engines, registries, and tools for observability and automation.

Event Envelope
```json
{
  "event": "string",
  "ts": "iso-datetime",
  "run_id": "string",
  "workflow": "string",
  "task_id": "string|null",
  "severity": "info|warn|error",
  "payload": {}
}
```

Core Events
- `workflow.started` – payload: { "name": "...", "start_tasks": ["..."] }
- `workflow.completed` – payload: { "status": "...", "duration_ms": 0 }
- `task.queued` – payload: { "task_id": "...", "deps": ["..."] }
- `task.started` – payload: { "task_id": "...", "action_type": "..." }
- `task.completed` – payload: { "task_id": "...", "status": "ok|error|skipped", "confidence": 0.0 }
- `task.retried` – payload: { "task_id": "...", "attempt": 2 }
- `task.failed` – payload: { "task_id": "...", "error_code": "RES-ERR-XXXX" }
- `phasegate.evaluated` – payload: { "gate_id": "...", "result": "pass|block" }
- `iar.synthesized` – payload: { "task_id": "..." }

New Events (v3.5‑GP live)
- `context.bundle.created` – payload: { "spr_id": "...", "term": "..." }
- `context.bundle.merged` – payload: { "spr_index": ["..."] }
- `iar.validation.failed` – payload: { "task_id": "...", "issues": ["..."] }
- `state.persisted` – payload: { "facts_count": 0, "digests_count": 0 }
- `prefetch.queue.enqueued` – payload: { "count": 0 }
- `sirc.autorun.started` – payload: { "reason": "complex_intent", "hint": "..." }
- `sirc.autorun.completed` – payload: { "clarity_score": 0.0 }
- `digest.flux_built` – payload: { "effects_count": 0 }

Transport
- Default: structured logs to `logs/`.
- Optional: WebSocket/HTTP bridge (see `visual_debug_bridges.md`).

Retention
- Minimum: per‑run rolling logs.
- Recommended: append‑only store for audits.

Traceability
- Chronicle: Events & Bridges.
- Code: `Three_PointO_ArchE/workflow_engine.py`.
