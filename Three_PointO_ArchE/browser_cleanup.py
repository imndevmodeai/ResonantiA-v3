"""
Browser Process Cleanup Utility
Ensures orphaned browser processes are terminated on exit or signal.
"""

import atexit
import signal
import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def cleanup_browser_processes():
    """
    Cleanup any remaining browser processes (Chrome/Chromium).
    This is a safety net for orphaned processes that weren't properly closed.
    """
    try:
        # Kill any orphaned Chrome/Chromium processes (headless or regular)
        # Only kill processes that appear to be automation-related
        cleanup_commands = [
            "pkill -f 'chrome.*--headless' 2>/dev/null || true",
            "pkill -f 'chromium.*--headless' 2>/dev/null || true",
            # More aggressive: kill any Chrome/Chromium processes started by this user
            # (comment out if you want to be more conservative)
            # "pkill -u $(whoami) -f 'chrome|chromium' 2>/dev/null || true",
        ]
        
        for cmd in cleanup_commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.debug(f"Executed cleanup command: {cmd}")
            except subprocess.TimeoutExpired:
                logger.warning(f"Cleanup command timed out: {cmd}")
            except Exception as e:
                logger.debug(f"Cleanup command failed (non-critical): {cmd}, {e}")
        
        logger.info("Browser process cleanup completed")
    except Exception as e:
        logger.warning(f"Error during browser process cleanup: {e}")

def register_cleanup_handlers():
    """Register cleanup handlers for process exit and signals."""
    # Register cleanup on normal exit
    atexit.register(cleanup_browser_processes)
    
    # Register cleanup on termination signals
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, cleaning up browser processes...")
        cleanup_browser_processes()
        # Re-raise the signal to allow normal termination
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
    
    try:
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        logger.debug("Browser cleanup handlers registered")
    except (ValueError, OSError) as e:
        # Signals might not be available in all environments (e.g., Windows)
        logger.debug(f"Could not register signal handlers: {e}")

# Auto-register on import
register_cleanup_handlers()


