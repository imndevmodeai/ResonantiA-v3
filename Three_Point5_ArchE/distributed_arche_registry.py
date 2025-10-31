import logging
import json
import time
from pathlib import Path
from threading import Lock, Thread
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class DistributedArcheRegistry:
    """
    The Decentralized Directory for a multi-node ArchE deployment. This registry
    manages the registration and discovery of various ArchE services (e.g., tool
    providers, workflow engines) across a network.

    This implementation uses a simple file-based backend for service discovery,
    which is suitable for single-host or small-scale deployments and can be
    extended to use a proper distributed key-value store like etcd or Consul
    for true multi-node scalability.
    """

    def __init__(self, registry_file_path: str = "outputs/service_registry.json", ttl_seconds: int = 60):
        """
        Initializes the DistributedArcheRegistry.

        Args:
            registry_file_path (str): Path to the file used for service registration.
            ttl_seconds (int): Time-to-live for a service registration. If a service
                               doesn't heartbeat within this time, it's considered stale.
        """
        self.registry_file = Path(registry_file_path)
        self.ttl = ttl_seconds
        self._lock = Lock()
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._load_registry()
        
        # Start a background thread to periodically clean up stale services
        self._stale_cleanup_thread = Thread(target=self._cleanup_loop, daemon=True)
        self._stale_cleanup_thread.start()
        
        logger.info(f"[Registry] Initialized with file backend at '{self.registry_file}' and TTL of {self.ttl}s.")

    def _load_registry(self):
        """Loads the service registry from the file."""
        with self._lock:
            try:
                if self.registry_file.exists():
                    with open(self.registry_file, 'r', encoding='utf-8') as f:
                        self._registry = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to load service registry: {e}", exc_info=True)
                self._registry = {}

    def _persist_registry(self):
        """Persists the current state of the registry to the file."""
        with self._lock:
            try:
                self.registry_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    json.dump(self._registry, f, indent=2)
            except IOError as e:
                logger.error(f"Failed to persist service registry: {e}", exc_info=True)

    def register_service(self, service_id: str, service_type: str, endpoint: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Registers a service with the directory.

        Args:
            service_id (str): A unique identifier for the service instance.
            service_type (str): The type of service (e.g., 'workflow_engine', 'llm_tool_provider').
            endpoint (str): The network address of the service (e.g., 'http://localhost:8001').
            metadata (dict, optional): Additional data about the service.

        Returns:
            True if registration was successful, False otherwise.
        """
        with self._lock:
            self._registry[service_id] = {
                "service_type": service_type,
                "endpoint": endpoint,
                "metadata": metadata or {},
                "last_heartbeat_ts": time.time()
            }
        self._persist_registry()
        logger.info(f"Service '{service_id}' of type '{service_type}' registered with endpoint '{endpoint}'.")
        return True

    def deregister_service(self, service_id: str) -> bool:
        """Removes a service from the directory."""
        with self._lock:
            if service_id in self._registry:
                del self._registry[service_id]
                self._persist_registry()
                logger.info(f"Service '{service_id}' deregistered.")
                return True
            logger.warning(f"Attempted to deregister non-existent service '{service_id}'.")
            return False

    def discover_service(self, service_type: str) -> Optional[Dict[str, Any]]:
        """
        Discovers a single, healthy instance of a given service type.
        (Simple strategy: returns the first one found).
        """
        with self._lock:
            for service_id, info in self._registry.items():
                if info.get("service_type") == service_type:
                    # In a real scenario, you'd also check health here
                    return info
        return None
        
    def discover_all_services(self, service_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Discovers all healthy instances of a given service type, or all services if type is None.
        """
        with self._lock:
            services = self._registry.values()
            if service_type:
                return [info for info in services if info.get("service_type") == service_type]
            return list(services)

    def heartbeat(self, service_id: str) -> bool:
        """Allows a service to signal that it is still alive."""
        with self._lock:
            if service_id in self._registry:
                self._registry[service_id]['last_heartbeat_ts'] = time.time()
                self._persist_registry()
                logger.debug(f"Heartbeat received from service '{service_id}'.")
                return True
            logger.warning(f"Heartbeat from unknown service '{service_id}'.")
            return False

    def _cleanup_stale_services(self):
        """Removes services that have not sent a heartbeat within the TTL."""
        with self._lock:
            now = time.time()
            stale_services = [
                service_id for service_id, info in self._registry.items()
                if (now - info.get("last_heartbeat_ts", 0)) > self.ttl
            ]
            
            if stale_services:
                logger.info(f"Cleaning up {len(stale_services)} stale service(s): {stale_services}")
                for service_id in stale_services:
                    del self._registry[service_id]
                self._persist_registry()

    def _cleanup_loop(self):
        """The main loop for the background cleanup thread."""
        while True:
            time.sleep(self.ttl / 2) # Check for stale services periodically
            self._cleanup_stale_services()


# --- Test Harness ---
def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    test_registry_file = "outputs/test_registry.json"
    if Path(test_registry_file).exists():
        Path(test_registry_file).unlink()

    # Use a short TTL for testing
    registry = DistributedArcheRegistry(registry_file_path=test_registry_file, ttl_seconds=3)

    print("\n--- [1] Registering services ---")
    registry.register_service("wf_engine_1", "workflow_engine", "localhost:8001", {"region": "us-east-1"})
    registry.register_service("llm_provider_1", "llm_tool_provider", "localhost:8002", {"model": "gemini-1.5-pro"})
    registry.register_service("llm_provider_2", "llm_tool_provider", "localhost:8003", {"model": "gemini-1.0-ultra"})

    print("\n--- [2] Discovering services ---")
    llm_service = registry.discover_service("llm_tool_provider")
    print(f"Discovered a single LLM provider: {llm_service['endpoint']} (Model: {llm_service['metadata']['model']})")

    all_llm_services = registry.discover_all_services("llm_tool_provider")
    print(f"Found {len(all_llm_services)} total LLM providers.")
    assert len(all_llm_services) == 2
    
    print("\n--- [3] Testing Heartbeat and Stale Service Cleanup ---")
    print("Sending heartbeat for wf_engine_1...")
    registry.heartbeat("wf_engine_1")
    
    print("Waiting for 4 seconds (longer than TTL of 3s) for other services to become stale...")
    time.sleep(4)
    
    # The cleanup thread runs automatically, but we can trigger it manually for a predictable test
    registry._cleanup_stale_services()
    
    all_services = registry.discover_all_services()
    print(f"Total services remaining after cleanup: {len(all_services)}")
    assert len(all_services) == 1
    assert all_services[0]['endpoint'] == "localhost:8001"
    print(f"Remaining service: {all_services[0]}")
    
    # Clean up
    if Path(test_registry_file).exists():
        Path(test_registry_file).unlink()


if __name__ == "__main__":
    main()
