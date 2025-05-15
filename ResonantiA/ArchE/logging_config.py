`python
# --- START OF FILE 3.0ArchE/logging_config.py ---
# ResonantiA Protocol v3.0 - logging_config.py
# Centralized logging configuration for Arche.

import logging
import os
from logging.handlers import RotatingFileHandler

# Assuming config.py is in the same directory or accessible in the Python path
# For relative imports if this becomes part of a larger package structure:
# from . import config
# For now, let's try a direct import, assuming it's runnable in an environment
# where 3.0ArchE is in PYTHONPATH or structured as a package that's installed.
try:
    from . import config # Relative import for package structure
except ImportError:
    import config # Fallback for simpler execution context (e.g. script in dir)

def setup_logging():
    \"\"\"
    Configures logging for the application based on settings in config.py.
    \"\"\"
    log_level_str = getattr(config, 'LOG_LEVEL', 'INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    log_format_console = getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_format_file = getattr(config, 'LOG_DETAILED_FORMAT', '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(module)s - %(message)s')
    
    log_file_path = getattr(config, 'LOG_FILE', 'logs/arche_v3_dev.log')
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        
    log_max_bytes = getattr(config, 'LOG_MAX_BYTES', 15*1024*1024)
    log_backup_count = getattr(config, 'LOG_BACKUP_COUNT', 5)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level) # Set root logger level

    # Clear existing handlers to avoid duplicate logging if setup_logging is called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level) # Console handler uses the global log level
    console_formatter = logging.Formatter(log_format_console)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File Handler (Rotating)
    try:
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=log_max_bytes,
            backupCount=log_backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level) # File handler also uses global log level initially (can be more verbose if needed)
        file_formatter = logging.Formatter(log_format_file)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        logging.info(f"File logging configured to: {log_file_path}")
    except Exception as e:
        logging.error(f"Failed to configure file logging to {log_file_path}: {e}", exc_info=True)
        
    logging.info(f"Logging initialized. Level: {log_level_str}, Console Format: '{log_format_console}', File Format: '{log_format_file}'")

if __name__ == '__main__':
    # Example of how to use it:
    # This ensures config has some defaults if run directly (though it should be part of the app)
    class MockConfig:
        LOG_LEVEL = "DEBUG"
        LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
        LOG_DETAILED_FORMAT = '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(module)s - %(message)s'
        LOG_FILE = 'temp_dev_log.log'
        LOG_MAX_BYTES = 1024*1024
        LOG_BACKUP_COUNT = 2

    config = MockConfig()
    setup_logging()
    logging.debug("This is a debug message.")
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    logging.error("This is an error message.")
    logging.critical("This is a critical message.")
    if os.path.exists(config.LOG_FILE):
        print(f"Log file '{config.LOG_FILE}' created with example messages.")

# --- END OF FILE 3.0ArchE/logging_config.py ---