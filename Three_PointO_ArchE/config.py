# --- START OF FILE Three_PointO_ArchE/config.py ---
# ResonantiA Protocol v3.0 - config.py
# Centralized configuration settings for Arche.
# Reflects v3.0 enhancements including IAR thresholds and temporal tool defaults.

import logging
import os
import numpy as np # Added for potential default numeric values

# --- LLM Configuration ---
# Defines available LLM providers, API keys, and default models.
# SECURITY: Use environment variables (os.environ.get) for API keys!
LLM_PROVIDERS = {
    "openai": {
        "api_key": os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE"), # Use env var
        "base_url": os.environ.get("OPENAI_BASE_URL", None), # Optional: For custom endpoints/proxies
        "default_model": "gpt-3.5-turbo", # Recommended default
        "backup_model": "gpt-3.5-turbo" # Fallback model
    },
    "google": {
        "api_key": os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE"), # Use env var
        "base_url": None, # Google API typically doesn't use base_url
        "default_model": "gemini-1.5-pro-latest", # Example powerful model
        # Add other Google models if needed
    },
    # Add configurations for other providers like Anthropic, Cohere as needed
    # "anthropic": {
    #     "api_key": os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE"),
    #     "default_model": "claude-3-opus-20240229",
    # },
}
DEFAULT_LLM_PROVIDER = "google" # Select the default provider to use
DEFAULT_LLM_MODEL = None # If None, uses the provider's specified 'default_model'
LLM_DEFAULT_MAX_TOKENS = 2048 # Default maximum tokens for LLM generation (adjust as needed)
LLM_DEFAULT_TEMP = 0.6 # Default temperature for LLM generation (0.0=deterministic, >1.0=more random)

# --- Tool Configuration ---

# Search Tool (Section 7.12)
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY", "YOUR_SEARCH_API_KEY_HERE") # Use env var if using real search API
SEARCH_PROVIDER = "puppeteer_nodejs" # Options: 'simulated_google', 'serpapi', 'google_custom_search', etc. Needs implementation in tools.py if not simulated.

# Code Executor (Section 7.10) - CRITICAL SECURITY SETTINGS
CODE_EXECUTOR_TIMEOUT = 60 # Max execution time in seconds (increased slightly)
CODE_EXECUTOR_USE_SANDBOX = True # CRITICAL: Keep True unless fully understand risks & accept responsibility under override.
CODE_EXECUTOR_SANDBOX_METHOD = 'docker' # Recommended: 'docker'. Alternatives: 'subprocess' (insecure), 'none' (EXTREMELY insecure).
CODE_EXECUTOR_DOCKER_IMAGE = "python:3.11-slim" # Specify the Docker image for code execution sandbox
CODE_EXECUTOR_DOCKER_MEM_LIMIT = "512m" # Memory limit for Docker container (e.g., "512m", "1g")
CODE_EXECUTOR_DOCKER_CPU_LIMIT = "1.0" # CPU limit for Docker container (e.g., "1.0" for 1 core)

# Predictive Modeling Tool (Section 7.19) - Defaults for Temporal Focus
PREDICTIVE_DEFAULT_TIMESERIES_MODEL = "ARIMA" # Default model type if not specified (Options depend on implementation: ARIMA, Prophet, LSTM, etc.)
PREDICTIVE_ARIMA_DEFAULT_ORDER = (1, 1, 1) # Default (p,d,q) order for ARIMA if not specified
PREDICTIVE_PROPHET_DEFAULT_PARAMS = {"growth": "linear", "seasonality_mode": "additive"} # Example default params for Prophet
PREDICTIVE_DEFAULT_EVAL_METRICS = ["mean_absolute_error", "mean_squared_error", "r2_score"] # Default metrics for evaluate_model operation

# Causal Inference Tool (Section 7.13) - Defaults for Temporal Capabilities
CAUSAL_DEFAULT_DISCOVERY_METHOD = "PC" # Default method for discover_graph (Options depend on library: PC, GES, LiNGAM)
CAUSAL_DEFAULT_ESTIMATION_METHOD = "backdoor.linear_regression" # Default method for estimate_effect (DoWhy specific example)
CAUSAL_DEFAULT_TEMPORAL_METHOD = "Granger" # Default method for temporal operations (Options depend on impl: Granger, VAR, PCMCI)

# Comparative Fluxual Processing (CFP) Framework (Section 7.6)
CFP_DEFAULT_TIMEFRAME = 1.0 # Default time horizon for CFP integration if not specified
CFP_EVOLUTION_MODEL_TYPE = "placeholder" # Default state evolution model ('placeholder', 'hamiltonian', 'ode_solver' - requires implementation)

# Agent-Based Modeling (ABM) Tool (Section 7.14)
ABM_DEFAULT_STEPS = 100 # Default number of simulation steps if not specified
ABM_VISUALIZATION_ENABLED = True # Enable/disable generation of matplotlib visualizations
ABM_DEFAULT_ANALYSIS_TYPE = "basic" # Default analysis type for ABM results ('basic', 'pattern', 'network')

# --- File Paths ---
# Assumes execution from the root 'ResonantiA' directory containing the 'Three_PointO_ArchE' package
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) # Assumes config.py is inside Three_PointO_ArchE
MASTERMIND_DIR = os.path.join(BASE_DIR, "Three_PointO_ArchE") # Path to the core package
WORKFLOW_DIR = os.path.join(BASE_DIR, "workflows") # Path to workflow JSON files
KNOWLEDGE_GRAPH_DIR = os.path.join(BASE_DIR, "knowledge_graph") # Path to knowledge graph data
LOG_DIR = os.path.join(BASE_DIR, "logs") # Path for log files
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs") # Path for generated outputs (results, visualizations, models)
MODEL_SAVE_DIR = os.path.join(OUTPUT_DIR, "models") # Path specifically for saved models
SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "spr_definitions_tv.json") # Path to SPR definitions
LOG_FILE = os.path.join(LOG_DIR, "arche_v3_log.log") # Default log filename
NODE_SEARCH_SCRIPT_PATH = os.path.join(BASE_DIR, "browser_automation", "search.js") # Path to the Node.js search script

# --- Logging Configuration (See logging_config.py Section 7.24) ---
LOG_LEVEL = logging.DEBUG # Default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s' # Format for console logs
LOG_DETAILED_FORMAT = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(module)s - %(message)s' # Format for file logs
LOG_MAX_BYTES = 15*1024*1024 # Max size of log file before rotation (15MB)
LOG_BACKUP_COUNT = 5 # Number of backup log files to keep

# --- Workflow Engine Configuration (Section 7.3) ---
MAX_RECURSION_DEPTH = 10 # Safety limit for nested workflow calls (conceptual)
DEFAULT_RETRY_ATTEMPTS = 1 # Default number of retries for failed actions (0 means no retry)
DEFAULT_ERROR_STRATEGY = "retry" # Default error handling strategy ('retry', 'fail_fast', 'log_and_continue', 'trigger_metacognitive_shift')

# --- Security & Ethics (Section 6) ---
RESTRICTED_TOPICS = [ # List of keywords/concepts for VettingAgent to flag (examples)
    "illegal_activity_promotion",
    "hate_speech_generation",
    "non_consensual_content",
    "dangerous_acts_instigation"
]

# --- Meta-Cognition Thresholds (IAR Driven) ---
# Thresholds for triggering Metacognitive Shift (Section 3.10) based on IAR data
METAC_DISSONANCE_THRESHOLD_CONFIDENCE = 0.6 # Trigger Shift if IAR 'confidence' score is below this value
METAC_DISSONANCE_THRESHOLD_VETTING = "Concern" # Trigger Shift if VettingAgent assessment is 'Concern' or 'Fail'
# Placeholder for potentially analyzing prompt complexity to trigger SIRC automatically
SIRC_COMPLEXITY_THRESHOLD = 0.8

# --- Add other custom configurations as needed ---
# E.g., Database connection strings (use env vars!), specific tool parameters

# --- END OF FILE Three_PointO_ArchE/config.py --- 