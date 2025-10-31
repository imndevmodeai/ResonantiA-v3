import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Three_PointO_ArchE.web_search_tool import search_web
from Three_PointO_ArchE.utils.reflection_utils import ExecutionStatus

class TestWebSearchToolIntegration(unittest.TestCase):

    def test_live_web_search_success(self):
        """
        Test a live web search for a common term, expecting results.
        This test validates the tool against the real-world system as per the Live Validation Mandate.
        """
        # Arrange
        inputs = {
            "query": "ResonantiA Protocol",
            "num_results": 5
        }

        # Act
        result = search_web(inputs)

        # Assert
        self.assertIn("result", result, f"Test failed. Full output: {result}")
        self.assertIn("reflection", result)
        self.assertNotIn("error", result)

        # Check the result part
        search_results = result["result"].get("results")
        self.assertIsInstance(search_results, list)
        self.assertGreater(len(search_results), 0, "Live search returned no results for a common term.")
        
        first_result = search_results[0]
        self.assertIn("title", first_result)
        self.assertIn("url", first_result)
        self.assertIn("snippet", first_result)
        self.assertTrue(first_result["url"].startswith("http"))

        # Check the reflection part for IAR compliance
        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.SUCCESS.value)
        self.assertEqual(reflection["action_name"], "web_search")
        self.assertGreaterEqual(reflection["confidence"], 0.8)
        self.assertEqual(reflection["outputs_preview"]["results_count"], len(search_results))

    def test_web_search_no_results(self):
        """
        Test a live web search for a nonsensical term, expecting no results but a 'Warning' status.
        """
        # Arrange
        # A long, random string is unlikely to produce results.
        inputs = {
            "query": "ajsdfhaksjdfhalksjdfhalksjdfhalksjdfhweoiru",
            "num_results": 5
        }

        # Act
        result = search_web(inputs)

        # Assert
        self.assertIn("result", result)
        self.assertIn("reflection", result)
        
        search_results = result["result"].get("results")
        self.assertIsInstance(search_results, list)
        self.assertEqual(len(search_results), 0)

        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.WARNING.value)
        self.assertIn("found no results", reflection["summary_message"])

    def test_web_search_missing_query(self):
        """
        Test the failure case when the query is missing. (No API call)
        """
        # Arrange
        inputs = {"num_results": 5}

        # Act
        result = search_web(inputs)

        # Assert
        self.assertIn("error", result)
        self.assertIn("reflection", result)
        self.assertIn("query' is required", result["error"])
        
        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.FAILURE.value)

if __name__ == '__main__':
    unittest.main() 