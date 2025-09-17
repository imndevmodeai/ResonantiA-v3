#!/usr/bin/env python3
"""
Test template variable substitution in the workflow engine
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine


def test_template_substitution():
    """Test if template variables are being substituted correctly"""
    
    # Initialize the workflow engine
    engine = IARCompliantWorkflowEngine()
    
    # Test template substitution directly
    test_template = "Hello {{ problem_description }} world!"
    test_context = {
        "problem_description": "Test Problem"
    }
    
    print(f"Template: {test_template}")
    print(f"Context: {test_context}")
    
    # Use the same resolver path the engine uses during task execution
    resolved = engine._resolve_value(test_template, runtime_context={}, initial_context=test_context)
    print(f"Resolved: {resolved}")
    assert resolved == "Hello Test Problem world!", "Direct substitution via initial_context failed"

    # Also test embedded usage and fallback chain
    runtime_ctx = {
        "some_task": {"result": {"generated_text": "From Runtime"}}
    }
    tpl_embedded = "R: {{ some_task.result.generated_text }}, C: {{ problem_description }}"
    resolved2 = engine._resolve_value(tpl_embedded, runtime_ctx, test_context)
    print(f"Resolved Embedded: {resolved2}")
    assert resolved2 == "R: From Runtime, C: Test Problem", "Embedded/template fallback resolution failed"


if __name__ == "__main__":
    test_template_substitution()
    print("All template substitution tests passed.")
