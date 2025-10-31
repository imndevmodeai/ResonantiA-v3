# ResonantiA Protocol v2.9.5 - logging_config.py
# Configures logging for the Arche system.

import logging
import logging.handlers
import os
import sys

# Import config carefully
try:
    from mastermind_ai_v2_9 import config
except ImportError:
    # Fallback config if running standalone or config import fails
    class FallbackConfig:
        LOG_LEVEL = logging.INFO
        LOG_DIR = "logs"
        LOG_FILE = "arche_log.log" # Keep consistent base name
        LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        LOG_MAX_BYTES = 10*1024*1024 # 10MB
        LOG_BACKUP_COUNT = 3
    config = FallbackConfig()
    logging.warning("Using fallback logging config for setup.")

# Use absolute path for log file based on LOG_DIR
log_file_path = os.path.join(config.LOG_DIR, os.path.basename(config.LOG_FILE))

def setup_logging():
    """Sets up the root logger with handlers and formatters."""
    log_level = getattr(config, 'LOG_LEVEL', logging.INFO) # Default to INFO
    log_format = getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_max_bytes = getattr(config, 'LOG_MAX_BYTES', 10*1024*1024)
    log_backup_count = getattr(config, 'LOG_BACKUP_COUNT', 3)

    # Ensure log directory exists
    try:
        if config.LOG_DIR:
             os.makedirs(config.LOG_DIR, exist_ok=True)
    except OSError as e:
        # Log initial error to stderr if directory creation fails
        sys.stderr.write(f"CRITICAL: Failed to create log directory {config.LOG_DIR}: {e}. Log file may not be written.\\n")
        # Fallback to logging only to console if directory fails?

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level) # Set the minimum level for the root logger

    # Clear existing handlers to avoid duplicate logging if setup is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(log_format)

    # --- Console Handler --- #
    console_handler = logging.StreamHandler(sys.stdout)
    # Set console handler level (can be different from root, e.g., INFO for console, DEBUG for file)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # --- Rotating File Handler --- #
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding='utf-8' # Specify encoding
        )
        # Set file handler level (often set to DEBUG to capture more details)
        file_handler.setLevel(logging.DEBUG if log_level == logging.DEBUG else logging.INFO) # Example: DEBUG if root is DEBUG, else INFO
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        # Log initialization success to the file itself
        root_logger.info(f"Logging setup complete. Level={logging.getLevelName(log_level)}, File='{log_file_path}'")

    except IOError as e:
        root_logger.error(f"Failed to create or write to log file {log_file_path}: {e}", exc_info=True)
    except Exception as e:
         root_logger.critical(f"Unexpected error setting up file logger: {e}", exc_info=True)


# Example: Call setup_logging() when this module is imported?
# Or more commonly, call it explicitly from the main entry point (e.g., main.py).
# For simplicity here, we don't call it automatically on import.

if __name__ == "__main__":
    print("Setting up logging via logging_config.py (standalone test)...")
    setup_logging()
    # Test logging
    logging.debug("This is a debug message (should appear in file).")
    logging.info("This is an info message (should appear in console and file).")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
    print(f"Check console output and log file at: {log_file_path}")
