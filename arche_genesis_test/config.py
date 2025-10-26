
# Three_PointO_ArchE/config.py

import os
import sys
from pathlib import Path
from types import SimpleNamespace

class Config:
    """
    Central configuration object for the ArchE system.

    This class encapsulates all operational parameters, providing a single,
    unambiguous source of truth. It is designed to be a singleton, instantiated
    once and imported by all other modules. It uses nested SimpleNamespace
    objects to create a clean, hierarchical, and attribute-accessible structure.

    This file is a primary enabler of the `Implementation resonancE` SPR,
    allowing system behavior to be centrally managed and easily modified to
    align the code's behavior with strategic intent.
    """

    def __init__(self):
        """
        Initializes the configuration by loading settings.

        Settings are loaded from environment variables where available,
        falling back to default values. This is a security best practice
        to avoid hardcoding secrets like API keys. It also creates
        necessary directories on startup.
        """
        # --- Paths Configuration ---
        self.paths = SimpleNamespace()
        # The base directory is the parent of this file's location.
        # Per spec: `Three_PointO_ArchE/config.py`
        self.paths.base = Path(__file__).resolve().parent
        self.paths.workflows = self.paths.base / "workflows"
        self.paths.knowledge_graph = self.paths.base / "knowledge_graph"
        self.paths.logs = self.paths.base / "logs"
        self.paths.output = self.paths.base / "output"

        # --- LLM Configuration ---
        self.llm = SimpleNamespace()
        self.llm.default_provider = "gemini"
        self.llm.default_model = "gemini-1.5-pro-latest"
        self.llm.temperature = 0.7
        self.llm.max_tokens = 8192
        # Critical: Load API key from environment for security
        self.llm.api_key = os.environ.get("GEMINI_API_KEY")  # Returns None if not set

        # --- Tools Configuration ---
        self.tools = SimpleNamespace()
        self.tools.web_search = SimpleNamespace(timeout=15)  # seconds
        self.tools.code_executor = SimpleNamespace(timeout=60)  # seconds

        # --- System Configuration ---
        self.system = SimpleNamespace()
        # This flag directly implements the `Keyholder OverridE` SPR.
        self.system.keyholder_override_active = os.environ.get(
            "KEYHOLDER_OVERRIDE", "False"
        ).lower() in ('true', '1', 't')
        self.system.debug_mode = os.environ.get(
            "DEBUG_MODE", "False"
        ).lower() in ('true', '1', 't')

        # --- Logging Configuration ---
        self.logging = SimpleNamespace()
        self.logging.log_level = "DEBUG" if self.system.debug_mode else "INFO"
        self.logging.log_file = self.paths.logs / "arche_system.log"

        # --- Initialization Side-Effects ---
        self._create_directories()

    def _create_directories(self):
        """
        Creates all necessary directories defined in the paths config.

        This is a helper method called during initialization to ensure the
        filesystem structure required by the application exists.
        """
        try:
            for _, path_obj in self.paths.__dict__.items():
                if isinstance(path_obj, Path):
                    path_obj.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            # If directories can't be created, it's a critical failure.
            print(
                f"FATAL: Could not create required directory: {e.filename}. "
                f"Error: {e.strerror}",
                file=sys.stderr
            )
            sys.exit(1)


# --- Singleton Instance Creation ---
# This is the global configuration object that should be imported by other modules.
_config_instance = Config()


def get_config() -> Config:
    """
    Returns the global singleton instance of the Config class.

    This function ensures that every module in the system accesses the exact
    same configuration state, preventing inconsistencies.

    Returns:
        Config: The singleton configuration object.
    """
    return _config_instance


# For direct import convenience: from Three_PointO_ArchE.config import CONFIG
CONFIG = get_config()


# --- Self-validation and warning for missing API key ---
if not CONFIG.llm.api_key:
    # This is a runtime warning, not an exception, to allow the system
    # to potentially run in a limited capacity or for non-LLM tasks.
    print(
        "WARNING: GEMINI_API_KEY environment variable not set. "
        "LLM-related functionality will be disabled.",
        file=sys.stderr
    )
