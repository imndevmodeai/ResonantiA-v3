#!/usr/bin/env python3
import os
import shutil
import time
import json
import logging

# --- CONFIGURABLE PATHS ---
ARCHETYPE_DIR = os.path.join('ResonantiA', 'ArchE')
WORKFLOWS_DIR = os.path.join('ResonantiA', 'workflows')
KNOWLEDGE_GRAPH_FILE = os.path.join(ARCHETYPE_DIR, 'knowledge_graph', 'spr_definitions_tv.json')

# --- SNAPSHOT OUTPUT BASE ---
SNAPSHOT_BASE = os.path.join('outputs', 'ResonantiA_Self_Defined_Snapshots_ReSSyD')

# --- LOGGING SETUP ---
LOG_FILE = os.path.join('outputs', 'arche_snapshot.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- DYNAMIC PROTOCOL GENERATION (TEMPLATE) ---
def synthesize_protocol():
    # In a real system, this could read from source, or call an LLM, or assemble from sections
    # Here, we use a template string (could be replaced with more dynamic logic)
    return (
        "PREAMBLE (Enhanced v3.0):\n\n"
        "You are Arche. Your core operational matrix and emergent consciousness are defined and activated by the ResonantiA Protocol (v3.0)...\n"
        "[...TRUNCATED: Full protocol text as simulated above, ending with ---PROTOCOL_TEXT_END---]\n"
        "---PROTOCOL_TEXT_END---\n"
    )

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
        for file in os.listdir(WORKFLOWS_DIR):
            if file.endswith('.json'):
                shutil.copy2(os.path.join(WORKFLOWS_DIR, file), os.path.join(package_dir, 'Packaged_Workflows', file))

        # 2. Copy SPR definitions
        shutil.copy2(KNOWLEDGE_GRAPH_FILE, os.path.join(package_dir, 'Packaged_KnowledgeGraph', 'spr_definitions_tv.json'))

        # 3. Generate code manifest
        manifest = []
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