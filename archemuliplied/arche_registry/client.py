import requests
import json
from typing import Dict, Any, List, Optional

class ArchEClient:
    """
    A client for interacting with the ArchE Instance Registry API.
    This allows an ArchE instance to register with the collective and discover others.
    """

    def __init__(self, registry_url: str, instance_id: str, instance_address: str):
        """
        Initializes the ArchEClient.

        Args:
            registry_url: The base URL of the ArchE Registry service (e.g., http://localhost:5000).
            instance_id: The unique ID of this ArchE instance.
            instance_address: The network address where this instance can be reached.
        """
        if registry_url.endswith('/'):
            registry_url = registry_url[:-1]
        self.registry_url = registry_url
        self.instance_id = instance_id
        self.instance_address = instance_address
        print(f"ArchE Client initialized for instance '{self.instance_id}' targeting registry at {self.registry_url}")

    def register(self, capabilities: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Registers this instance with the ArchE Registry.

        Args:
            capabilities: A dictionary describing the instance's capabilities.

        Returns:
            The JSON response from the registry, or None if registration fails.
        """
        endpoint = f"{self.registry_url}/register"
        payload = {
            "instance_id": self.instance_id,
            "capabilities": capabilities,
            "address": self.instance_address
        }
        try:
            response = requests.post(endpoint, json=payload, timeout=5)
            response.raise_for_status()  # Raise an exception for bad status codes
            print(f"Instance '{self.instance_id}' registered successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error registering instance '{self.instance_id}': {e}")
            return None

    def list_instances(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves a list of all active instances from the registry.

        Returns:
            A list of instance dictionaries, or None if the request fails.
        """
        endpoint = f"{self.registry_url}/instances"
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving instance list: {e}")
            return None

    def unregister(self) -> Optional[Dict[str, Any]]:
        """
        Unregisters this instance from the ArchE Registry.

        Returns:
            The JSON response from the registry, or None if unregistration fails.
        """
        endpoint = f"{self.registry_url}/unregister"
        payload = {"instance_id": self.instance_id}
        try:
            response = requests.delete(endpoint, json=payload, timeout=5)
            response.raise_for_status()
            print(f"Instance '{self.instance_id}' unregistered successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error unregistering instance '{self.instance_id}': {e}")
            return None

    def reset_registry(self) -> Optional[Dict[str, Any]]:
        """
        Resets the entire registry, clearing all instances. For testing.
        """
        endpoint = f"{self.registry_url}/reset"
        try:
            response = requests.post(endpoint, timeout=5)
            response.raise_for_status()
            print("Registry has been reset successfully.")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error resetting registry: {e}")
            return None

if __name__ == '__main__':
    # Example Usage
    REGISTRY_URL = "http://localhost:5000"
    
    # --- Create a client for setup/teardown ---
    setup_client = ArchEClient(REGISTRY_URL, "setup-client", "local")
    
    # --- Reset the registry for a clean test ---
    print("--- Preparing for test: Resetting Registry ---")
    setup_client.reset_registry()
    print("------------------------------------------\n")

    # --- Define an Engineering Instance ---
    engineering_instance_client = ArchEClient(
        registry_url=REGISTRY_URL,
        instance_id="arche-engineering-01",
        instance_address="192.168.13.131:8001"
    )

    engineering_capabilities = {
        "Functional Domains": ["engineering", "analysis", "protocol_evolution"],
        "Performance Tiers": "high_capacity",
        "Specialization Tags": ["python", "system_architecture", "distributed_systems"],
        "Instance Type": "Engineering instancE",
        "Cognitive toolS": ["Code executoR", "Search tooL", "direct_file_accessX"]
    }

    # Register the instance
    registration_result = engineering_instance_client.register(engineering_capabilities)
    if not registration_result:
        print("Halting example due to registration failure.")
    else:
        # List all instances in the collective
        instances = engineering_instance_client.list_instances()
        if instances:
            print("\n--- Current Collective ---")
            print(json.dumps(instances, indent=2))
            print("------------------------\n")

        # --- Define an Analytical Instance ---
        analytical_instance_client = ArchEClient(
            registry_url=REGISTRY_URL,
            instance_id="arche-analytical-01",
            instance_address="192.168.13.131:8002"
        )
        analytical_capabilities = {
            "Functional Domains": ["analysis", "prediction", "simulation"],
            "Performance Tiers": "medium_capacity",
            "Specialization Tags": ["temporal_analysis", "causal_reasoning"],
            "Instance Type": "General ArchE",
            "Cognitive toolS": ["CfpframeworK", "Causal inference tooL", "Predictive modeling tooL"]
        }
        
        analytical_instance_client.register(analytical_capabilities)

        # List instances again to see the new member
        instances = engineering_instance_client.list_instances()
        if instances:
            print("\n--- Collective After New Member ---")
            print(json.dumps(instances, indent=2))
            print("---------------------------------\n")

        # Unregister the instances
        engineering_instance_client.unregister()
        analytical_instance_client.unregister()

        # Final list to confirm
        instances = engineering_instance_client.list_instances()
        if instances is not None:
            print("\n--- Final Collective State ---")
            print(json.dumps(instances, indent=2))
            print("----------------------------\n") 