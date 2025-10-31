# Vetting Agent

Source spec: ../specifications/vetting_agent.md

## Purpose
Guardian of validation: logical, ethical, scope-aware vetting with IAR integration.

## API (Conceptual)
- perform_scope_limitation_assessment(objective, current_thought, action_inputs, context) -> dict
- format_vetting_prompt(objective, previous_result, current_thought, current_action, action_inputs, prompt_template=None) -> str
- validate_workflow_step(step_data, previous_step_result, context) -> dict

## Inputs
- objective: str
- previous_result: dict|any (must include IAR when available)
- current_thought: str
- current_action: str
- action_inputs: dict
- context: dict (risk tolerance, high_stakes, sandbox flags, etc.)

## Outputs
- JSON assessment per spec (vetting_summary, checks, scope_limitation_assessment, overall_recommendation, confidence)

## Integration
- RISE Phases C/D (high_stakes_vetting.json)
- Workflow Engine step validation
- IAR enhancement pipeline

## Examples
See specifications/vetting_agent.md for templates and examples.
