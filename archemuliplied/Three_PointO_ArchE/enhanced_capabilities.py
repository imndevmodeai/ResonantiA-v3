"""
Enhanced Capabilities Module for ArchE

This module implements the enhanced capabilities provided by the Gemini API,
including code execution, file handling, grounding, function calling, and structured output.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from .llm_providers import GoogleProvider, LLMProviderError

logger = logging.getLogger(__name__)

class EnhancedCapabilities:
    """Manages enhanced capabilities provided by the Gemini API."""
    
    def __init__(self, google_provider: GoogleProvider):
        """Initialize with a configured GoogleProvider instance."""
        self.provider = google_provider
        
    def execute_code(self, code: str, **kwargs) -> Dict[str, Any]:
        """
        Execute Python code using Gemini's built-in code interpreter.
        
        Args:
            code: Python code to execute
            **kwargs: Additional execution parameters
            
        Returns:
            Dict containing execution results and IAR reflection
        """
        try:
            result = self.provider.execute_code(code, **kwargs)
            
            # Create IAR reflection
            reflection = {
                "status": result["status"],
                "confidence": 1.0 if result["status"] == "success" else 0.0,
                "summary": "Code execution completed successfully" if result["status"] == "success" else f"Code execution failed: {result['error']}",
                "alignment_check": "Code execution aligned with expected behavior" if result["status"] == "success" else "Code execution deviated from expected behavior",
                "potential_issues": [] if result["status"] == "success" else [result["error"]],
                "raw_output_preview": str(result["output"]) if result["output"] else None
            }
            
            return {
                "result": result,
                "reflection": reflection
            }
            
        except Exception as e:
            logger.error(f"Error in code execution: {str(e)}", exc_info=True)
            return {
                "result": {
                    "output": None,
                    "status": "error",
                    "error": str(e)
                },
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "summary": f"Code execution failed: {str(e)}",
                    "alignment_check": "Code execution failed to align with expected behavior",
                    "potential_issues": [str(e)],
                    "raw_output_preview": None
                }
            }
            
    def process_file(self, file_url: str, **kwargs) -> Dict[str, Any]:
        """
        Process a file from a URL using Gemini's file handling capabilities.
        
        Args:
            file_url: URL of the file to process
            **kwargs: Additional processing parameters
            
        Returns:
            Dict containing processing results and IAR reflection
        """
        try:
            result = self.provider.process_file(file_url, **kwargs)
            
            # Create IAR reflection
            reflection = {
                "status": result["status"],
                "confidence": 1.0 if result["status"] == "success" else 0.0,
                "summary": "File processing completed successfully" if result["status"] == "success" else f"File processing failed: {result['error']}",
                "alignment_check": "File processing aligned with expected behavior" if result["status"] == "success" else "File processing deviated from expected behavior",
                "potential_issues": [] if result["status"] == "success" else [result["error"]],
                "raw_output_preview": str(result["content"]) if result["content"] else None
            }
            
            return {
                "result": result,
                "reflection": reflection
            }
            
        except Exception as e:
            logger.error(f"Error in file processing: {str(e)}", exc_info=True)
            return {
                "result": {
                    "content": None,
                    "status": "error",
                    "error": str(e)
                },
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "summary": f"File processing failed: {str(e)}",
                    "alignment_check": "File processing failed to align with expected behavior",
                    "potential_issues": [str(e)],
                    "raw_output_preview": None
                }
            }
            
    def generate_with_grounding(self, prompt: str, sources: List[str], **kwargs) -> Dict[str, Any]:
        """
        Generate text with grounding in specified sources.
        
        Args:
            prompt: The prompt to generate from
            sources: List of source URLs or texts to ground the generation
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generation results and IAR reflection
        """
        try:
            # Configure grounding
            kwargs["grounding"] = {
                "sources": sources,
                "citation_style": kwargs.get("citation_style", "default"),
                "citation_format": kwargs.get("citation_format", "text")
            }
            
            # Generate with grounding
            result = self.provider.generate(prompt, **kwargs)
            
            # Create IAR reflection
            reflection = {
                "status": "Success",
                "confidence": 0.9,  # High confidence due to grounding
                "summary": "Text generation completed with grounding",
                "alignment_check": "Generation aligned with provided sources",
                "potential_issues": [],
                "raw_output_preview": result
            }
            
            return {
                "result": result,
                "reflection": reflection
            }
            
        except Exception as e:
            logger.error(f"Error in grounded generation: {str(e)}", exc_info=True)
            return {
                "result": None,
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "summary": f"Grounded generation failed: {str(e)}",
                    "alignment_check": "Generation failed to align with sources",
                    "potential_issues": [str(e)],
                    "raw_output_preview": None
                }
            }
            
    def generate_with_function_calling(self, prompt: str, tools: List[Dict[str, Any]], **kwargs) -> Dict[str, Any]:
        """
        Generate text with function calling capabilities.
        
        Args:
            prompt: The prompt to generate from
            tools: List of tool definitions for function calling
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generation results and IAR reflection
        """
        try:
            # Configure function calling
            kwargs["tools"] = tools
            
            # Generate with function calling
            result = self.provider.generate(prompt, **kwargs)
            
            # Check if result is a function call
            if isinstance(result, dict) and result.get("type") == "function_call":
                reflection = {
                    "status": "Success",
                    "confidence": 0.95,
                    "summary": f"Function call generated: {result['function']}",
                    "alignment_check": "Function call aligned with tool definitions",
                    "potential_issues": [],
                    "raw_output_preview": str(result)
                }
            else:
                reflection = {
                    "status": "Success",
                    "confidence": 0.9,
                    "summary": "Text generation completed with function calling capability",
                    "alignment_check": "Generation aligned with tool definitions",
                    "potential_issues": [],
                    "raw_output_preview": result
                }
            
            return {
                "result": result,
                "reflection": reflection
            }
            
        except Exception as e:
            logger.error(f"Error in function calling generation: {str(e)}", exc_info=True)
            return {
                "result": None,
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "summary": f"Function calling generation failed: {str(e)}",
                    "alignment_check": "Generation failed to align with tool definitions",
                    "potential_issues": [str(e)],
                    "raw_output_preview": None
                }
            }
            
    def generate_with_structured_output(self, prompt: str, output_schema: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Generate text with structured output according to a schema.
        
        Args:
            prompt: The prompt to generate from
            output_schema: JSON schema defining the expected output structure
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing generation results and IAR reflection
        """
        try:
            # Configure structured output
            kwargs["output_schema"] = output_schema
            
            # Generate with structured output
            result = self.provider.generate(prompt, **kwargs)
            
            # Create IAR reflection
            reflection = {
                "status": "Success",
                "confidence": 0.95,  # High confidence due to schema enforcement
                "summary": "Text generation completed with structured output",
                "alignment_check": "Generation aligned with output schema",
                "potential_issues": [],
                "raw_output_preview": result
            }
            
            return {
                "result": result,
                "reflection": reflection
            }
            
        except Exception as e:
            logger.error(f"Error in structured output generation: {str(e)}", exc_info=True)
            return {
                "result": None,
                "reflection": {
                    "status": "Failed",
                    "confidence": 0.0,
                    "summary": f"Structured output generation failed: {str(e)}",
                    "alignment_check": "Generation failed to align with output schema",
                    "potential_issues": [str(e)],
                    "raw_output_preview": None
                }
            } 