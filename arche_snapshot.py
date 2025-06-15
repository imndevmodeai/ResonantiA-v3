#!/usr/bin/env python3
import os
import shutil
import time
import json
import logging

# --- GET SCRIPT'S DIRECTORY TO BUILD ROBUST PATHS ---
# This makes the script runnable from any location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR) # Assumes script is in a top-level dir like 'scripts' or root. Adjust if nested deeper.
# If the script is in the project root, use: PROJECT_ROOT = SCRIPT_DIR

# --- CONFIGURABLE PATHS (NOW ROBUST) ---
ARCHETYPE_DIR = os.path.join(PROJECT_ROOT, 'Three_PointO_ArchE') # Corrected path
WORKFLOWS_DIR = os.path.join(PROJECT_ROOT, 'workflows')
# The knowledge graph and protocol docs seem to be in different locations based on the project structure
KNOWLEDGE_GRAPH_FILE = os.path.join(PROJECT_ROOT, 'knowledge_graph', 'spr_definitions_tv.json')
PROTOCOL_DOC_PATH = os.path.join(PROJECT_ROOT, 'wiki', '01_ResonantiA_Protocol_v3_0', '01_Introduction_to_ResonantiA_v3_0.md') # Example path, adjust to actual location

# --- SNAPSHOT OUTPUT BASE ---
SNAPSHOT_BASE = os.path.join(PROJECT_ROOT, 'outputs', 'ResonantiA_Self_Defined_Snapshots_ReSSyD')

# --- LOGGING SETUP ---
LOG_DIR = os.path.join(PROJECT_ROOT, 'outputs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'arche_snapshot.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- DYNAMIC PROTOCOL GENERATION (TEMPLATE) ---
def synthesize_protocol():
    # Read from the dedicated protocol markdown file
    if not os.path.exists(PROTOCOL_DOC_PATH):
        logging.error(f"CRITICAL: Protocol document not found at: {PROTOCOL_DOC_PATH}")
        return "ERROR: ResonantiA Protocol v3.0 document not found. Please ensure it exists at the configured path."
    try:
        with open(PROTOCOL_DOC_PATH, 'r', encoding='utf-8') as f:
            protocol_content = f.read()
        if not protocol_content.strip():
            logging.warning(f"Protocol document at {PROTOCOL_DOC_PATH} is empty.")
            return "WARNING: ResonantiA Protocol v3.0 document is empty."
        return protocol_content
    except Exception as e:
        logging.error(f"Failed to read protocol document from {PROTOCOL_DOC_PATH}: {e}")
        return f"ERROR: Failed to load ResonantiA Protocol v3.0. Details: {e}"

# --- DYNAMIC HOWTO GENERATION (TEMPLATE) ---
def synthesize_howto():
    # In a real system, this could inspect the project, or call an LLM, or assemble from config
    # Here, we use a template string (could be replaced with more dynamic logic)
    return (
        "# HowTo Arche (ResonantiA Protocol v3.0)\n\n"
        "## 1. Project Overview\n\n"
        "Arche is an advanced AI system operating under the ResonantiA Protocol v3.0. Its purpose is to achieve deep **`Cognitive resonancE`** by aligning data, analysis, strategy, and outcomes dynamically across time (**`Temporal Resonance`**). Key v3.0 features include **`Integrated Action Reflection` (`IAR`)** for continuous self-assessment, and comprehensive **`Temporal Reasoning` (`4D Thinking`)** capabilities.\n\n"
        "## 2. Core Project Structure\n\n"
        "The project is primarily organized into:\n\n"
        "*   **`ArchE/`**: The core Python package containing all logic for Arche, including:\n"
        "    *   `config.py`: Central configuration.\n"
        "    *   `main.py`: Main execution entry point.\n"
        "    *   `workflow_engine.py`: Orchestrates workflows.\n"
        "    *   `action_registry.py`: Manages and dispatches tool actions.\n"
        "    *   `spr_manager.py`: Handles Sparse Priming Representations.\n"
        "    *   Tool modules like `tools.py`, `enhanced_tools.py`, `code_executor.py`, `cfp_framework.py`, `predictive_modeling_tool.py`, `causal_inference_tool.py`, `agent_based_modeling_tool.py`, etc.\n"
        "    *   (Full list of modules: see code manifest.)\n"
        "*   **`workflows/`**: Contains JSON definitions for `Process blueprintS` (workflows).\n"
        "*   **`knowledge_graph/`**: Stores the `Knowledge tapestrY`.\n"
        "    *   `spr_definitions_tv.json`: Definitions for all `SPRs`.\n\n"
        "## 3. Setup Instructions\n\n"
        "1.  **Prerequisites:** Python 3.9+, Git. **Docker Desktop/Engine is CRITICAL** for secure `CodeexecutoR` operation.\n"
        "2.  **Clone:** Get the project code.\n"
        "3.  **Virtual Environment:**\n    ```bash\n    python -m venv .venv\n    source .venv/bin/activate # Or equivalent for your OS\n    ```\n"
        "4.  **Dependencies:**\n    ```bash\n    pip install -r requirements.txt\n    ```\n"
        "5.  **API Key Configuration (CRITICAL):**\n"
        "    *   Edit `ArchE/config.py` **ONLY** if you cannot use environment variables.\n"
        "    *   **STRONGLY RECOMMENDED:** Set API keys (OpenAI, Google, Search, etc.) as **ENVIRONMENT VARIABLES** (e.g., `export OPENAI_API_KEY='your_actual_key'`). `config.py` is designed to read these. **DO NOT COMMIT KEYS.**\n"
        "6.  **Docker:** Ensure Docker is installed, running, and the user has permissions to run containers. Verify `CODE_EXECUTOR_SANDBOX_METHOD = 'docker'` in `config.py`.\n\n"
        "## 4. Basic Usage\n\n"
        "1.  Activate virtual environment.\n"
        "2.  Set API key environment variables.\n"
        "3.  Run workflows from the project root directory:\n    ```bash\n    python -m ArchE.main workflows/basic_analysis.json -c '{\"user_query\": \"What is IAR?\"}'\n    ```\n"
        "4.  **Interpreting Output:** Check console, `logs/arche_v3_log.log`, and `outputs/` for JSON results. Each task's result in the JSON output will contain a `reflection` dictionary – this is the **`IAR`** data, providing status, confidence, issues, etc., for that specific step.\n\n"
        "## 5. Key v3.0 Features to Explore\n\n"
        "*   **`IAR` (Integrated Action Reflection):** Examine the `reflection` dictionary in all task outputs. Use it in workflow `condition` fields.\n"
        "*   **Temporal Tools:** Experiment with `temporal_forecasting_workflow.json`, `temporal_causal_analysis_workflow.json`, `comparative_future_scenario_workflow.json`. Explore `PredictivE ModelinG TooL`, `CausalInferenceTool`, `AgentBasedModelingTool`, and `CfpframeworK` with state evolution.\n"
        "*   **Meta-Cognition:** Use patterns in Section 8 of the Protocol Document to invoke `Metacognitive shifT` (e.g., via `self_reflection.json`) or conceptual `SIRC`.\n"
        "*   **`SPRs`:** Review `knowledge_graph/spr_definitions_tv.json`. Observe how SPRs are used in prompts and workflow logic. Use `InsightSolidificatioN` to add new knowledge.\n\n"
        "## 6. Disclaimer\n\n"
        "This is an advanced, experimental AI framework.\n"
        "*   **Security:** Docker sandboxing for `CodeexecutoR` is essential. Manage API keys securely via environment variables.\n"
        "*   **Ethics:** Adhere to ethical guidelines (Protocol Section 6). `Keyholder Override` bypasses safeguards; use responsibly.\n"
        "*   **Experimental:** While core features are implemented, some advanced algorithms or integrations may be conceptual. Outputs from analytical tools require careful interpretation and validation.\n"
    )

# --- MAIN SNAPSHOT FUNCTION ---
def create_snapshot():
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    package_name = f'ResonantiA_Canonical_Package_{timestamp}'
    package_dir = os.path.join(SNAPSHOT_BASE, package_name)
    try:
        logging.info(f"Snapshot run started: {package_name}")
        os.makedirs(os.path.join(package_dir, 'Packaged_Workflows'), exist_ok=True)
        os.makedirs(os.path.join(package_dir, 'Packaged_KnowledgeGraph'), exist_ok=True)
        os.makedirs(os.path.join(package_dir, 'Packaged_Code'), exist_ok=True)

        # 1. Copy all workflow JSONs
        if not os.path.exists(WORKFLOWS_DIR):
            logging.error(f"Workflows directory not found at: {WORKFLOWS_DIR}")
        else:
            for file in os.listdir(WORKFLOWS_DIR):
                if file.endswith('.json'):
                    shutil.copy2(os.path.join(WORKFLOWS_DIR, file), os.path.join(package_dir, 'Packaged_Workflows', file))

        # 2. Copy SPR definitions
        if not os.path.exists(KNOWLEDGE_GRAPH_FILE):
             logging.error(f"Knowledge graph file not found at: {KNOWLEDGE_GRAPH_FILE}")
        else:
            shutil.copy2(KNOWLEDGE_GRAPH_FILE, os.path.join(package_dir, 'Packaged_KnowledgeGraph', 'spr_definitions_tv.json'))

        # 3. Generate code manifest from the correct ArchE directory
        manifest = []
        if not os.path.exists(ARCHETYPE_DIR):
            logging.error(f"ArchE code directory not found at: {ARCHETYPE_DIR}")
        else:
            for file in os.listdir(ARCHETYPE_DIR):
                if file.endswith('.py'):
                    manifest.append(file)
            manifest.sort()
            with open(os.path.join(package_dir, 'Packaged_Code', 'ArchE_Manifest.json'), 'w') as f:
                json.dump({'modules': manifest}, f, indent=2)

        # 4. Dynamically generate protocol and HowTo files
        protocol_target = os.path.join(package_dir, f'ResonantiA_Protocol_v3.0_Canonical_{timestamp}.md')
        howto_target = os.path.join(package_dir, f'HowTo_Arche_{timestamp}.md')
        with open(protocol_target, 'w') as f:
            f.write(synthesize_protocol())
        with open(howto_target, 'w') as f:
            f.write(synthesize_howto())

        logging.info(f"Snapshot created successfully at: {package_dir}")
        print(f"Snapshot created at: {package_dir}")
        print(f"Includes workflows, knowledge graph, code manifest, protocol, and HowTo guide (all generated dynamically).")
    except Exception as e:
        logging.error(f"Snapshot failed: {package_name} | Error: {e}")
        print(f"Snapshot failed: {e}")

if __name__ == '__main__':
    create_snapshot() 