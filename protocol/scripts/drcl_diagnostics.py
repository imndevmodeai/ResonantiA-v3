import json
import os
from typing import Dict, Any

# Assume these paths are relative to the project root where this script is run
DRCL_SPEC_PATH = "protocol/Distributed_Resonant_Corrective_Loop.md"
DRCL_WORKFLOW_PATH = "Happier/workflows/distributed_resonant_corrective_loop.json"
DIAGNOSTIC_SPRS_PATH = "protocol/diagnostic_sprs.json"

def get_project_root():
    """Finds the project root by looking for a known artifact, e.g., '.git' or a specific file."""
    current_path = Path(__file__).resolve()
    while current_path != current_path.parent:
        if (current_path / '.git').exists() or (current_path / 'README.md').exists():
            return current_path
        current_path = current_path.parent
    return Path.cwd() # Fallback to current working directory

def generate_diagnostic_report() -> Dict[str, Any]:
    """
    Generates a 'magnetic image' of the system by checking for the
    presence and alignment of core DRCL artifacts.
    """
    report = {
        "report_id": "drcl_diagnostic_01",
        "timestamp": __import__('datetime').datetime.now().isoformat(),
        "summary": "DRCL Health Check",
        "components": {}
    }

    # 1. Check for the DRCL Specification
    spec_check = {
        "name": "DRCL Specification",
        "path": DRCL_SPEC_PATH,
        "status": "MISSING",
        "details": "The core specification file for the DRCL protocol is not found."
    }
    if os.path.exists(DRCL_SPEC_PATH):
        spec_check["status"] = "PRESENT"
        spec_check["details"] = "DRCL specification is in place."
    report["components"]["drcl_spec"] = spec_check

    # 2. Check for the DRCL Workflow
    workflow_check = {
        "name": "DRCL Executable Workflow",
        "path": DRCL_WORKFLOW_PATH,
        "status": "MISSING",
        "details": "The primary workflow file for executing the DRCL is not found."
    }
    if os.path.exists(DRCL_WORKFLOW_PATH):
        workflow_check["status"] = "PRESENT"
        workflow_check["details"] = "DRCL workflow is ready for execution."
    report["components"]["drcl_workflow"] = workflow_check

    # 3. Check for Diagnostic SPRs
    spr_check = {
        "name": "Diagnostic SPR Definitions",
        "path": DIAGNOSTIC_SPRS_PATH,
        "status": "MISSING",
        "details": "The diagnostic SPR definitions file is not found."
    }
    if os.path.exists(DIAGNOSTIC_SPRS_PATH):
        spr_check["status"] = "PRESENT"
        spr_check["details"] = "Diagnostic SPRs are available for analysis."
    report["components"]["diagnostic_sprs"] = spr_check
    
    # --- Overall Resonance Assessment ---
    component_statuses = [c["status"] for c in report["components"].values()]
    if all(s == "PRESENT" for s in component_statuses):
        report["overall_resonance"] = "HEALTHY"
        report["recommendation"] = "All core DRCL components are present. The system is ready to use this diagnostic query to analyze its own state."
    else:
        report["overall_resonance"] = "DEGRADED"
        report["recommendation"] = "One or more core DRCL components are missing. The 'magnetic image' is incomplete. Restore the missing files to regain full diagnostic capability."

    return report

if __name__ == "__main__":
    from pathlib import Path
    
    # Change CWD to project root for the script to work from anywhere
    project_root = get_project_root()
    os.chdir(project_root)
    
    diagnostic_report = generate_diagnostic_report()
    print(json.dumps(diagnostic_report, indent=2))
