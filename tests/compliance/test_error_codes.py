"""
Spec links:
- Spec: protocol/specs/compliance_and_error_codes.md
- Spec: protocol/specs/contracts_and_schemas.md
"""
import os


def test_error_codes_spec_exists():
	assert os.path.exists('protocol/specs/compliance_and_error_codes.md')


def test_contracts_spec_exists():
	assert os.path.exists('protocol/specs/contracts_and_schemas.md')
