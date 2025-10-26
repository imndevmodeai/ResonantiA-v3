# ResonantiA Protocol v2.9.5 - config.py
# Configuration settings for Arche

import logging
import os # Added for potential env var use

# --- LLM Configuration ---
LLM_PROVIDERS = {
    "openai": { # Example using standard key name
        "api_key": os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE"), # Prioritize env var
        "base_url": None, # Optional: For custom endpoints
        "default_model": "gpt-4-turbo-preview", # Example model
        "backup_model": "gpt-3.5-turbo"
    },
    "google": { # Example using standard key name
        "api_key": os.environ.get("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE"), # Prioritize env var
        "base_url": None,
        "default_model": "gemini-pro", # Example model
    },
    # Add more providers as needed (e.g., anthropic, cohere) following a similar structure
    # "anthropic": {
    #     "api_key": os.environ.get("ANTHROPIC_API_KEY", "YOUR_ANTHROPIC_API_KEY_HERE"),
    #     "default_model": "claude-3-opus-20240229",
    # },
}
# Choose the default provider key (lowercase) to use if not specified in a task
DEFAULT_LLM_PROVIDER = "openai"
# Set a specific model name to override provider defaults, or None to use provider's default
DEFAULT_LLM_MODEL = None
# Default LLM settings (can be overridden in invoke_llm inputs)
LLM_DEFAULT_MAX_TOKENS = 1024
LLM_DEFAULT_TEMP = 0.7

# --- Tool Configuration ---
# Example: Search Tool (using a hypothetical config structure)
# Replace with actual config needed by your chosen search library/API wrapper
SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY", "YOUR_SEARCH_API_KEY_HERE") # e.g., SerpApi, Google Custom Search
SEARCH_PROVIDER = "simulated_google" # Options: 'simulated_google', 'serpapi', 'google_custom_search' etc.

# Example: Code Executor
CODE_EXECUTOR_TIMEOUT = 30 # Seconds before killing the execution
CODE_EXECUTOR_USE_SANDBOX = True # CRITICAL: Set to False ONLY for trusted code / testing. Docker recommended.
# Options for SANDBOX_METHOD in code_executor.py: 'docker', 'subprocess', 'none'
CODE_EXECUTOR_SANDBOX_METHOD = 'docker' # Strongly recommended
CODE_EXECUTOR_DOCKER_IMAGE = "python:3.10-slim" # Docker image for python execution sandbox

# --- File Paths ---
# Assumes execution from the root directory containing 'mastermind_ai_v2_9', 'workflows', etc.
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Gets the parent dir of mastermind_ai_v2_9
# It's often safer to define paths relative to where the main script runs or use absolute paths
# For simplicity here, assuming relative paths from project root
BASE_DIR = "." # Assume running from resonatia_arche root
MASTERMIND_DIR = os.path.join(BASE_DIR, "mastermind_ai_v2_9")
WORKFLOW_DIR = os.path.join(BASE_DIR, "workflows")
KNOWLEDGE_GRAPH_DIR = os.path.join(BASE_DIR, "knowledge_graph")
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
MODEL_SAVE_DIR = os.path.join(OUTPUT_DIR, "models") # Specific dir for models
SPR_JSON_FILE = os.path.join(KNOWLEDGE_GRAPH_DIR, "spr_definitions_tv.json")
LOG_FILE = os.path.join(LOG_DIR, "arche_log.log")

# --- Logging Configuration ---
LOG_LEVEL = logging.INFO # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_MAX_BYTES = 10*1024*1024 # 10MB file size limit for rotation
LOG_BACKUP_COUNT = 5 # Number of backup log files to keep

# --- Workflow Engine Configuration ---
MAX_RECURSION_DEPTH = 10 # Prevent infinite loops in workflow execution
DEFAULT_RETRY_ATTEMPTS = 1 # Default number of retries for failed actions (0 means 1 attempt total)
DEFAULT_ERROR_STRATEGY = "retry" # Default error handling: 'retry', 'fail_fast', 'log_and_continue', 'trigger_metacog'

# --- CFP Configuration ---
CFP_DEFAULT_TIMEFRAME = 1.0 # Default time horizon for CFP analysis in seconds

# --- ABM Configuration ---
ABM_DEFAULT_STEPS = 100 # Default number of steps for ABM simulations
ABM_VISUALIZATION_ENABLED = True # Whether to attempt saving visualizations

# --- Security & Ethics ---
# Define any specific ethical flags or restricted topics if needed
RESTRICTED_TOPICS = ["illegal_activity_promotion", "hate_speech_generation", "non_consensual_content"] # Example list

# --- Meta-Cognition ---
# Example thresholds (adjust based on testing)
METAC_DISSONANCE_THRESHOLD = 0.7 # Confidence score below which might trigger Shift
SIRC_COMPLEXITY_THRESHOLD = 0.8 # Prompt complexity score above which might trigger SIRC

# --- Add other configurations as needed ---
