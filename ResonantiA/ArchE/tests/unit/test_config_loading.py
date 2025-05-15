import unittest
import os # Added for os.path.isabs
import logging # Added to check LOG_LEVEL type
import sys

# Determine the path to the '3.0ArchE' directory
# Path of current file: Happier/ResonantiA/3.0ArchE/tests/unit/test_config_loading.py
# Path to 3.0ArchE directory: os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
arche_dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent of '3.0ArchE' (i.e., 'Happier/ResonantiA') to sys.path
# to allow 'from 3.0ArchE import config' if '3.0ArchE' is a package
# However, direct import of '3.0ArchE' is problematic due to its name.
# Instead, add '3.0ArchE' itself to the path so we can just 'import config'
if arche_dir_path not in sys.path:
    sys.path.insert(0, arche_dir_path)

try:
    import config
except ImportError as e:
    # This block might be hit if 'python -m unittest test_config_loading.py' is run from 'tests/unit/'
    # or if the primary sys.path manipulation isn't enough for the execution context.
    # A more robust solution is to ensure tests are run from the project root or that
    # the 3.0ArchE package is properly installed/discoverable.
    print(f"Failed to import config directly. Sys.path: {sys.path}", file=sys.stderr)
    print(f"ImportError: {e}", file=sys.stderr)
    # As a last resort for this specific file structure, try relative import if tests are run as module
    try:
        from ... import config as config_relative
        config = config_relative # Use the relatively imported module
    except ImportError as e_rel:
        print(f"Relative import also failed: {e_rel}", file=sys.stderr)
        raise ImportError("Could not import 'config' module. Ensure 3.0ArchE is in Python path or tests are run correctly.") from e_rel

class TestConfigLoading(unittest.TestCase):

    def test_config_module_imported_successfully(self):
        """Test that the config module can be imported."""
        self.assertTrue(hasattr(config, '__file__'), "config module was not imported successfully.")

    def test_llm_providers_defined_correctly(self):
        """Test that LLM_PROVIDERS is defined and is a dictionary."""
        self.assertTrue(hasattr(config, 'LLM_PROVIDERS'), "LLM_PROVIDERS not found in config.")
        self.assertIsInstance(config.LLM_PROVIDERS, dict, "LLM_PROVIDERS should be a dictionary.")
        self.assertIn("openai", config.LLM_PROVIDERS, "OpenAI provider missing from LLM_PROVIDERS.")

    def test_code_executor_timeout_defined_correctly(self):
        """Test that CODE_EXECUTOR_TIMEOUT is defined and is an integer."""
        self.assertTrue(hasattr(config, 'CODE_EXECUTOR_TIMEOUT'), "CODE_EXECUTOR_TIMEOUT not found in config.")
        self.assertIsInstance(config.CODE_EXECUTOR_TIMEOUT, int, "CODE_EXECUTOR_TIMEOUT should be an integer.")
        self.assertGreater(config.CODE_EXECUTOR_TIMEOUT, 0, "CODE_EXECUTOR_TIMEOUT should be positive.")

    def test_log_level_defined_correctly(self):
        """Test that LOG_LEVEL is defined and is a valid logging level (integer)."""
        self.assertTrue(hasattr(config, 'LOG_LEVEL'), "LOG_LEVEL not found in config.")
        self.assertIsInstance(config.LOG_LEVEL, int, "LOG_LEVEL should be an integer (e.g., logging.INFO).")
        # Check if it's one of the standard logging levels for good measure
        valid_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        self.assertIn(config.LOG_LEVEL, valid_levels, f"LOG_LEVEL {config.LOG_LEVEL} is not a standard logging level.")

    def test_base_dir_defined_correctly(self):
        """Test that BASE_DIR is defined, is a string, and is an absolute path."""
        self.assertTrue(hasattr(config, 'BASE_DIR'), "BASE_DIR not found in config.")
        self.assertIsInstance(config.BASE_DIR, str, "BASE_DIR should be a string.")
        self.assertTrue(os.path.isabs(config.BASE_DIR), f"BASE_DIR '{config.BASE_DIR}' should be an absolute path.")
        self.assertTrue(os.path.exists(config.BASE_DIR), f"BASE_DIR '{config.BASE_DIR}' path does not exist.")

    # Original placeholder test - can be removed or kept
    def test_config_loads_successfully_generic(self):
        """
        Original generic test that the configuration loads without critical errors.
        This is somewhat redundant with test_config_module_imported_successfully.
        """
        try:
            # This just re-confirms import works
            from ... import config as app_config # Re-check import within test
            self.assertIsNotNone(app_config)
        except ImportError:
            self.fail("config.py could not be imported or is missing.")
        self.assertTrue(True)

    # Add more specific tests for config values below
    # def test_specific_api_key_present(self):
    #     from .... import config as app_config
    #     self.assertIsNotNone(app_config.API_KEY, "API_KEY should be defined in config.")
    #     self.assertIsInstance(app_config.API_KEY, str, "API_KEY should be a string.")

if __name__ == '__main__':
    unittest.main() 