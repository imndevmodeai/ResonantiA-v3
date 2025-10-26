import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class Config:
    """
    The Centralized Rulebook of ArchE. This class loads, validates, and provides
    access to all system-wide configuration parameters. It promotes modularity and
    adaptability by decoupling configuration from the core application logic.

    Settings are loaded from a `config.yaml` file, with environment variables
    taking precedence for sensitive data like API keys.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.config_path = Path(config_path)
        self.settings: Dict[str, Any] = {}
        self._load_config()
        self._initialized = True
        logger.info(f"Configuration loaded from '{self.config_path}' and environment variables.")

    def _load_config(self):
        """Loads configuration from YAML file and environment variables."""
        # 1. Load default settings
        defaults = self._get_default_settings()
        self.settings.update(defaults)

        # 2. Load settings from YAML file
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self.settings.update(self._recursive_update(self.settings, yaml_config))
            else:
                logger.warning(f"Config file not found at '{self.config_path}'. Using default settings. Consider creating one.")
                self._create_default_config_file()

        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file '{self.config_path}': {e}. Using default settings.", exc_info=True)
        
        # 3. Override with environment variables for sensitive data
        self._override_with_env_vars()

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieves a configuration value. Nested keys can be accessed with dot notation.
        e.g., config.get('logging.level')
        """
        keys = key.split('.')
        value = self.settings
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def _get_default_settings(self) -> Dict[str, Any]:
        """Provides the base configuration for the system."""
        return {
            "system": {
                "version": "3.5.0-ArchE",
                "name": "ArchE",
            },
            "logging": {
                "level": "INFO",
                "file": "logs/arche.log",
                "max_size_mb": 10,
                "backup_count": 5
            },
            "api_keys": {
                "gemini": None # Should be loaded from env var
            },
            "paths": {
                "outputs": "outputs/",
                "workflows": "workflows/",
                "spr_knowledge_base": "knowledge/sprs.json",
                "token_cache": "outputs/token_cache.json"
            },
            "features": {
                "enable_vetting_agent": True,
                "enable_quantum_simulation": False,
                "use_unified_web_search": False,
            },
            "services": {
                "websocket_bridge": {
                    "host": "localhost",
                    "port": 8765
                },
                "vcd_ui": {
                    "host": "localhost",
                    "port": 5001
                }
            }
        }

    def _override_with_env_vars(self):
        """Overrides specific config keys with environment variables if they exist."""
        # Example for API keys
        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if gemini_api_key:
            self.settings["api_keys"]["gemini"] = gemini_api_key
            logger.info("Loaded GEMINI_API_KEY from environment variable.")

    def _recursive_update(self, base_dict, new_dict):
        """Helper to recursively update a dictionary."""
        for key, value in new_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                base_dict[key] = self._recursive_update(base_dict[key], value)
            else:
                base_dict[key] = value
        return base_dict

    def _create_default_config_file(self):
        """Creates a default config.yaml file if one doesn't exist."""
        try:
            default_config_to_dump = self._get_default_settings()
            # Don't write API keys to the file
            default_config_to_dump['api_keys']['gemini'] = "YOUR_GEMINI_API_KEY_HERE"
            
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(default_config_to_dump, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Created a default config file at '{self.config_path}'. Please review and update it.")
        except Exception as e:
            logger.error(f"Could not create default config file: {e}")

# Global instance
config = Config()


# --- Test Harness ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("\n--- [1] Testing Configuration Loading ---")
    
    # Use a test config file
    test_config_path = "test_config.yaml"
    test_config_content = """
    system:
      name: "ArchE-Test"
    logging:
      level: "DEBUG"
    features:
      enable_quantum_simulation: true
    """
    with open(test_config_path, "w") as f:
        f.write(test_config_content)

    # Set a test environment variable
    os.environ["GEMINI_API_KEY"] = "test_key_from_env"

    # Instantiate the config with the test file
    test_config = Config(config_path=test_config_path)

    print(f"System Name (from YAML): {test_config.get('system.name')}")
    print(f"Logging Level (from YAML): {test_config.get('logging.level')}")
    print(f"System Version (from default): {test_config.get('system.version')}")
    print(f"Gemini Key (from env var): {test_config.get('api_keys.gemini')}")
    print(f"Quantum Feature Flag (from YAML): {test_config.get('features.enable_quantum_simulation')}")
    print(f"Non-existent Key (with default): {test_config.get('a.b.c', 'default_value')}")

    # Clean up
    del os.environ["GEMINI_API_KEY"]
    os.remove(test_config_path)
    
    # Test default file creation
    print("\n--- [2] Testing Default Config File Creation ---")
    default_test_path = "outputs/temp/default_config.yaml"
    if os.path.exists(default_test_path):
        os.remove(default_test_path)

    Config(config_path=default_test_path)
    print(f"Default config file created: {os.path.exists(default_test_path)}")
    if os.path.exists(default_test_path):
        os.remove(default_test_path)


if __name__ == "__main__":
    main()
