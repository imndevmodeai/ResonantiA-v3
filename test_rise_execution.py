import sys
import os
import json
from pathlib import Path

def setup_paths():
    """Add project directories to Python's path."""
    project_root = Path(__file__).resolve().parent
    sys.path.insert(0, str(project_root))
    
    # Also add the package directory if it's not the same as root
    package_dir = project_root / 'Three_PointO_ArchE'
    if package_dir.exists() and str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))

def main():
    """Set up environment and run the RISE workflow."""
    setup_paths()
    
    try:
        from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator
    except ImportError as e:
        print(f"ERR_IMPORT: Could not import RISE_Orchestrator: {e}")
        print("\nPython Path:")
        for p in sys.path:
            print(f"- {p}")
        sys.exit(1)

    problem = os.environ.get('RISE_PROBLEM') or "Develop a comprehensive framework for ethically aligning and auditing distributed, autonomous AI systems operating in high-stakes environments like critical infrastructure or global finance. The framework must address emergent behaviors, ensure robust value alignment, and provide transparent, verifiable reporting mechanisms for human oversight, while being computationally efficient."

    print("🚀 Initializing RISE Orchestrator...")
    try:
        workflows_path = os.path.join(Path(__file__).resolve().parent, "archemuliplied", "workflows")
        orchestrator = RISE_Orchestrator(workflows_dir=workflows_path)
        print("✅ Orchestrator initialized successfully.")
        
        print(f"\n🧠 Running RISE workflow with problem:\n   '{problem[:100]}...'")
        result = orchestrator.run_rise_workflow(problem)
        
        print("\n🎉 RISE Workflow Completed.")
        
        # A more detailed summary can be printed here if needed
        summary = {
            "session_id": result.get("session_id"),
            "status": result.get("execution_status"),
            "total_duration": result.get("total_duration"),
            "final_strategy_present": bool(result.get("final_strategy"))
        }
        print("\n📊 Summary:")
        print('RISE_RUN_SUMMARY=' + json.dumps(summary, indent=2))

    except Exception as e:
        print(f"\n❌ ERR_RUN: An error occurred during the RISE workflow execution:\n {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)

if __name__ == "__main__":
    main()
