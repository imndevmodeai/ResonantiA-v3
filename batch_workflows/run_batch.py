import json
import sys
import time
from pathlib import Path
import subprocess
from datetime import datetime

WORKFLOW = "workflows/gorilla_scenario_abm_narrative_workflow.json"
CONTEXT_DIR = Path("contexts/batch_runs")
CONTEXT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS = []

def run_single_query(query: str, idx: int):
    context_file = CONTEXT_DIR / f"context_{idx}.json"
    context = {"user_query": query}
    context_file.write_text(json.dumps(context, indent=2))
    cmd = [
        "python3", "-m", "Three_PointO_ArchE.main", "run-workflow", WORKFLOW, "--context", str(context_file)
    ]
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start
    run_id_line = next((l for l in result.stdout.splitlines() if "workflow_run_id" in l), "")
    OUTPUTS.append({
        "query": query,
        "index": idx,
        "duration_sec": round(duration,2),
        "stdout_tail": result.stdout[-500:],
    })
    print(f"Finished query {idx} in {duration:.1f}s")


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_batch.py queries.txt")
        sys.exit(1)
    queries_file = Path(sys.argv[1])
    queries = [q.strip() for q in queries_file.read_text().splitlines() if q.strip()]
    for i,q in enumerate(queries,1):
        run_single_query(q,i)
    summary_path = Path("outputs/batch_summary_"+datetime.utcnow().strftime("%Y%m%d_%H%M%S")+".json")
    summary_path.write_text(json.dumps(OUTPUTS, indent=2))
    print("Batch complete. Summary saved to", summary_path)

if __name__ == "__main__":
    main() 