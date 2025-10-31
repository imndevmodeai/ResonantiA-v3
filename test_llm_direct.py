#!/usr/bin/env python3
"""
Direct test of the LLM tool to isolate the JSON parsing issue.
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Three_PointO_ArchE.llm_tool import generate_text_llm
from Three_PointO_ArchE.logging_config import setup_logging
import json

def main():
    setup_logging()
    print("=== Direct LLM Tool Test ===")
    
    # Test with a very simple prompt
    inputs = {
        "prompt": "Write a simple Python function called 'add_numbers' that takes two integers and returns their sum. Include a docstring. ONLY output the Python code, nothing else.",
        "model": "gemini-1.5-flash-latest",
        "temperature": 0.1,
        "max_tokens": 200,
        "encode_output_base64": False  # Don't encode to see raw output
    }
    
    print("Calling LLM with inputs:")
    print(json.dumps(inputs, indent=2))
    print("\n" + "="*50 + "\n")
    
    try:
        result = generate_text_llm(inputs)
        print("LLM Result:")
        print(json.dumps(result, indent=2, default=str))
        
        if "response_text" in result:
            print("\n" + "="*50)
            print("Generated Code:")
            print("="*50)
            print(result["response_text"])
            print("="*50)
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()