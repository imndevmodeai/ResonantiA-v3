# RISE Orchestrator

Entry: Three_PointO_ArchE/rise_orchestrator.py

## Responsibilities
- Phase A/B/C/D orchestration
- SPR pre-detection for prompts
- Axiomatic knowledge activation via Vetting Agent hooks

## Inputs/Outputs
- Input: problem_description (str)
- Output: final_strategy, spr_definition, execution_metrics, history

## Integration
- Uses workflows/knowledge_scaffolding*.json, strategy_fusion.json, high_stakes_vetting.json, distill_spr.json
- Calls vetting_prompts.perform_scope_limitation_assessment

