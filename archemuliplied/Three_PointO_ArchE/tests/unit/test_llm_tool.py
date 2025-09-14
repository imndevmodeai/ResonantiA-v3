import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import time

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Three_PointO_ArchE.llm_tool import generate_text_llm
from Three_PointO_ArchE.utils.reflection_utils import ExecutionStatus

# --- Prerequisite Check for Live API Test ---
GEMINI_API_KEY_PRESENT = bool(os.environ.get("GEMINI_API_KEY"))

class TestLLMToolIntegration(unittest.TestCase):

    @unittest.skipUnless(GEMINI_API_KEY_PRESENT, "GEMINI_API_KEY environment variable not set. Skipping live API test.")
    def test_live_generate_text_llm_success(self):
        """
        Test the successful execution of generate_text_llm against the live Gemini API.
        """
        # Arrange
        inputs = {
            "prompt": "This is a live test. Respond with a single word: 'Acknowledged'",
            "provider": "gemini",
            "model": "gemini-1.5-flash-latest",
            "temperature": 0.0 # Set to 0 for deterministic output
        }

        # Act
        result = generate_text_llm(inputs)

        # Assert
        self.assertIn("result", result, f"Test failed. Full output: {result}")
        self.assertIn("reflection", result)
        self.assertNotIn("error", result)
        
        # Check the result part for a non-empty string
        response_text = result["result"]["response_text"]
        self.assertIsInstance(response_text, str)
        self.assertGreater(len(response_text), 0, "The API returned an empty response.")
        
        # Optionally, check if the response contains the expected word for this specific prompt
        self.assertIn("Acknowledged", response_text)

        # Check the reflection part for IAR compliance
        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.SUCCESS.value)
        self.assertEqual(reflection["action_name"], "generate_text")
        self.assertGreaterEqual(reflection["confidence"], 0.8)
        self.assertIn("live test", reflection["inputs_preview"]["prompt"])
        self.assertIn("Acknowledged", reflection["outputs_preview"]["response_text"])
        self.assertIsInstance(reflection["potential_issues"], list)
        self.assertEqual(len(reflection["potential_issues"]), 0)
        self.assertIsNotNone(reflection["execution_time_seconds"])

    def test_generate_text_llm_unsupported_provider(self):
        """
        Test the failure case with an unsupported provider. (No API call)
        """
        # Arrange
        inputs = {
            "prompt": "Test prompt",
            "provider": "unsupported_ai"
        }

        # Act
        result = generate_text_llm(inputs)

        # Assert
        self.assertIn("error", result)
        self.assertIn("reflection", result)
        self.assertNotIn("result", result)
        self.assertIn("not implemented", result["error"])

        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.FAILURE.value)

    def test_generate_text_llm_missing_prompt(self):
        """
        Test the failure case when the prompt is missing. (No API call)
        """
        # Arrange
        inputs = {"provider": "gemini"}

        # Act
        result = generate_text_llm(inputs)

        # Assert
        self.assertIn("error", result)
        self.assertIn("reflection", result)
        self.assertIn("prompt' is required", result["error"])
        
        reflection = result["reflection"]
        self.assertEqual(reflection["status"], ExecutionStatus.FAILURE.value)

if __name__ == '__main__':
    # Ensure the script can be run directly.
    # Note: Running this way will execute the live test if the API key is present.
    unittest.main() 