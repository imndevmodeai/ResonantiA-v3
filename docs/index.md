# ArchE Documentation Index

Use these docs for contributor onboarding, protocol reference, and quick linking in prompts or logs. You can reference any page with an at-path like @docs/<relative_path> (e.g., @docs/components/vetting_agent.md).

## Start Here (v3.5‑GP)
- Chronicle: `../protocol/ResonantiA_Protocol_v3.5-GP_Canonical.md`
- Spec Suite: `../protocol/specs/`

## Structure
- docs/index.md — this index
- docs/spr_format_rules.md — Guardian Points and SPR rules
- docs/components/ — component-level docs (runtime modules/tools)
- docs/workflows/ — workflow specs and guides

## Key Components
- Vetting Agent — @docs/components/vetting_agent.md
- RISE Orchestrator — @docs/components/rise_orchestrator.md
- Workflow Engine — @docs/components/workflow_engine.md
- Action Registry — @docs/components/action_registry.md
- SPR Manager — @docs/components/spr_manager.md

## Conventions (CRDSP)
- Any code change that affects a component must update its doc page in the same PR.
- Cross-link using relative paths (e.g., ../specifications/vetting_agent.md).
- Keep an API section (Inputs, Outputs, Examples) and an Integration section for each component.
