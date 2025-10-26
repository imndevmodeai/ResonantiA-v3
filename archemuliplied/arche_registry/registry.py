import threading
import time
from typing import Dict, Any, List

class ArchERegistry:
    """
    Manages a distributed network of heterogeneous ArchE instances,
    as defined by the Conceptual Arche instance registrY protocoL (Section 3.17).
    """

    def __init__(self):
        self._instances: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        print("ArchE Registry initialized.")

    def register_instance(self, instance_id: str, capabilities: Dict[str, Any], address: str) -> Dict[str, Any]:
        """
        Registers a new ArchE instance with the collective.

        Args:
            instance_id: A unique identifier for the instance.
            capabilities: A dictionary describing the instance's capabilities,
                          conforming to the Capability Classification System.
            address: The network address for communicating with the instance.

        Returns:
            A dictionary containing the status of the registration.
        """
        with self._lock:
            if instance_id in self._instances:
                print(f"Instance {instance_id} already registered. Updating.")
            
            self._instances[instance_id] = {
                "instance_id": instance_id,
                "capabilities": capabilities,
                "address": address,
                "status": "active",
                "registered_at": time.time()
            }
            
            print(f"Instance {instance_id} registered successfully at {address}.")
            return {"status": "success", "instance_id": instance_id}

    def list_instances(self) -> List[Dict[str, Any]]:
        """
        Lists all currently registered and active instances.

        Returns:
            A list of dictionaries, each representing a registered instance.
        """
        with self._lock:
            # Return a copy to prevent modification of internal state
            return list(self._instances.values())

    def get_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Retrieves the details of a specific instance.

        Args:
            instance_id: The ID of the instance to retrieve.

        Returns:
            A dictionary containing the instance details, or an empty dictionary if not found.
        """
        with self._lock:
            # Return a copy
            return self._instances.get(instance_id, {}).copy()

    def unregister_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Removes an instance from the registry.

        Args:
            instance_id: The ID of the instance to unregister.

        Returns:
            A dictionary containing the status of the unregistration.
        """
        with self._lock:
            if instance_id in self._instances:
                del self._instances[instance_id]
                print(f"Instance {instance_id} unregistered.")
                return {"status": "success", "instance_id": instance_id}
            else:
                print(f"Instance {instance_id} not found for unregistration.")
                return {"status": "error", "message": "Instance not found"}

    def clear(self):
        """
        Clears all instances from the registry. Used for testing and reset purposes.
        """
        with self._lock:
            count = len(self._instances)
            self._instances.clear()
            print(f"Registry cleared. Removed {count} instances.")
            return {"status": "success", "cleared_count": count} 