# --- START OF FILE Three_PointO_ArchE/config.py ---
# ResonantiA Protocol v3.0 - config.py
# Centralized configuration settings for Arche.
# Reflects v3.0 enhancements including IAR thresholds and temporal tool defaults.

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# --- Project Root ---
# Assumes the script is run from the project root.
# Adjust if necessary, e.g., Path(__file__).parent.parent
PROJECT_ROOT = Path(os.getcwd())

@dataclass
class PathConfig:
    """Stores all relevant paths for the ArchE system."""
    project_root: Path = PROJECT_ROOT
    arche_root: Path = PROJECT_ROOT / "Three_PointO_ArchE"
    tools: Path = arche_root / "tools"
    llm_providers: Path = arche_root / "llm_providers"
    
    # Top-level directories
    knowledge_graph: Path = PROJECT_ROOT / "knowledge_graph"
    workflows: Path = PROJECT_ROOT / "workflows"
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
    # Add other API keys as needed
    # e.g., github_token: str = os.getenv("GITHUB_TOKEN")

@dataclass
class LLMConfig:
    """Configuration for Large Language Models."""
    default_provider: str = "openai"
    default_model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 4096

    # Specific models for different providers
    openai_models: list[str] = field(default_factory=lambda: ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"])
    google_models: list[str] = field(default_factory=lambda: ["gemini-1.5-pro-latest", "gemini-pro"])
    
    # Vetting agent specific configuration
    vetting_provider: str = "openai"
    vetting_model: str = "gpt-4o"

@dataclass
class ToolConfig:
    """Configuration for various cognitive tools."""
    # Code Executor (Docker)
    code_executor_docker_image: str = "python:3.11-slim"
    code_executor_timeout: int = 300  # seconds

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
    cfp_default_evolution_model: str = "placeholder"
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