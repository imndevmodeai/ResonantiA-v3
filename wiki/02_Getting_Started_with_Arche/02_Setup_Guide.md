# 2. Setup Guide (Detailed Walkthrough)

<!--
Instruction for AI Assistant (e.g., Cursor) or Keyholder populating the Wiki:
Expand on Section 4 of the ResonantiA Protocol v3.0. Provide step-by-step commands and explanations.
-->

This guide provides a detailed walkthrough for setting up the Arche project environment. It expands on the information in Section 4 of the ResonantiA Protocol v3.0.

*   **Cloning the Repository**
    *   Command: `git clone <repository_url>` (Replace `<repository_url>` with the actual URL)
    *   Explanation: Briefly explain what cloning does.
*   **Setting up a Python Virtual Environment**
    *   Command (Linux/macOS): `python3 -m venv .venv`
    *   Command (Windows): `python -m venv .venv`
    *   Activation (Linux/macOS): `source .venv/bin/activate`
    *   Activation (Windows Cmd): `.venv\Scripts\activate`
    *   Activation (Windows PowerShell): `.venv\Scripts\Activate.ps1`
    *   Explanation: Importance of virtual environments.
*   **Installing Dependencies**
    *   Command: `pip install -r requirements.txt`
    *   Explanation: How this command installs the libraries listed in `requirements.txt`.
*   **Directory Structure Explained**
    *   Provide an overview of the key directories and their purpose:
        *   `Three_PointO_ArchE/`: The core Python package containing all of Arche's logic.
        *   `workflows/`: Contains workflow definitions (`Process blueprintS`) in JSON format.
        *   `Three_PointO_ArchE/knowledge_graph/`: Contains the `Knowledge tapestrY` (`spr_definitions_tv.json`).
        *   `outputs/`: Default directory for all generated files, including results, models, and visualizations.
        *   `logs/`: Contains execution logs (`arche_v3_log.log`).
    *   (Link back to Section 4.2 of the Protocol for the canonical structure if desired). 