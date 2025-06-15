"""
Tests for tools implementation with native Gemini API integration
"""
import unittest
import asyncio
from typing import Dict, Any
from Three_PointO_ArchE.tools import Tools, SearchResult, LLMResult

class TestTools(unittest.TestCase):
    """Test suite for tools implementation."""
    
    def setUp(self):
        """Set up test environment."""
        self.tools = Tools()
        self.test_context = {
            "user_id": "test_user",
            "session_id": "test_session",
            "timestamp": "2024-03-20T12:00:00Z"
        }
    
    def test_search_web(self):
        """Test web search functionality."""
        async def run_test():
            # Test Gemini grounded search
            result = await self.tools.search_web(
                query="test query",
                context=self.test_context,
                provider="gemini_grounded_search"
            )
            
            self.assertIsInstance(result, SearchResult)
            self.assertIsInstance(result.results, list)
            self.assertIsInstance(result.citations, list)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.iar_data, dict)
            
            # Test result validation
            self.assertTrue(self.tools.validate_result(result))
            
            # Test fallback provider
            fallback_result = await self.tools.search_web(
                query="test query",
                context=self.test_context,
                provider="fallback"
            )
            
            self.assertIsInstance(fallback_result, SearchResult)
        
        asyncio.run(run_test())
    
    def test_invoke_llm(self):
        """Test LLM invocation functionality."""
        async def run_test():
            # Test basic LLM invocation
            result = await self.tools.invoke_llm(
                prompt="test prompt",
                context=self.test_context
            )
            
            self.assertIsInstance(result, LLMResult)
            self.assertIsInstance(result.response, str)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.iar_data, dict)
            
            # Test with response schema
            schema = {
                "type": "object",
                "properties": {
                    "key": {"type": "string"}
                }
            }
            
            schema_result = await self.tools.invoke_llm(
                prompt="test prompt",
                context=self.test_context,
                response_schema=schema
            )
            
            self.assertIsInstance(schema_result, LLMResult)
            self.assertIsInstance(schema_result.structured_output, dict)
            
            # Test result validation
            self.assertTrue(self.tools.validate_result(result))
            self.assertTrue(self.tools.validate_result(schema_result))
        
        asyncio.run(run_test())
    
    def test_analyze_url_content(self):
        """Test URL content analysis functionality."""
        async def run_test():
            result = await self.tools.analyze_url_content(
                url="https://example.com",
                context=self.test_context
            )
            
            self.assertIsInstance(result, LLMResult)
            self.assertIsInstance(result.response, str)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.iar_data, dict)
            
            # Test result validation
            self.assertTrue(self.tools.validate_result(result))
        
        asyncio.run(run_test())
    
    def test_error_handling(self):
        """Test error handling in tools."""
        async def run_test():
            # Test search error
            error_result = await self.tools.search_web(
                query="",  # Empty query should trigger error
                context=self.test_context
            )
            
            self.assertEqual(error_result.confidence, 0.0)
            self.assertEqual(error_result.iar_data["status"], "Error")
            
            # Test LLM error
            llm_error = await self.tools.invoke_llm(
                prompt="",  # Empty prompt should trigger error
                context=self.test_context
            )
            
            self.assertEqual(llm_error.confidence, 0.0)
            self.assertEqual(llm_error.iar_data["status"], "Error")
            
            # Test URL analysis error
            url_error = await self.tools.analyze_url_content(
                url="",  # Empty URL should trigger error
                context=self.test_context
            )
            
            self.assertEqual(url_error.confidence, 0.0)
            self.assertEqual(url_error.iar_data["status"], "Error")
        
        asyncio.run(run_test())
    
    def test_execution_summary(self):
        """Test execution summary functionality."""
        async def run_test():
            # Perform some operations
            await self.tools.search_web(
                query="test query",
                context=self.test_context
            )
            
            await self.tools.invoke_llm(
                prompt="test prompt",
                context=self.test_context
            )
            
            # Get execution summary
            summary = self.tools.get_execution_summary()
            
            self.assertIsInstance(summary, dict)
            self.assertIn("total_executions", summary)
            self.assertIn("average_resonance", summary)
            self.assertIn("detected_issues", summary)
        
        asyncio.run(run_test())

if __name__ == "__main__":
    unittest.main() 