#!/bin/bash
# =================================================================
# Canonical Entry Point for the ArchE System
# =================================================================
#
# This script is the single, correct way to run any Python component
# of the ArchE system. It performs the critical function of setting
# the PYTHONPATH to the project root, ensuring that all modules and
# sub-packages are discoverable by the interpreter.
#
# It resolves the `ModuleNotFoundError` issues by handling path
# management at the environment level, before the Python process begins.
#

# --- Get the absolute path of the project root (the directory this script is in) ---
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# --- Add the project root to the PYTHONPATH ---
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"

echo "✓ PYTHONPATH set. Project root: ${PROJECT_ROOT}"
echo "--------------------------------------------------"

# --- Activate the virtual environment and execute the Python script ---
# All arguments passed to this script ($@) are forwarded to ask_arche.py
source "${PROJECT_ROOT}/arche_env/bin/activate" && python3 "${PROJECT_ROOT}/ask_arche.py" "$@"
