# Living Specification: Protocol & VCD Event Schema

Defines canonical JSON shapes emitted by the engine and processors for UI/logs; standardizes Phoenix observability.

## EnhancedMessage (Envelope)
```json
{
  "id":"uuid","content":"string","timestamp":"2025-08-08T12:34:56Z","sender":"user|arche",
  "message_type":"chat|iar|spr|temporal|meta|complex|implementation|protocol_init|error",
  "protocol_compliance":true,
  "protocol_version":"ResonantiA v3.1-CA",
  "iar": { "status":"ok|warn|error","confidence":0.92 },
  "spr_activations":[{"spr_id":"Cognitive resonancE","confidence":0.88}],
  "temporal_context": {"timeframe":"short","forecasts":{"metric":1.23}},
  "meta_cognitive_state": {"sirc_active":false,"shift_active":false},
  "complex_system_visioning": {"abm_summary":"string","indicators":{"gini":0.41}},
  "implementation_resonance": {"crdsp_pass":true,"docs_updated":true},
  "thought_trail":["string"],
  "protocol_init":{"session_id":"phoenix_123","version":"v3.1-CA"},
  "protocol_error":{"message":"string","error":"details","fallback_mode":true}
}
```

## VcdEvent (Timeline Atom)
```json
{
  "id":"uuid","t":1245,
  "type":"WorkflowStart|TaskEvaluation|TaskExecution|TaskSuccess|TaskFailure|WorkflowSuccess|WorkflowFailure|ThoughtTrail|IAR|SPR|Temporal|Meta|Complex|Implementation",
  "message":"string",
  "metadata":{"task_id":"deconstruct_code_blueprints","attempt":1},
  "severity":"info|success|warn|error"
}
```

## Emission Contract
- `emit_vcd_event(type, message, metadata?)` ⇒ single-line JSON `VcdEvent`.
- Task transitions: TaskEvaluation → TaskExecution → (TaskSuccess|TaskFailure).
- Workflow MUST emit WorkflowStart and terminal success/failure.

## IAR Embedding
- When action returns IAR, emit `VcdEvent` type `IAR` with confidence/issues; envelope MAY also embed.

## Errors
- Fallback: set `protocol_error.fallback_mode=true` and emit error/warn event.
- Exceptions: `WorkflowFailure` with `metadata.error` (truncated stack).

## Phoenix Markers
- `metadata.phase`: `ingest_spec|deconstruct_blueprints|generate_code|validate_integrity|first_sunrise`.

## Versioning & Security
- Include `protocol_version`; schema evolution: additive, optional fields.
- No secrets; cap event payload to ~8KB; UI truncates with expand.

## CRDSP Links
- Code: `Three_PointO_ArchE/workflow_engine.py`, `webSocketServer.js`.
- Specs: `workflow_engine.md`, `visual_cognitive_debugger_ui.md`, `autopoietic_genesis_protocol.md`.
