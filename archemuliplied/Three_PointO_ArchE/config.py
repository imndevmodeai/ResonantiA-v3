# ResonantiA Protocol v3.0 - config.py
# Configuration settings for Arche

import logging
import os
from pathlib import Path

# --- Core Paths ---
# Use an absolute base path for robustness
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
OUTPUT_DIR = BASE_DIR / "outputs"
WORKFLOW_DIR = BASE_DIR / "workflows"
KNOWLEDGE_GRAPH_DIR = BASE_DIR / "knowledge_graph"
MODEL_SAVE_DIR = OUTPUT_DIR / "models"


class Config:
    """
    The Foundation Stone of ArchE.
    Centralized configuration object that holds all essential settings and paths,
    mirroring the structure described in specifications/config.md.
    """
    def __init__(self):
        # --- Path Management ---
        class Paths:
            def __init__(self):
                self.project_root = BASE_DIR
                self.arche_root = BASE_DIR / "Three_PointO_ArchE"
                self.logs = LOG_DIR
                self.outputs = OUTPUT_DIR
                self.workflows = WORKFLOW_DIR
                self.knowledge_graph = KNOWLEDGE_GRAPH_DIR
                self.output_models = MODEL_SAVE_DIR
                self.output_visualizations = OUTPUT_DIR / "visualizations"
                self.output_reports = OUTPUT_DIR / "reports"

        self.paths = Paths()

        # --- LLM Configuration ---
        class LLM:
            def __init__(self):
                self.providers = {
                    "openai": {
                        "api_key": os.environ.get("OPENAI_API_KEY"),
                        "default_model": "gpt-4-turbo-preview",
                    },
                    "google": {
                        "api_key": os.environ.get("GOOGLE_API_KEY"),
                        "default_model": "gemini-1.5-pro-latest",
                    }
                }
                self.default_provider = "google"
                self.default_model = "gemini-1.5-flash-latest"
                self.temperature = 0.5
                self.max_tokens = 4096

        self.llm = LLM()
        
        # --- Tool Configuration ---
        class Tools:
            def __init__(self):
                self.code_executor_timeout = 300
                self.search_result_count = 10
                self.prediction_default_model = "LinearRegression"
                self.cfp_default_time_horizon = 10.0
                self.cfp_default_integration_steps = 100
                self.cfp_default_evolution_model = "placeholder"
        
        self.tools = Tools()

        # --- System Configuration ---
        class System:
            def __init__(self):
                self.log_level = "INFO"
                self.keyholder_override_active = os.environ.get("KEYHOLDER_OVERRIDE_ACTIVE", "false").lower() == "true"
                self.restricted_topics = []

        self.system = System()

        # Ensure directories exist
        LOG_DIR.mkdir(exist_ok=True)
        OUTPUT_DIR.mkdir(exist_ok=True)
        MODEL_SAVE_DIR.mkdir(exist_ok=True)

# --- Singleton Instance ---
CONFIG = Config()

def get_config():
    """Returns the singleton Config instance."""
    return CONFIG

# Legacy flat variables for compatibility where needed, though structured access is preferred.
LLM_PROVIDERS = CONFIG.llm.providers
DEFAULT_LLM_PROVIDER = "google"
DEFAULT_LLM_MODEL = None # Let provider's default take precedence
LLM_DEFAULT_MAX_TOKENS = 4096
LLM_DEFAULT_TEMP = 0.5
LLM_REQUEST_TIMEOUT = 120 # seconds

# --- Search Configuration ---
SEARCH_PROVIDER = "simulated_google" # or "serpapi", "google_custom_search" etc.
SEARCH_API_KEY = os.environ.get("SERP_API_KEY", "YOUR_SEARCH_API_KEY_HERE")

# --- Logging Configuration ---
LOG_LEVEL = "INFO" # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.path.join(LOG_DIR, "arche_log.log")
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 5 * 1024 * 1024 # 5 MB
LOG_BACKUP_COUNT = 3

# --- Workflow Engine Configuration ---
# Specifies the file path for Sparse Priming Representation definitions
SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "spr_definitions_tv.json")

# --- Code Executor Configuration ---
CODE_EXECUTOR_TIMEOUT = 300 # seconds
# Set to True to use Docker for code execution, requires Docker to be running
USE_DOCKER_FOR_EXECUTION = False
DOCKER_IMAGE = "python:3.10-slim"

# --- Agent-Based Modeling Configuration ---
ABM_DEFAULT_STEPS = 100
ABM_VISUALIZATION_ENABLED = True

# --- Causal Inference Configuration ---
CAUSAL_INFERENCE_DEFAULT_METHOD = "backdoor.linear_regression"

# --- CFP Framework Configuration ---
CFP_DEFAULT_EVOLUTION_MODEL = "placeholder"
CFP_DEFAULT_TIME_HORIZON = 10.0
CFP_DEFAULT_INTEGRATION_STEPS = 100

# --- Security & Compliance ---
# In a production system, use a proper secrets management tool (e.g., Vault, AWS Secrets Manager)
# This is a placeholder for demonstration.
SECRET_KEYS = {
    "example_api": os.environ.get("EXAMPLE_API_SECRET", "default_secret_value")
} 