# Contracts and Schemas (v3.5‑GP)

Purpose
- Canonicalize action, task, workflow, IAR, and error contracts across engines and tools.
- Provide machine‑verifiable JSON examples aligned to current code paths.

References
- Engine: `Three_PointO_ArchE/workflow_engine.py`
- Chaining/IAR: `Three_PointO_ArchE/workflow_chaining_engine.py`
- Actions: `Three_PointO_ArchE/action_registry.py`
- SPRs: `Three_PointO_ArchE/spr_manager.py`, `knowledge_graph/spr_definitions_tv.json`

Live modules (So BeloW)
- State: `Three_PointO_ArchE/session_state_manager.py`
- Context Bundles: `Three_PointO_ArchE/context_superposition.py`
- Retrieval Modulation: `Three_PointO_ArchE/enhanced_perception_engine.py`
- Predictive Prefetch: `Three_PointO_ArchE/prefetch_manager.py`
- Autonomous SIRC: `Three_PointO_ArchE/sirc_autonomy.py`
- Causal Digest: `Three_PointO_ArchE/causal_digest.py`

### Guiding Principle — “Code is a lossy projection”
- Single Source of Truth: executable specifications describe intent, constraints, and contracts; code implements and emits events against them.
- Loss minimizers in this repository:
  1) Standard Schemas (IAR/Task/Workflow/Event) encode semantics beyond code shapes.
  2) Protocol Events provide an observable API surface for runtime behavior.
  3) IAR validation + phase‑gates enforce constraints at runtime, catching drift early.
  4) Acceptance Tests assert behavior; failures signal divergence from the spec.
  5) Executable Spec Parser (spec → artifacts) keeps narrative/contracts and code in lockstep.
  6) Chronicle ↔ Spec ↔ Code cross‑references provide bi‑directional traceability.

## 1. Integrated Action Reflection (IAR) Envelope

Every action result MUST include an IAR envelope (engine may synthesize if absent).

```json
{
  "status": "ok|error|skipped",
  "confidence": 0.0,
  "alignment_check": "pass|concern|fail",
  "potential_issues": ["string"],
  "telemetry": {"duration_ms": 0, "retries": 0, "attempt": 1}
}
```

## 2. Action Result Schema

```json
{
  "error": null,
  "data": {},
  "reflection": {"status": "ok", "confidence": 0.7, "alignment_check": "pass", "potential_issues": []}
}
```

- error: null or Error Object (see §4).
- data: domain payload (tool specific).
- reflection: IAR envelope.

### 2.1 LLM Action
```json
{
  "error": null,
  "data": {"text": "string", "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}, "model": "string"},
  "reflection": {"status": "ok", "confidence": 0.62, "alignment_check": "pass", "potential_issues": []}
}
```

### 2.2 Search Action
```json
{
  "error": null,
  "data": {"results": [{"title": "...", "url": "...", "snippet": "..."}], "provider": "serpapi|simulated_google"},
  "reflection": {"status": "ok", "confidence": 0.55, "alignment_check": "pass", "potential_issues": ["simulated_provider"]}
}
```

### 2.3 Code Execution
```json
{
  "error": null,
  "data": {"stdout": "...", "stderr": "", "artifacts": []},
  "reflection": {"status": "ok", "confidence": 0.8, "alignment_check": "pass", "potential_issues": []}
}
```

## 3. Task Record

```json
{
  "task_id": "string",
  "action_type": "string",
  "description": "string",
  "inputs_resolved": {},
  "result": {"error": null, "data": {}, "reflection": {}},
  "started_at": "iso-datetime",
  "finished_at": "iso-datetime",
  "attempts": 1,
  "dependencies": ["task_id"],
  "condition": "string|null"
}
```

## 4. Error Object and Codes

```json
{
  "code": "RES-ERR-XXXX",
  "message": "human readable",
  "details": {"provider": "...", "hint": "..."}
}
```

- Code families are defined in `compliance_and_error_codes.md`.

## 5. Workflow Definition Addenda

- Required fields: `name`, `description`, `tasks`.
- Optional: `start_tasks`, `phase_gates`, `policies`.

## 6. Backward Compatibility

- Engines MUST tolerate missing IAR by synthesizing minimal envelopes.
- Unknown fields are ignored but preserved when possible.

## 7. Validation

- JSON Schema drafts can be layered later; start with example‑first tests in `tests/`.

## 8. New Schemas (v3.5‑GP live)

### 8.1 Session State
```json
{
  "facts_ledger": [
    {"task": "string", "status": "success|error|skipped", "confidence": 0.0, "ts": "iso-datetime"}
  ],
  "digests": [
    {"type": "flux", "summary": "string", "causal": {"effects": []}, "ts": "iso-datetime"}
  ],
  "prefetch_queue": [
    {"type": "file_ref|topic|url", "target": "string", "priority": 1}
  ],
  "updated_at": "iso-datetime"
}
```

### 8.2 Context Bundles (Superposition)
```json
{
  "spr_id": "WorkflowEnginE",
  "term": "Workflow Engine",
  "blueprint_details": "path/or ref",
  "relationships": {"part_of": ["Mind Forge"]},
  "created_at": "iso-datetime",
  "hints": {"keywords": ["IAR", "phase-gate"], "files": ["Three_PointO_ArchE/workflow_engine.py"]}
}
```
Merged index returned to context:
```json
{ "spr_index": ["WorkflowEnginE", "ComparativE FluxuaL ProcessinG"] }
```

### 8.3 Retrieval Modulation
```json
{
  "pinned_policy_terms": ["IAR", "phase-gate", "SPR"],
  "weight": 1.2
}
```

### 8.4 Predictive Prefetch Queue Item
```json
{ "type": "topic", "target": "IAR validation", "priority": 2 }
```

### 8.5 Auto Workflow Adjustments (Action Registry hint)
```json
{
  "auto_workflow_adjustments": {
    "suggested_inserts": [
      {"after_task": "task_id", "action": "vetting_agent.run", "reason": "low confidence"}
    ]
  }
}
```

### 8.6 SIRC Finalized Objective (Context)
```json
{
  "sirc": {
    "finalized_objective": "Design retrieval-weight modulation",
    "clarity_score": 0.91
  }
}
```

---

Traceability
- Chronicle: v3.5‑GP Chronicle → Contracts and Schemas.
- Code: engine/registry modules cited above.
