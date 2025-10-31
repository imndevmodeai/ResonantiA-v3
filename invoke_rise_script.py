import time
import sys
import os
import json

sys.path.insert(0, os.getcwd())

from Three_PointO_ArchE.code_executor import execute_code
from Three_PointO_ArchE.config import get_config
from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.spr_manager import SPRManager

def main():
    """
    Tests the code executor timeout functionality.
    """
    try:
        config = get_config()
        timeout = config.tools.code_executor_timeout

        print(f"--- Running timeout test with configured timeout: {timeout} seconds ---")

        code_to_run = """
import time
print("Starting long-running task...")
time.sleep(45)
print("Long-running task finished.")
"""

        result = execute_code({
            "code": code_to_run,
            "language": "python",
            "timeout": timeout
        })

        print("--- Test Result ---")
        import json
        print(json.dumps(result, indent=2))
        print("--- End of Test ---")
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()


