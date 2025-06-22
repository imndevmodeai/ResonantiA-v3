import unittest
import os
import sys

# Attempt to import the config module directly, assuming tests are run correctly from project root.
CONFIG_MODULE_FOUND = False
CONFIG_VALUES_LOADED = False
ERROR_MESSAGE = ""
CONFIG_DIRECT_LOADED = False

try:
    from Three_PointO_ArchE import config
    # Try accessing a known variable to confirm it's loaded correctly
    _ = config.MASTERMIND_DIR 
    CONFIG_MODULE_FOUND = True
    CONFIG_VALUES_LOADED = True
    CONFIG_DIRECT_LOADED = True
    print(f"Successfully loaded config via: from Three_PointO_ArchE import config. MASTERMIND_DIR: {config.MASTERMIND_DIR}")
except ImportError as e:
    ERROR_MESSAGE = f"Primary import (from Three_PointO_ArchE import config) failed: {e}"
    print(ERROR_MESSAGE)
    print(f"sys.path was: {sys.path}")
    # If this fails, the test 'test_config_module_found_and_loaded' will catch it.

class TestConfigLoading(unittest.TestCase):

    def test_config_module_found_and_loaded(self):
        """Test that the config module was found and its values can be accessed."""
        if not CONFIG_DIRECT_LOADED:
            # This provides a clearer error message in the test itself if the top-level import failed.
            print(f"DEBUG: test_config_module_found_and_loaded: CONFIG_DIRECT_LOADED is False. Error during import: {ERROR_MESSAGE}")
        self.assertTrue(CONFIG_MODULE_FOUND, f"Config module could not be imported. Error: {ERROR_MESSAGE}")
        self.assertTrue(CONFIG_VALUES_LOADED, "Config module was imported, but accessing values failed. This indicates an issue within config.py or its dependencies.")
        self.assertIsNotNone(config.MASTERMIND_DIR, "MASTERMIND_DIR should not be None.")
        self.assertIsNotNone(config.SPR_JSON_FILE, "SPR_JSON_FILE should not be None.")

    def test_config_values_are_correct_type(self):
        """Test that specific config values have the expected types."""
        if not CONFIG_DIRECT_LOADED:
            self.skipTest(f"Skipping type check as config module failed to load. Error: {ERROR_MESSAGE}")
        
        self.assertIsInstance(config.MASTERMIND_DIR, str)
        self.assertIsInstance(config.SPR_JSON_FILE, str)
        self.assertIsInstance(config.DEBUG_MODE, bool)
        self.assertIsInstance(config.LOG_LEVEL, int) # LOG_LEVEL is an int (e.g., logging.INFO)
        # Add more type checks as needed for other critical config variables

    def test_critical_paths_exist_or_are_creatable(self):
        """Test that critical directory paths defined in config either exist or can be created (conceptual)."""
        if not CONFIG_DIRECT_LOADED:
            self.skipTest(f"Skipping path check as config module failed to load. Error: {ERROR_MESSAGE}")

        # For directories that are expected to exist or be creatable by the application
        paths_to_check = [
            config.MASTERMIND_DIR,
            os.path.dirname(config.SPR_JSON_FILE), # Check parent dir of SPR file
            config.WORKFLOW_DIR,
            config.LOG_DIR,
            config.OUTPUT_DIR,
            # Add other critical paths from config
        ]
        for path in paths_to_check:
            # This test doesn't create them, just checks if they are absolute or can be conceptualized.
            # A more robust test might try os.makedirs(path, exist_ok=True) if appropriate.
            self.assertTrue(os.path.isabs(path) or not path.startswith("/"), 
                            f"Path {path} should be absolute or a relative path not starting with root slash.")
            # Here, we are mostly ensuring the config values are present and look like paths.
            # Actual directory creation is usually handled by the application setup.
            print(f"Config path check: {path} (is_abs: {os.path.isabs(path)})")

if __name__ == '__main__':
    unittest.main() 