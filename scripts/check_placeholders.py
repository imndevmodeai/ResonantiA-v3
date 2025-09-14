import os
import re
import sys

# Regex to find common placeholder variants.
# This looks for lines containing "existing code" with variations of "..." before or after.
PLACEHOLDER_REGEX = re.compile(r"(\.\.\.\s*existing code\s*\.\.\.|# \.\.\. existing code \.\.\.|// \.\.\. existing code \.\.\.|\/\* \.\.\. existing code \.\.\. \*\/)")

# File extensions to check. Add any other relevant source code extensions.
CODE_EXTENSIONS = {'.py', '.js', '.ts', '.md', '.json', '.sh', '.css', '.html'}

# Directories to exclude from the scan.
EXCLUDE_DIRS = {'node_modules', '.venv', '.git', '__pycache__', 'dist', 'build', '.next'}

def scan_for_placeholders(start_dir):
    """
    Scans the specified directory for files containing placeholder text.

    Args:
        start_dir (str): The root directory to start scanning from.

    Returns:
        list: A list of file paths that contain placeholders.
    """
    flagged_files = []
    for root, dirs, files in os.walk(start_dir, topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in CODE_EXTENSIONS):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if PLACEHOLDER_REGEX.search(content):
                            flagged_files.append(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}", file=sys.stderr)
    return flagged_files

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print(f"Scanning for placeholder text in: {project_root}")
    
    leaked_files = scan_for_placeholders(project_root)
    
    if leaked_files:
        print("\n[ERROR] Placeholder text detected in the following files:", file=sys.stderr)
        for file_path in leaked_files:
            print(f"  - {file_path}", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n[SUCCESS] No placeholder text found. Code is clean.")
        sys.exit(0)
