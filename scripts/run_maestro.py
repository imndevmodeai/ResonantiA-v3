#!/usr/bin/env python3
import sys
import os
import json
import logging

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Three_PointO_ArchE.resonantia_maestro import ResonantiAMaestro, EnhancementLevel
from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine
from Three_PointO_ArchE.spr_manager import SPRManager


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    # Compose query from CLI args or use a default demonstration query
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = "Where does the RISE engine fit and should SCA agents be persisted after creation?"

    # Initialize components
    spr_path = os.path.join(PROJECT_ROOT, "knowledge_graph", "spr_definitions_tv.json")
    try:
        spr_manager = SPRManager(spr_path)
    except Exception as e:
        logging.error("Failed to initialize SPRManager: %s", e)
        spr_manager = None

    try:
        engine = IARCompliantWorkflowEngine(workflows_dir=os.path.join(PROJECT_ROOT, "workflows"), spr_manager=spr_manager)
    except Exception as e:
        logging.error("Failed to initialize IARCompliantWorkflowEngine: %s", e)
        print(json.dumps({"error": f"Engine init failed: {e}"}))
        sys.exit(1)

    # No LLM/search providers configured here; Maestro will gracefully fall back
    maestro = ResonantiAMaestro(
        workflow_engine=engine,
        llm_provider=None,
        spr_manager=spr_manager,
        search_tool=None,
    )

    result = maestro.weave_response(query, enhancement_level=EnhancementLevel.STRATEGIC)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
