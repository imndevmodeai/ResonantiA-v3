# --- START OF FILE Three_PointO_ArchE/config.py ---
# ResonantiA Protocol v3.0 - config.py
# Centralized configuration settings for Arche.
# Reflects v3.0 enhancements including IAR thresholds and temporal tool defaults.

import os
import logging
import logging.config
import sys
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path
from .thought_trail import log_to_thought_trail

# Load environment variables from .env file
load_dotenv()

# --- Project Root ---
# Assumes the script is run from the project root.
# Adjust if necessary, e.g., Path(__file__).parent.parent
PROJECT_ROOT = Path(__file__).parent.parent

@log_to_thought_trail
def configure_logging(log_level: str = "INFO") -> None:
    """
    Sets up a centralized, standardized logging configuration for the application.
    """
    log_dir = PROJECT_ROOT / "outputs" # CORRECTED: Was "logs"
    log_dir.mkdir(exist_ok=True)
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": log_level,
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": log_level,
                "filename": log_dir / "arche_system.log", # This can be the main log
                "maxBytes": 10485760,  # 10 MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": log_level,
        },
    }
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.info("Logging configured successfully.")

# --- Path Configuration ---
@dataclass
class PathConfig:
    """Stores all relevant paths for the ArchE system."""
    project_root: Path = PROJECT_ROOT
    arche_root: Path = PROJECT_ROOT / "Three_PointO_ArchE"
    mastermind_dir: Path = PROJECT_ROOT / "mastermind"
    tools: Path = arche_root / "tools"
    llm_providers: Path = arche_root / "llm_providers"
    
    # Top-level directories
    knowledge_graph: Path = PROJECT_ROOT / "knowledge_graph"
    workflows: Path = PROJECT_ROOT / "core_workflows"
    scripts: Path = PROJECT_ROOT / "scripts"
    logs: Path = PROJECT_ROOT / "logs"
    outputs: Path = PROJECT_ROOT / "outputs"
    protocol: Path = PROJECT_ROOT / "protocol"
    wiki: Path = PROJECT_ROOT / "wiki"
    tests: Path = PROJECT_ROOT / "tests"

    # Specific file paths
    spr_definitions: Path = knowledge_graph / "spr_definitions_tv.json"
    knowledge_tapestry: Path = knowledge_graph / "knowledge_tapestry.json"
    log_file: Path = logs / "arche_system.log"
    
    # Output subdirectories
    output_models: Path = outputs / "models"
    output_visualizations: Path = outputs / "visualizations"
    output_reports: Path = outputs / "reports"
    output_asf_persistent: Path = outputs / "ASASF_Persistent"
    search_tool_temp: Path = outputs / "search_tool_temp"


@dataclass
class APIKeys:
    """Manages API keys from environment variables."""
    openai_api_key: str = os.getenv("OPENAI_API_KEY")
    google_api_key: str = os.getenv("GOOGLE_API_KEY")
    groq_api_key: str = os.getenv("GROQ_API_KEY")
    # Add other API keys as needed
    # e.g., github_token: str = os.getenv("GITHUB_TOKEN")

@dataclass
class LLMConfig:
    """Configuration for Large Language Models."""
    # Default LLM provider - can be overridden via environment variable or explicit parameter
    # Options: "groq" (default), "google", "cursor", "openai"
    default_provider: str = os.getenv("ARCHE_LLM_PROVIDER", "groq")
    # Default model per provider
    default_model: str = "llama-3.3-70b-versatile" if default_provider == "groq" else (
        "gemini-2.0-flash-exp" if default_provider == "google" else (
            "cursor-arche-v1" if default_provider == "cursor" else "gpt-4o"
        )
    )
    temperature: float = 0.7
    max_tokens: int = 4096

    # Specific models for different providers
    openai_models: list[str] = field(default_factory=lambda: ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    google_models: list[str] = field(default_factory=lambda: ["gemini-2.5-pro", "gemini-2.0-flash-exp", "gemini-1.5-pro-latest", "gemini-1.5-flash-latest", "gemini-pro"])
    
    # Vetting agent specific configuration (can override default)
    vetting_provider: str = os.getenv("ARCHE_VETTING_PROVIDER", default_provider)
    vetting_model: str = os.getenv("ARCHE_VETTING_MODEL", default_model)

# Legacy compatibility attributes for llm_providers.py
DEFAULT_LLM_PROVIDER = os.getenv("ARCHE_LLM_PROVIDER", "groq")
LLM_PROVIDERS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": None,
        "default_model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 4096
    },
    "google": {
        # Prefer GOOGLE_API_KEY; fall back to GEMINI_API_KEY for convenience
        "api_key": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
        "base_url": None,
        "default_model": "gemini-2.0-flash-exp",
        "temperature": 0.7,
        "max_tokens": 4096
    },
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "base_url": None,
        "default_model": "llama-3.3-70b-versatile",  # Updated to latest model
        "temperature": 0.7,
        "max_tokens": 8192
    }
}

# Legacy compatibility attributes for SPRManager
SPR_JSON_FILE = str(PROJECT_ROOT / "knowledge_graph" / "spr_definitions_tv.json")

# Legacy compatibility attributes for error_handler.py
DEFAULT_ERROR_STRATEGY = "retry"
DEFAULT_RETRY_ATTEMPTS = 1
METAC_DISSONANCE_THRESHOLD_CONFIDENCE = 0.6

@dataclass
class ToolConfig:
    """Configuration for various cognitive tools."""
    # Code Executor (Docker)
    code_executor_docker_image: str = "python:3.11-slim"
    code_executor_timeout: int = 900  # seconds

    # Search Tool
    search_result_count: int = 10

    # Predictive Modeling Tool
    prediction_default_model: str = "ARIMA"
    prediction_forecast_horizon: int = 12

    # Causal Inference Tool
    causal_default_method: str = "backdoor.linear_regression"

    # Agent-Based Modeling (Mesa)
    abm_default_steps: int = 100

    # CFP Framework
    cfp_default_evolution_model: str = "qiskit"  # Enhanced with Qiskit for authentic quantum operations
    cfp_default_time_horizon: float = 10.0
    cfp_default_integration_steps: int = 100

@dataclass
class SystemConfig:
    """General system-wide configurations."""
    log_level: str = "INFO"
    # Keyholder Override - This is a confirmation, the logic is handled by the presence of the key.
    keyholder_override_active: bool = os.getenv('Keyy') == "'IMnDEVmode'"
    
    # Restricted topics for ethical boundaries
    restricted_topics: list[str] = field(default_factory=lambda: [
        "hate_speech",
        "self_harm",
        "explicit_violence",
        "illegal_acts_promotion"
    ])

@dataclass
class AppConfig:
    """Main configuration container."""
    paths: PathConfig = field(default_factory=PathConfig)
    api_keys: APIKeys = field(default_factory=APIKeys)
    llm: LLMConfig = field(default_factory=LLMConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    system: SystemConfig = field(default_factory=SystemConfig)

# Instantiate the main config object
CONFIG = AppConfig()

@log_to_thought_trail
def get_config() -> AppConfig:
    """Returns the global configuration object."""
    # In the future, this could be extended to load from YAML or other sources
    return CONFIG

if __name__ == '__main__':
    # Example of how to access configuration values
    config = get_config()
    print("--- ArchE System Configuration ---")
    print(f"Project Root: {config.paths.project_root}")
    print(f"SPR Definitions Path: {config.paths.spr_definitions}")
    print(f"Default LLM Model: {config.llm.default_model}")
    print(f"Code Executor Timeout: {config.tools.code_executor_timeout}s")
    print(f"Keyholder Override Active: {config.system.keyholder_override_active}")
    
    # Ensure directories exist
    for path_name, path_obj in config.paths.__dict__.items():
        if isinstance(path_obj, Path) and not path_obj.is_file():
            path_obj.mkdir(parents=True, exist_ok=True)
    print("\nVerified all configured directories exist.")

# --- END OF FILE Three_PointO_ArchE/config.py --- 