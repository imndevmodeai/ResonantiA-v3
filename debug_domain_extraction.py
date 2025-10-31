#!/usr/bin/env python3
"""
Debug script to test domain extraction workflow
"""

import sys
import os
import json
import logging

# Add the project root to the path
sys.path.insert(0, os.path.abspath('.'))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_domain_extraction():
    """Test the domain extraction workflow with a simple example"""
    
    # Create workflow engine
    engine = IARCompliantWorkflowEngine()
    
    # Test problem description
    test_problem = "I am the CEO of a publicly traded pharmaceutical company. We have developed a life-saving drug that could help millions, but our pricing strategy is under intense scrutiny."
    
    # Create a simple test workflow that mimics the problematic parts
    test_workflow = {
        "name": "Domain Extraction Debug",
        "description": "Test workflow to debug domain extraction",
        "version": "1.0",
        "tasks": {
            "deconstruct_problem": {
                "action_type": "generate_text_llm",
                "description": "Deconstruct the problem into core components",
                "inputs": {
                    "prompt": f"Analyze the following problem and deconstruct it into core components:\n\n{test_problem}\n\nIdentify:\n1. Core domain areas\n2. Key variables and unknowns\n3. Strategic requirements\n4. Risk factors\n5. Success criteria\n\nOutput your analysis as a structured JSON object with a key 'deconstruction_text'.",
                    "model": "gemini-1.5-flash-latest",
                    "max_tokens": 2000,
                    "temperature": 0.3
                },
                "dependencies": []
            },
            "extract_domain_from_deconstruction": {
                "action_type": "generate_text_llm",
                "description": "Extract the primary domain from the deconstruction analysis",
                "inputs": {
                    "prompt": "From the following JSON analysis, identify and extract only the single, most relevant 'Core domain area'. Your output must be a single, clean JSON object with one key: 'domain'. For example: {\"domain\": \"Artificial Intelligence Strategy\"}\n\nAnalysis:\n{{deconstruct_problem.output}}",
                    "model": "gemini-1.5-flash-latest",
                    "max_tokens": 100,
                    "temperature": 0.1
                },
                "dependencies": ["deconstruct_problem"]
            },
            "debug_domain_output": {
                "action_type": "execute_code",
                "description": "Debug the domain output",
                "inputs": {
                    "language": "python",
                    "code": "import json\nprint('=== DEBUG DOMAIN OUTPUT ===')\nprint('Raw domain task result:')\nprint(repr({{extract_domain_from_deconstruction}}))\nprint('\\nDomain output field:')\nprint(repr({{extract_domain_from_deconstruction.output}}))\nprint('\\nTrying to access domain field:')\ntry:\n    domain_value = {{extract_domain_from_deconstruction.output.domain}}\n    print(f'Domain value: {repr(domain_value)}')\nexcept Exception as e:\n    print(f'Error accessing domain: {e}')\nprint('=== END DEBUG ===')"
                },
                "dependencies": ["extract_domain_from_deconstruction"]
            }
        }
    }
    
    # Save the test workflow
    with open('debug_domain_workflow.json', 'w') as f:
        json.dump(test_workflow, f, indent=2)
    
    print("Created debug_domain_workflow.json")
    
    # Run the workflow
    try:
        result = engine.run_workflow('debug_domain_workflow.json', {
            'problem_description': test_problem
        })
        
        print("\n=== WORKFLOW RESULT ===")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_domain_extraction()