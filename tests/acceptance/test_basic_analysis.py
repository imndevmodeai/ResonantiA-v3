"""
Spec links:
- Chronicle: v3.5‑GP Chronicle → Mind Forge → WorkflowEnginE
- Spec: protocol/specs/protocol_events.md
- Workflow: workflows/basic_analysis.json
"""
import json
import os


def test_workflow_file_exists():
	assert os.path.exists('workflows/basic_analysis.json')


def test_workflow_has_tasks():
	with open('workflows/basic_analysis.json', 'r', encoding='utf-8') as f:
		wf = json.load(f)
	assert 'tasks' in wf and isinstance(wf['tasks'], dict) and len(wf['tasks']) > 0
	# Minimal contract: start task and a search task present
	assert any(t for t in wf['tasks'].values() if t.get('action_type') == 'search_web')
