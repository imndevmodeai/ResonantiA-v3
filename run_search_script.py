import subprocess
import sys
import os

def main():
    if len(sys.argv) != 2:
        print("Usage: python run_search_script.py \"<query>\"", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    
    # Ensure the path to the script is correct, assuming this script is run from the project root
    script_path = "ResonantiA/browser_automation/search.js"
    output_path = "ResonantiA/browser_automation/workflow_search_results.json"
    
    if not os.path.exists(script_path):
        print(f"Error: Search script not found at {script_path}", file=sys.stderr)
        sys.exit(1)

    command = [
        "node",
        script_path,
        "--query", query,
        "--output", output_path,
        "--engine", "google"
    ]

    try:
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print("Search script executed successfully.")
        print("STDOUT:")
        print(result.stdout)
    except FileNotFoundError:
        print("Error: 'node' command not found. Please ensure Node.js is installed and in your PATH.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error executing search script. Return code: {e.returncode}", file=sys.stderr)
        print("STDERR:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 