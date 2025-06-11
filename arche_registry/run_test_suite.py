import threading
import time
import requests
import os
import signal

# Add the parent directory to the path to allow direct imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from arche_registry.api import app, configure_orchestrator_client
from arche_registry.client import ArchEClient
# The test suite no longer needs to import the orchestrator directly
import json

class TestSuite:
    def __init__(self):
        self.server_thread = None
        self.host = "127.0.0.1"
        self.port = 5001  # Use a different port to avoid conflicts
        self.registry_url = f"http://{self.host}:{self.port}"
        self.session = requests.Session() # Use a session for requests

    def run_server(self):
        """Runs the Flask app in a separate thread."""
        print(f"Starting server on {self.registry_url}...")
        from waitress import serve
        # Configure the orchestrator's internal client URL before starting
        configure_orchestrator_client(self.port)
        serve(app, host=self.host, port=self.port)

    def start_server(self):
        """Starts the server thread."""
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(2)  # Give the server a moment to start

    def stop_server(self):
        """Stops the server."""
        # This is tricky with dev servers; for a real app, you'd have a proper shutdown endpoint.
        # For this test, we'll rely on the script ending to kill the daemon thread.
        print("Test complete. Server thread will be terminated.")
        
    def run_tests(self):
        """Runs the full client test suite."""
        print("\n--- INITIALIZING TEST SUITE ---")
        self.start_server()

        try:
            # 1. Initialize Clients
            print("\n--- Step 1: Initializing Clients ---")
            eng_client = ArchEClient(self.registry_url, "arche-eng-01", f"{self.host}:8001")
            anl_client = ArchEClient(self.registry_url, "arche-anl-01", f"{self.host}:8002")
            print("Clients initialized.")

            # 2. Reset Registry and Orchestrator via API
            print("\n--- Step 2: Resetting System State via API ---")
            response = self.session.post(f"{self.registry_url}/reset")
            response.raise_for_status()
            assert response.json()['status'] == 'success', "Reset via API failed!"
            print("System state reset successfully.")

            # 3. Verify Registry is Empty
            print("\n--- Step 3: Verifying Registry is Empty ---")
            instances = eng_client.list_instances()
            assert instances is not None and len(instances) == 0, "Registry not empty after reset!"
            print("Registry confirmed empty.")

            # 4. Register Instances
            print("\n--- Step 4: Registering Instances ---")
            eng_caps = {
                "Instance Type": "Engineering instancE",
                "Cognitive toolS": ["Code executoR", "Search tooL", "direct_file_accessX"]
            }
            reg_result_eng = eng_client.register(eng_caps)
            assert reg_result_eng is not None and reg_result_eng['status'] == 'success'
            
            anl_caps = {
                "Instance Type": "General ArchE",
                "Cognitive toolS": ["CfpframeworK", "Causal inference tooL", "Predictive modeling tooL"]
            }
            reg_result_anl = anl_client.register(anl_caps)
            assert reg_result_anl is not None and reg_result_anl['status'] == 'success'
            print("Instances registered.")

            # 5. Create Roadmap via API
            print("\n--- Step 5: Creating Roadmap via API ---")
            task_desc1 = "Generate a patch for a critical bug"
            task1_payload = {"description": task_desc1, "capability_needed": "Code executoR"}
            res1 = self.session.post(f"{self.registry_url}/orchestrator/tasks", json=task1_payload)
            res1.raise_for_status()
            task1 = res1.json()
            assert task1['description'] == task_desc1
            print(f"Task 1 ({task1['task_id']}) created.")
            
            task_desc2 = "Model the bug's downstream impact"
            task2_payload = {"description": task_desc2, "capability_needed": "Causal inference tooL"}
            res2 = self.session.post(f"{self.registry_url}/orchestrator/tasks", json=task2_payload)
            res2.raise_for_status()
            task2 = res2.json()
            assert task2['description'] == task_desc2
            print(f"Task 2 ({task2['task_id']}) created.")

            # 6. Assign Tasks via API
            print("\n--- Step 6: Assigning Tasks via API ---")
            res_assign1 = self.session.post(f"{self.registry_url}/orchestrator/tasks/{task1['task_id']}/assign")
            res_assign1.raise_for_status()
            assigned_task1 = res_assign1.json()
            assert assigned_task1['status'] == 'assigned'
            assert assigned_task1['assigned_to'] == 'arche-eng-01'
            print(f"Task 1 correctly assigned to {assigned_task1['assigned_to']}.")

            res_assign2 = self.session.post(f"{self.registry_url}/orchestrator/tasks/{task2['task_id']}/assign")
            res_assign2.raise_for_status()
            assigned_task2 = res_assign2.json()
            assert assigned_task2['status'] == 'assigned'
            assert assigned_task2['assigned_to'] == 'arche-anl-01'
            print(f"Task 2 correctly assigned to {assigned_task2['assigned_to']}.")

            # 7. Simulate Task Completion and Report Back via API
            print("\n--- Step 7: Simulating Task Completion & IAR Feedback ---")
            # Simulate Engineering Instance completing its task
            completion1_payload = {
                "result": "def fix_bug():\n    return 'Bug Fixed'",
                "iar": {
                    "confidence": 0.98,
                    "tactical_resonance": "high",
                    "crystallization_potential": "medium",
                    "potential_issues": []
                }
            }
            res_complete1 = self.session.post(f"{self.registry_url}/tasks/{task1['task_id']}/complete", json=completion1_payload)
            res_complete1.raise_for_status()
            assert res_complete1.json()['status'] == 'success'
            print(f"Task 1 completion reported successfully.")

            # 8. Unregister All Instances
            print("\n--- Step 8: Unregistering All Instances ---")
            eng_client.unregister()
            anl_client.unregister()
            print("Instances unregistered.")

            # 9. Verify Final State (Optional: could add a final state check API endpoint)
            print("\n--- Step 9: Final Verification ---")
            print("Lifecycle complete.")


            print("\n\n✅ ✅ ✅ ALL TESTS PASSED! ✅ ✅ ✅")
            print("Implementation Resonance Achieved for Full Orchestration Loop.")

        except (AssertionError, requests.exceptions.RequestException) as e:
            print(f"\n\n❌ ❌ ❌ TEST FAILED! ❌ ❌ ❌")
            print(f"Error: {e}")
            print("Dissonance detected. Further debugging required.")
        finally:
            self.stop_server()


if __name__ == '__main__':
    suite = TestSuite()
    suite.run_tests() 