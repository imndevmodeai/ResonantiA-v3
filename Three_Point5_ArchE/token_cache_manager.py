import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class TokenCacheManager:
    """
    The Alchemist's Vault. Manages the counting, caching, and analysis of LLM token usage
    to provide crucial data for cost estimation, rate limit adherence, and context window
    management. This tool is essential for maintaining operational efficiency and
    preventing costly overruns.
    """

    def __init__(self, cache_path: str = "outputs/token_cache.json", persist_interval_seconds: int = 300):
        """
        Initializes the TokenCacheManager.

        Args:
            cache_path (str): The file path to persist the token cache.
            persist_interval_seconds (int): How often to automatically save the cache to disk.
        """
        self.cache_path = Path(cache_path)
        self.persist_interval = timedelta(seconds=persist_interval_seconds)
        self.last_persist_time = datetime.utcnow()
        self._lock = Lock()
        self.cache: Dict[str, Any] = {
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "schema_version": "1.0"
            },
            "usage_by_model": {},
            "usage_by_workflow": {},
            "daily_totals": {}
        }
        self._load_cache()
        logger.info(f"[TokenCacheManager] Initialized. Cache loaded from '{self.cache_path}'. Persisting every {self.persist_interval.total_seconds()}s.")

    def _load_cache(self):
        """Loads the token cache from the specified file path if it exists."""
        with self._lock:
            try:
                if self.cache_path.exists():
                    with open(self.cache_path, 'r', encoding='utf-8') as f:
                        loaded_cache = json.load(f)
                        # Basic validation
                        if isinstance(loaded_cache, dict) and "metadata" in loaded_cache:
                            self.cache = loaded_cache
                            logger.info(f"Successfully loaded token cache from {self.cache_path}")
                        else:
                            logger.warning("Token cache file is malformed. Starting with a fresh cache.")
                else:
                    logger.info("No existing token cache found. Starting with a fresh cache.")
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load token cache from {self.cache_path}: {e}. Starting fresh.", exc_info=True)

    def _persist_cache(self, force: bool = False):
        """
        Persists the current token cache to the file path.
        By default, it only persists if the interval has elapsed.
        
        Args:
            force (bool): If True, forces a save regardless of the time interval.
        """
        now = datetime.utcnow()
        if not force and (now - self.last_persist_time) < self.persist_interval:
            return

        with self._lock:
            try:
                self.cache['metadata']['last_updated'] = now.isoformat()
                self.cache_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cache_path, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, indent=2)
                self.last_persist_time = now
                logger.info(f"Token cache persisted to {self.cache_path}")
            except (IOError, TypeError) as e:
                logger.error(f"Failed to persist token cache: {e}", exc_info=True)

    def log_usage(self, model_name: str, workflow_name: str, prompt_tokens: int, completion_tokens: int, total_tokens: int):
        """
        Logs a new token usage event, updating all relevant metrics.

        Args:
            model_name (str): The name of the LLM used (e.g., 'gemini-1.5-pro-latest').
            workflow_name (str): The name of the workflow that triggered the usage.
            prompt_tokens (int): The number of tokens in the prompt.
            completion_tokens (int): The number of tokens in the completion.
            total_tokens (int): The total number of tokens for the API call.
        """
        if not all(isinstance(x, int) and x >= 0 for x in [prompt_tokens, completion_tokens, total_tokens]):
            logger.warning("Invalid token counts provided. All counts must be non-negative integers. Skipping log.")
            return

        with self._lock:
            now = datetime.utcnow()
            today_str = now.strftime('%Y-%m-%d')

            # Update usage by model
            model_stats = self.cache['usage_by_model'].setdefault(model_name, self._get_default_stats())
            self._update_stats(model_stats, prompt_tokens, completion_tokens, total_tokens, now)

            # Update usage by workflow
            workflow_stats = self.cache['usage_by_workflow'].setdefault(workflow_name, self._get_default_stats())
            self._update_stats(workflow_stats, prompt_tokens, completion_tokens, total_tokens, now)

            # Update daily totals
            daily_stats = self.cache['daily_totals'].setdefault(today_str, self._get_default_stats())
            self._update_stats(daily_stats, prompt_tokens, completion_tokens, total_tokens, now)

        logger.info(f"Logged {total_tokens} tokens for model '{model_name}' in workflow '{workflow_name}'.")
        self._persist_cache() # Attempt to persist after logging

    def get_summary(self) -> Dict[str, Any]:
        """
        Retrieves a summary of token usage across all tracked categories.

        Returns:
            A dictionary containing summaries for models, workflows, and daily totals.
        """
        with self._lock:
            # Return a deep copy to prevent modification of the internal cache
            return json.loads(json.dumps(self.cache))

    def check_usage_limit(self, limit_type: str, identifier: str, threshold: int, time_window_hours: int = 24) -> Tuple[bool, Dict[str, Any]]:
        """
        Checks if a specific usage metric is within a defined threshold.
        (This is a conceptual check; real rate limiting requires more sophisticated tracking).

        Args:
            limit_type (str): The category to check ('model', 'workflow', 'daily').
            identifier (str): The specific model, workflow, or date ('YYYY-MM-DD') to check.
            threshold (int): The token threshold to check against.
            time_window_hours (int): Not implemented yet, defaults to daily check.

        Returns:
            A tuple containing:
            - bool: True if usage is under the limit, False otherwise.
            - dict: Details of the check (current usage, threshold, status).
        """
        with self._lock:
            usage_data = None
            if limit_type == 'model':
                usage_data = self.cache['usage_by_model'].get(identifier)
            elif limit_type == 'workflow':
                usage_data = self.cache['usage_by_workflow'].get(identifier)
            elif limit_type == 'daily':
                usage_data = self.cache['daily_totals'].get(identifier)
            else:
                return False, {"error": f"Invalid limit_type: {limit_type}"}

            if usage_data is None:
                return True, {"identifier": identifier, "usage": 0, "threshold": threshold, "status": "under_limit"}

            current_usage = usage_data.get("total_tokens", 0)
            is_under_limit = current_usage < threshold
            
            return is_under_limit, {
                "identifier": identifier,
                "usage": current_usage,
                "threshold": threshold,
                "status": "under_limit" if is_under_limit else "over_limit"
            }

    def _get_default_stats(self) -> Dict[str, Any]:
        """Returns a default dictionary structure for tracking statistics."""
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "call_count": 0,
            "first_call_utc": None,
            "last_call_utc": None
        }

    def _update_stats(self, stats_dict: Dict[str, Any], prompt: int, completion: int, total: int, timestamp: datetime):
        """Helper function to update a statistics dictionary."""
        stats_dict["prompt_tokens"] += prompt
        stats_dict["completion_tokens"] += completion
        stats_dict["total_tokens"] += total
        stats_dict["call_count"] += 1
        iso_timestamp = timestamp.isoformat()
        if stats_dict["first_call_utc"] is None:
            stats_dict["first_call_utc"] = iso_timestamp
        stats_dict["last_call_utc"] = iso_timestamp

# Main entry point for the tool to be registered in the action_registry
def manage_token_cache(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Action to interact with the TokenCacheManager.

    Args:
        inputs (Dict[str, Any]): A dictionary defining the operation.
            'operation' (str): The action to perform ('log', 'get_summary', 'check_limit').
            ... other args depending on operation ...

    Returns:
        Dict[str, Any]: A dictionary with the result of the operation and an IAR reflection.
    """
    # In a real system, the manager would likely be a singleton instance.
    # For this tool, we instantiate it each time for simplicity and statelessness between calls.
    manager = TokenCacheManager()
    operation = inputs.get("operation")
    
    result_data = {}
    reflection = {"status": "failure", "potential_issues": []}

    try:
        if operation == "log":
            manager.log_usage(
                model_name=inputs["model_name"],
                workflow_name=inputs["workflow_name"],
                prompt_tokens=inputs["prompt_tokens"],
                completion_tokens=inputs["completion_tokens"],
                total_tokens=inputs["total_tokens"]
            )
            result_data = {"status": "log_successful"}
            reflection["status"] = "success"
        
        elif operation == "get_summary":
            result_data = manager.get_summary()
            reflection["status"] = "success"

        elif operation == "check_limit":
            is_under, details = manager.check_usage_limit(
                limit_type=inputs["limit_type"],
                identifier=inputs["identifier"],
                threshold=inputs["threshold"]
            )
            result_data = {"is_under_limit": is_under, "details": details}
            reflection["status"] = "success"

        else:
            result_data = {"error": f"Invalid operation: {operation}"}
            reflection["potential_issues"].append(f"Unsupported operation '{operation}' requested.")

    except KeyError as e:
        error_msg = f"Missing required input for operation '{operation}': {e}"
        result_data = {"error": error_msg}
        reflection["potential_issues"].append(error_msg)
    except Exception as e:
        error_msg = f"An unexpected error occurred in TokenCacheManager: {e}"
        result_data = {"error": error_msg}
        reflection["potential_issues"].append(error_msg)
        logger.error(error_msg, exc_info=True)

    manager._persist_cache(force=True) # Force save on exit
    return {"result": result_data, "reflection": reflection}

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    print("--- Token Cache Manager Test Harness ---")
    
    # Use a temporary cache file for testing
    test_cache_file = "outputs/test_token_cache.json"
    if Path(test_cache_file).exists():
        Path(test_cache_file).unlink()

    # Instantiate manager
    tcm = TokenCacheManager(cache_path=test_cache_file, persist_interval_seconds=5)

    # Log some usage
    print("\n[1] Logging usage...")
    tcm.log_usage("gemini-1.5-pro", "AnalyticsWorkflow", 1500, 350, 1850)
    tcm.log_usage("gemini-1.5-pro", "AnalyticsWorkflow", 2000, 500, 2500)
    tcm.log_usage("gemini-1.0-pro", "SimpleQuery", 100, 50, 150)
    tcm.log_usage("gemini-1.5-pro", "CodeGeneration", 4000, 800, 4800)

    # Get summary
    print("\n[2] Getting summary...")
    summary = tcm.get_summary()
    print(json.dumps(summary, indent=2))

    # Check limit
    print("\n[3] Checking limits...")
    under, details = tcm.check_usage_limit("model", "gemini-1.5-pro", 10000)
    print(f"  gemini-1.5-pro under 10000 limit? {under} -> {details}")
    
    under, details = tcm.check_usage_limit("model", "gemini-1.5-pro", 5000)
    print(f"  gemini-1.5-pro under 5000 limit? {under} -> {details}")

    under, details = tcm.check_usage_limit("workflow", "AnalyticsWorkflow", 4000)
    print(f"  AnalyticsWorkflow under 4000 limit? {under} -> {details}")

    # Test persistence
    print("\n[4] Forcing persistence...")
    tcm._persist_cache(force=True)
    print(f"  Cache file exists: {Path(test_cache_file).exists()}")

    # Clean up
    if Path(test_cache_file).exists():
        Path(test_cache_file).unlink()
        print(f"\nCleaned up test cache file: {test_cache_file}")

    print("\n--- Test Harness Complete ---")
