"""
Gemini Enhanced Tools Suite

This module provides a suite of tools that leverage the enhanced capabilities
of the Gemini API through the EnhancedCapabilities wrapper. It serves as the
direct interface for the action registry to access these powerful features.
"""

import logging
from typing import Dict, Any, List

# Use relative imports to access modules within the same package
from ..llm_providers import GoogleProvider, LLMProviderError, get_llm_provider
from ..enhanced_capabilities import EnhancedCapabilities
from थ्री_PointO_ArchE.utils.reflection_utils import (
    create_reflection,
    ExecutionStatus,
)

logger = logging.getLogger(__name__)

class GeminiToolSuite:
    """
    A wrapper class that makes Gemini's enhanced capabilities available as tools.
    """
    def __init__(self, google_provider: GoogleProvider):
        """
        Initializes the tool suite with a GoogleProvider instance.

        Args:
            google_provider: An initialized instance of the GoogleProvider.
        """
        if not isinstance(google_provider, GoogleProvider):
            raise TypeError("GeminiToolSuite requires an instance of GoogleProvider.")
        
        self.capabilities = EnhancedCapabilities(google_provider)
        logger.info("GeminiToolSuite initialized with EnhancedCapabilities.")

    def execute_gemini_code(self, code: str, sandbox_id: str = None, **kwargs) -> Dict[str, Any]:
        """
        Action to execute Python code using the Gemini code interpreter.

        Args:
            code: The Python code string to execute.
            sandbox_id: The ID of the sandbox environment.
            **kwargs: Additional parameters for the execution environment.

        Returns:
            A dictionary containing the execution result and an IAR reflection.
        """
        logger.debug(f"Executing Gemini code: {code[:100]}...")
        return self.capabilities.execute_code(code, sandbox_id)

    def process_gemini_file(self, file_url: str, **kwargs) -> Dict[str, Any]:
        """
        Action to process a file from a URL using Gemini's file handling.

        Args:
            file_url: The URL of the file to process.
            **kwargs: Additional parameters for file processing.

        Returns:
            A dictionary containing the file content and an IAR reflection.
        """
        logger.debug(f"Processing Gemini file from URL: {file_url}")
        return self.capabilities.process_file(file_url)

    def generate_with_grounding(self, prompt: str, sources: List[str], **kwargs) -> Dict[str, Any]:
        """
        Action to generate text grounded in a list of sources.

        Args:
            prompt: The prompt for the generation.
            sources: A list of source URLs or texts to ground the response.
            **kwargs: Additional generation parameters.

        Returns:
            A dictionary containing the generated text and an IAR reflection.
        """
        logger.debug("Generating text with grounding...")
        return self.capabilities.generate_with_grounding(prompt, sources)

    def generate_with_function_calling(self, prompt: str, functions: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Action to generate a response that may include a function call.

        Args:
            prompt: The prompt for the generation.
            functions: A list of function definitions available for the LLM to call.
            **kwargs: Additional generation parameters.

        Returns:
            A dictionary containing the generated text or function call and an IAR reflection.
        """
        logger.debug("Generating text with function calling enabled...")
        return self.capabilities.generate_with_function_calling(prompt, functions)

    def generate_with_structured_output(self, prompt: str, schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Action to generate text that conforms to a specific JSON schema.

        Args:
            prompt: The prompt for the generation.
            schema: The JSON schema for the desired output structure.
            **kwargs: Additional generation parameters.

        Returns:
            A dictionary containing the structured output and an IAR reflection.
        """
        logger.debug("Generating text with a structured output schema...")
        return self.capabilities.generate_with_structured_output(prompt, schema)


def get_gemini_tool_suite() -> GeminiToolSuite:
    """
    Factory function to get an initialized GeminiToolSuite instance.
    This handles the logic of getting the Google provider.
    """
    try:
        # get_llm_provider should be able to return a specific provider
        google_provider = get_llm_provider('google')
        if not isinstance(google_provider, GoogleProvider):
            raise LLMProviderError("The 'google' provider is not a valid GoogleProvider instance.")
            
        return GeminiToolSuite(google_provider)
    except (LLMProviderError, TypeError) as e:
        logger.error(f"Failed to initialize GeminiToolSuite: {e}", exc_info=True)
        # Depending on strictness, you might return None or raise the exception
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while creating GeminiToolSuite: {e}", exc_info=True)
        raise

# Example of how to get an instance (for testing or direct use)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     try:
#         tool_suite = get_gemini_tool_suite()
#         print("GeminiToolSuite created successfully.")
#         # You could add a test call here, e.g.,
#         # result = tool_suite.execute_gemini_code("print('Hello from Gemini')")
#         # print(result)
#     except Exception as e:
#         print(f"Failed to create GeminiToolSuite: {e}") 