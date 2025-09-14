"""
Spec links:
- Spec: protocol/specs/protocol_events.md
"""
import os


def test_protocol_events_spec_exists():
	assert os.path.exists('protocol/specs/protocol_events.md')
