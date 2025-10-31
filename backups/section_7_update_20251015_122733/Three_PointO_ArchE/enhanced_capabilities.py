"""
Enhanced Capabilities Module for ArchE

This module implements the enhanced capabilities provided by the Gemini API,
including code execution, file handling, grounding, function calling, and structured output.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from .llm_providers.google import GoogleProvider
from .llm_providers.base import LLMProviderError

logger = logging.getLogger(__name__)

class GeminiCapabilities:
    """
    A class to manage and execute enhanced capabilities using the Gemini API.
    """
    
    def __init__(self, google_provider: GoogleProvider):
        """
        Initializes the GeminiCapabilities with a GoogleProvider instance.

        Args:
            google_provider: An instance of GoogleProvider configured for Gemini API access.
        """
        self.google_provider = google_provider

    def execute_code(self, script: str, language: str = "python") -> Dict[str, Any]:
        """
        Executes a code string using the Gemini API's code execution capability.
        
        Args:
            script: The code to execute.
            language: The programming language of the code (default: "python").
            
        Returns:
            A dictionary containing the execution results with IAR compliance.
        """
        try:
            # This assumes the provider has a method for this. This is a conceptual link.
            result = self.google_provider.execute_code(script, language)
            return result
        except (LLMProviderError, AttributeError) as e:
            logger.error(f"Error executing code: {e}")
            return {
                "status": "error",
                "message": f"Code execution failed: {str(e)}",
                "error_details": str(e),
                "reflection": {
                    "status": "Failed",
                    "summary": f"Code execution failed due to provider error: {str(e)}",
                    "confidence": 0.0,
                    "alignment_check": {
                        "objective_alignment": 0.0,
                        "protocol_alignment": 0.0
                    },
                    "potential_issues": [
                        "GoogleProvider.execute_code() method not implemented or raised an error",
                        str(e)
                    ],
                    "raw_output_preview": f"Error: {str(e)}"
                }
            }

    def handle_files(self, file_operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Handles file operations using the Gemini API's file handling capability.
        
        Args:
            file_operations: A list of dictionaries, each describing a file operation.
            
        Returns:
            A dictionary containing the results with IAR compliance.
        """
        try:
            result = self.google_provider.handle_files(file_operations)
            return result
        except (LLMProviderError, AttributeError) as e:
            logger.error(f"Error handling files: {e}")
            return {
                "status": "error",
                "message": f"File handling failed: {str(e)}",
                "reflection": {
                    "status": "Failed",
                    "summary": f"File handling failed: {str(e)}",
                    "confidence": 0.0,
                    "alignment_check": {"objective_alignment": 0.0, "protocol_alignment": 0.0},
                    "potential_issues": ["GoogleProvider.handle_files() not implemented or raised error", str(e)],
                    "raw_output_preview": f"Error: {str(e)}"
                }
            }

    def perform_grounding(self, query: str, context_data: str) -> Optional[str]:
        """
        Performs grounding using the Gemini API.
        
        Args:
            query: The query to ground.
            context_data: The context data to use for grounding.
            
        Returns:
            The grounded response, or None if grounding fails.
        """
        try:
            grounded_response = self.google_provider.perform_grounding(query, context_data)
            return grounded_response
        except (LLMProviderError, AttributeError) as e:
            logger.error(f"Error performing grounding: {e}")
            return None

    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls a function using the Gemini API's function calling capability.
        
        Args:
            function_name: The name of the function to call.
            arguments: A dictionary of arguments to pass to the function.
            
        Returns:
            A dictionary containing the function's return value with IAR compliance.
        """
        try:
            result = self.google_provider.call_function(function_name, arguments)
            return result
        except (LLMProviderError, AttributeError) as e:
            logger.error(f"Error calling function {function_name}: {e}")
            return {
                "status": "error",
                "message": f"Function call failed: {str(e)}",
                "reflection": {
                    "status": "Failed",
                    "summary": f"Function '{function_name}' call failed: {str(e)}",
                    "confidence": 0.0,
                    "alignment_check": {"objective_alignment": 0.0, "protocol_alignment": 0.0},
                    "potential_issues": ["GoogleProvider.call_function() not implemented or raised error", str(e)],
                    "raw_output_preview": f"Error: {str(e)}"
                }
            }

    def generate_structured_output(self, prompt: str, schema: Dict[str, Any]) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """
        Generates structured output based on a prompt and a schema using the Gemini API.
        
        Args:
            prompt: The prompt to use for generating the output.
            schema: The schema to use for structuring the output.
            
        Returns:
            Structured output with IAR compliance, or error dict if generation fails.
        """
        try:
            result = self.google_provider.generate_structured_output(prompt, schema)
            return result
        except (LLMProviderError, AttributeError) as e:
            logger.error(f"Error generating structured output: {e}")
            return {
                "status": "error",
                "message": f"Structured output generation failed: {str(e)}",
                "reflection": {
                    "status": "Failed",
                    "summary": f"Structured output generation failed: {str(e)}",
                    "confidence": 0.0,
                    "alignment_check": {"objective_alignment": 0.0, "protocol_alignment": 0.0},
                    "potential_issues": ["GoogleProvider.generate_structured_output() not implemented or raised error", str(e)],
                    "raw_output_preview": f"Error: {str(e)}"
                }
            } 