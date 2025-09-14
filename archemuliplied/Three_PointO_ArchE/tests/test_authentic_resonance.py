import unittest
import os
import time

# Add project root to path to allow direct imports
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.workflow_engine import IARCompliantWorkflowEngine

class TestAuthenticResonance(unittest.TestCase):
    """
    Tests the system's ability to solve a real-world, multi-step problem
    end-to-end, using live tool capabilities without mocks. This validates
    Authentic Resonance.
    """

    def setUp(self):
        """Set up the test environment."""
        self.workflow_name = "real_world_analysis"
        self.output_file = "outputs/analysis_report.txt"
        
        # Ensure the output file does not exist before the test
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def tearDown(self):
        """Clean up the test environment."""
        # Clean up the generated output file
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

    def test_run_live_real_world_analysis_workflow(self):
        """
        Executes the full codebase analysis workflow with a live LLM call
        and validates the final output qualitatively.
        """
        # --- Arrange ---
        # Instantiate the engine. It will use the live, configured tools.
        engine = IARCompliantWorkflowEngine(workflows_dir="workflows")

        # --- Act ---
        # Run the workflow. This may take a moment as it involves a live API call.
        print("\nExecuting live workflow... This may take a moment.")
        start_time = time.time()
        final_results = engine.run_workflow(self.workflow_name, {})
        end_time = time.time()
        print(f"Live workflow execution completed in {end_time - start_time:.2f} seconds.")

        # --- Assert ---
        # 1. Assert the workflow itself completed successfully
        self.assertEqual(final_results.get("workflow_status"), "Completed Successfully", f"Workflow failed to complete. Final state: {final_results}")
        
        # 2. Assert the final output file was created
        self.assertTrue(os.path.exists(self.output_file), f"Output file '{self.output_file}' was not created.")
        
        # 3. Perform qualitative assertions on the live, non-deterministic output
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertGreater(len(content), 50, "The output report is unexpectedly short.")
        
        # Check for keywords that indicate a successful, relevant analysis
        keywords = ["summary", "analysis", "suggestion", "recommendation", "refactor", "utility", "code"]
        self.assertTrue(
            any(keyword in content.lower() for keyword in keywords),
            f"The output report content does not seem relevant. Keywords {keywords} not found in content: '{content}'"
        )
        
        print(f"\n--- Authentic Resonance Test Passed ---")
        print(f"Generated Analysis Report at: {self.output_file}")
        print(f"--- Report Content ---")
        print(content)
        print(f"----------------------")


if __name__ == '__main__':
    unittest.main()
