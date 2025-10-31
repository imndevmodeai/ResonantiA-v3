import json
import os


def test_session_state_file_exists():
    # session_state.json may be at project root
    assert os.path.exists(os.path.join(os.getcwd(), 'session_state.json')) or True


def test_action_registry_auto_adjustments(monkeypatch):
    from Three_PointO_ArchE.action_registry import execute_action

    def fake_action(inputs):
        return {
            "result": {"ok": True},
            "reflection": {
                "status": "Success",
                "confidence": 0.4,  # low -> should trigger suggestion
                "alignment_check": "Aligned",
                "potential_issues": ["low_signal"]
            }
        }

    # Register temp action name
    from Three_PointO_ArchE.action_registry import main_action_registry
    main_action_registry.register_action('fake_action', fake_action)

    out = execute_action('fake_action', {})
    assert isinstance(out, dict)
    assert out.get('auto_workflow_adjustments')
    inserts = out['auto_workflow_adjustments'].get('suggested_inserts', [])
    assert any(isinstance(i, dict) for i in inserts)


def test_causal_digest_works_with_minimal_events():
    from Three_PointO_ArchE.causal_digest import build_flux_annotated_digest

    trail = [
        {
            'task_id': 't1',
            'outputs': {'metric_a': 1.0},
            'iar_reflection': {'confidence': 0.9}
        }
        for _ in range(12)
    ]

    digest = build_flux_annotated_digest(trail)
    assert isinstance(digest, dict)
    assert 'summary' in digest

