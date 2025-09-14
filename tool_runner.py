import argparse
import json
import sys
import os

# Ensure the Three_PointO_ArchE directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Three_PointO_ArchE.action_registry import ACTION_REGISTRY

def main():
    """
    A direct tool runner for the ArchE system.
    Bypasses the WorkflowEngine to call tools directly from the registry.
    """
    parser = argparse.ArgumentParser(
        description="Directly execute a tool from the ArchE Action Registry.",
        usage="python3 tool_runner.py <tool_name> '<json_inputs>'"
    )
    parser.add_argument("tool_name", help="The name of the tool to execute (e.g., 'list_directory').")
    parser.add_argument("json_inputs", help="A JSON string representing the 'inputs' dictionary for the tool (e.g., '{\"directory\": \".\"}').")
    
    args = parser.parse_args()
    
    tool_name = args.tool_name
    
    # 1. Find the tool in the registry
    if tool_name not in ACTION_REGISTRY:
        print(f"Error: Tool '{tool_name}' not found in the Action Registry.")
        print("Available tools:", ", ".join(ACTION_REGISTRY.keys()))
        sys.exit(1)
        
    tool_function = ACTION_REGISTRY[tool_name]
    
    # 2. Parse the JSON inputs
    try:
        inputs = json.loads(args.json_inputs)
        if not isinstance(inputs, dict):
            raise TypeError("JSON inputs must decode to a dictionary.")
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error: Invalid JSON string for inputs: {e}")
        print("Please provide a valid JSON dictionary string, e.g., '{\"key\": \"value\"}'")
        sys.exit(1)
        
    # 3. Execute the tool
    print(f"-> Executing tool: '{tool_name}' with inputs: {inputs}")
    try:
        result = tool_function(**inputs)
        
        print("\\n---(Tool Result)---")
        print(json.dumps(result, indent=2, default=str))
        print("-------------------")
        
    except Exception as e:
        print(f"\\nAn unexpected error occurred while executing the tool: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 