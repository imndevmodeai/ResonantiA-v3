# Acceptance Tests (v3.5‑GP)

Scope
- Define behavior‑level tests for workflows and events; link each test to spec section.

Conventions
- Tests under `tests/acceptance/` mirror workflow names.
- Each test declares links: Chronicle section, spec file, workflow file.

Minimal Template
```python
# tests/acceptance/test_basic_analysis.py
"""
Spec links:
- Chronicle: v3.5‑GP Chronicle → Mind Forge → WorkflowEnginE
- Spec: protocol/specs/protocol_events.md
- Workflow: workflows/basic_analysis.json
"""
import json
import os

def test_workflow_exists():
    assert os.path.exists('workflows/basic_analysis.json')
```

Additional Criteria (v3.5‑GP live)
- Session State: after a successful task, `session_state.json` contains new facts_ledger entry; emit `state.persisted`.
- IAR Enforcement: engine rejects missing/malformed IAR with `iar.validation.failed` event.
- Context Bundles: when SPRs are primed, bundles are created/merged; emit `context.bundle.*` events.
- Autonomous SIRC: complex intent triggers autorun; context contains `sirc.finalized_objective` and `clarity_score`.
- Prefetch: upon bundle merge, `prefetch_queue` is populated; emit `prefetch.queue.enqueued`.
- Flux Digest: building a digest yields `digest.flux_built` event with non‑empty effects list.
