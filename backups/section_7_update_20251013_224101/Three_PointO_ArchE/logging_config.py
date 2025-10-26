# --- START OF FILE 3.0ArchE/logging_config.py ---
# ResonantiA Protocol v3.0 - logging_config.py
# Configures the Python standard logging framework for Arche.
# Reads settings from config.py for levels, file paths, and formats.

import logging
import logging.config
import os
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig: LOG_LEVEL=logging.INFO; LOG_FILE='logs/arche_fallback_log.log'; LOG_DIR='logs'; LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'; LOG_DETAILED_FORMAT='%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(module)s - %(message)s'; LOG_MAX_BYTES=10*1024*1024; LOG_BACKUP_COUNT=3
    config = FallbackConfig(); logging.warning("config.py not found for logging_config, using fallback configuration.")

# --- Logging Configuration Dictionary ---
# Reads settings from the main config module

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False, # Keep existing loggers (e.g., from libraries)
    "formatters": {
        # Formatter for console output (simpler)
        "standard": {
            "format": getattr(config, 'LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        # Formatter for file output (more detailed)
        "detailed": {
            "format": getattr(config, 'LOG_DETAILED_FORMAT', '%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(module)s - %(message)s'),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        # Console Handler (outputs to stderr by default)
        "console": {
            "level": getattr(config, 'LOG_LEVEL', logging.INFO), # Use level from config
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr", # Explicitly direct to stderr
        },
        # Rotating File Handler (writes to log file, rotates when size limit reached)
        "file": {
            "level": getattr(config, 'LOG_LEVEL', logging.INFO), # Use level from config
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": getattr(config, 'LOG_FILE', 'logs/arche_v3_default.log'), # Log file path from config
            "maxBytes": getattr(config, 'LOG_MAX_BYTES', 15*1024*1024), # Max size from config (15MB default)
            "backupCount": getattr(config, 'LOG_BACKUP_COUNT', 5), # Number of backups from config
            "encoding": "utf-8",
        },
    },
    "loggers": {
        # Root logger configuration
        "root": {
            "level": getattr(config, 'LOG_LEVEL', logging.INFO), # Root level from config
            "handlers": ["console", "file"], # Apply both handlers to the root logger
            # "propagate": True # Propagate messages to ancestor loggers (usually not needed for root)
        },
        # Example: Quieter logging for noisy libraries if needed
        # "noisy_library_name": {
        #     "level": logging.WARNING, # Set higher level for specific libraries
        #     "handlers": ["console", "file"],
        #     "propagate": False # Prevent messages from reaching root logger
        # },
        "openai": { # Example: Quieter logging for OpenAI library specifically
            "level": logging.WARNING,
            "handlers": ["console", "file"],
            "propagate": False
        },
         "google": { # Example: Quieter logging for Google library specifically
            "level": logging.WARNING,
            "handlers": ["console", "file"],
            "propagate": False
        },
         "urllib3": { # Often noisy with connection pool messages
            "level": logging.WARNING,
            "handlers": ["console", "file"],
            "propagate": False
        }
    }
}

def setup_logging():
    """Applies the logging configuration."""
    try:
        # Ensure the log directory exists before configuring file handler
        log_dir = getattr(config, 'LOG_DIR', 'logs')
        if log_dir: # Check if log_dir is configured and not empty
            os.makedirs(log_dir, exist_ok=True)
        else:
            # Handle case where LOG_DIR might be None or empty in config
            # Default to creating 'logs' in the current directory or handle as error
            default_log_dir = 'logs'
            print(f"Warning: LOG_DIR not configured or empty in config.py. Attempting to use default '{default_log_dir}'.")
            os.makedirs(default_log_dir, exist_ok=True)
            # Update the filename in the config dict if LOG_DIR was missing
            if 'filename' in LOGGING_CONFIG['handlers']['file']:
                log_filename = os.path.basename(LOGGING_CONFIG['handlers']['file']['filename'])
                LOGGING_CONFIG['handlers']['file']['filename'] = os.path.join(default_log_dir, log_filename)

        # Apply the configuration dictionary
        logging.config.dictConfig(LOGGING_CONFIG)
        logging.info("--- Logging configured successfully (ResonantiA v3.0) ---")
        logging.info(f"Log Level: {logging.getLevelName(getattr(config, 'LOG_LEVEL', logging.INFO))}")
        logging.info(f"Log File: {LOGGING_CONFIG['handlers']['file']['filename']}")
    except Exception as e:
        # Fallback to basic config if dictionary config fails
        logging.basicConfig(level=logging.WARNING) # Use WARNING to avoid flooding console
        logging.critical(f"CRITICAL: Failed to configure logging using dictConfig: {e}. Falling back to basic config.", exc_info=True)

# --- END OF FILE 3.0ArchE/logging_config.py --- 