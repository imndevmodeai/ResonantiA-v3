"""
Enhanced Search Tool - Browser Automation Integration
Replaces the broken web search functionality with robust browser automation
"""

import subprocess
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import time

class EnhancedSearchTool:
    """
    Enhanced search tool using browser automation for reliable web searches.
    Integrates with the existing ArchE system while providing superior search capabilities.
    """
    
    def __init__(self, browser_search_dir: Optional[str] = None):
        """
        Initialize the enhanced search tool.
        
        Args:
            browser_search_dir: Path to the browser_search directory
        """
        self.logger = logging.getLogger(__name__)
        
        # Set up paths
        if browser_search_dir:
            self.browser_search_dir = Path(browser_search_dir)
        else:
            # Default to the browser_search directory relative to this file
            current_dir = Path(__file__).parent.parent
            self.browser_search_dir = current_dir / "browser_search"
        
        # Validate setup
        self._validate_setup()
        
        # Performance tracking
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_response_time": 0.0
        }
    
    def _validate_setup(self) -> None:
        """Validate that all required files and dependencies are present."""
        if not self.browser_search_dir.exists():
            raise FileNotFoundError(f"Browser search directory not found: {self.browser_search_dir}")
        
        # Check for simple_search.js
        simple_search_script = self.browser_search_dir / "simple_search.js"
        if not simple_search_script.exists():
            raise FileNotFoundError(f"Simple search script not found: {simple_search_script}")
        
        # Check for node_modules
        node_modules = self.browser_search_dir / "node_modules"
        if not node_modules.exists():
            self.logger.warning(f"Node modules not found. Run 'npm install' in {self.browser_search_dir}")
    
    def search(self, query: str, engine: str = "duckduckgo", debug: bool = False) -> Dict[str, Any]:
        """
        Perform a web search using browser automation.
        
        Args:
            query: Search query string
            engine: Search engine to use ("google" or "duckduckgo")
            debug: Enable debug mode with screenshots
            
        Returns:
            Dictionary containing search results and metadata
        """
        start_time = time.time()
        self.search_stats["total_searches"] += 1
        
        try:
            self.logger.info(f"Performing search: '{query}' on {engine}")
            
            # Use the simple search script
            cmd = ["node", "simple_search.js", query]
            
            # Execute search from the browser_search directory
            result = subprocess.run(
                cmd,
                cwd=str(self.browser_search_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            # Process results
            if result.returncode == 0:
                try:
                    # Parse JSON output from stdout
                    search_results = json.loads(result.stdout)
                    
                    # Calculate response time
                    response_time = time.time() - start_time
                    
                    # Update statistics
                    self.search_stats["successful_searches"] += 1
                    self._update_average_response_time(response_time)
                    
                    # Format results for ArchE system
                    formatted_results = self._format_results(search_results, query, engine, response_time)
                    
                    self.logger.info(f"Search completed successfully: {len(search_results)} results in {response_time:.2f}s")
                    return formatted_results
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse search results JSON: {e}")
                    self.logger.error(f"Raw stdout: {result.stdout}")
                    return self._create_error_result(query, engine, f"JSON parsing error: {e}")
                    
            else:
                error_msg = result.stderr if result.stderr else "Search script failed"
                self.logger.error(f"Search failed: {error_msg}")
                return self._create_error_result(query, engine, error_msg)
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"Search timeout for query: {query}")
            self.search_stats["failed_searches"] += 1
            return self._create_error_result(query, engine, "Search timeout")
            
        except Exception as e:
            self.logger.error(f"Unexpected error during search: {e}")
            self.search_stats["failed_searches"] += 1
            return self._create_error_result(query, engine, f"Unexpected error: {e}")
    
    def _format_results(self, results: List[Dict], query: str, engine: str, response_time: float) -> Dict[str, Any]:
        """Format search results for ArchE system compatibility."""
        return {
            "success": True,
            "query": query,
            "engine": engine,
            "total_results": len(results),
            "response_time": response_time,
            "results": results,
            "timestamp": time.time(),
            "tool": "enhanced_search_tool",
            "version": "1.0.0"
        }
    
    def _create_error_result(self, query: str, engine: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error result."""
        self.search_stats["failed_searches"] += 1
        return {
            "success": False,
            "query": query,
            "engine": engine,
            "error": error_message,
            "results": [],
            "timestamp": time.time(),
            "tool": "enhanced_search_tool",
            "version": "1.0.0"
        }
    
    def _update_average_response_time(self, response_time: float) -> None:
        """Update the running average response time."""
        current_avg = self.search_stats["average_response_time"]
        successful_searches = self.search_stats["successful_searches"]
        
        if successful_searches == 1:
            self.search_stats["average_response_time"] = response_time
        else:
            # Calculate running average
            self.search_stats["average_response_time"] = (
                (current_avg * (successful_searches - 1)) + response_time
            ) / successful_searches
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search performance statistics."""
        success_rate = 0.0
        if self.search_stats["total_searches"] > 0:
            success_rate = (
                self.search_stats["successful_searches"] / 
                self.search_stats["total_searches"]
            ) * 100
        
        return {
            **self.search_stats,
            "success_rate": success_rate
        }


# Integration function for existing ArchE system
def perform_web_search(query: str, engine: str = "duckduckgo", debug: bool = False) -> Dict[str, Any]:
    """
    Drop-in replacement for the existing web search function.
    
    Args:
        query: Search query string
        engine: Search engine to use
        debug: Enable debug mode
        
    Returns:
        Search results in ArchE-compatible format
    """
    search_tool = EnhancedSearchTool()
    return search_tool.search(query, engine, debug)


if __name__ == "__main__":
    # Test the enhanced search tool
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create search tool
    search_tool = EnhancedSearchTool()
    
    # Test query
    test_query = sys.argv[1] if len(sys.argv) > 1 else "artificial intelligence"
    
    print(f"Testing Enhanced Search Tool with query: '{test_query}'")
    print("=" * 60)
    
    # Perform test search
    result = search_tool.search(test_query, debug=True)
    
    # Display results
    if result["success"]:
        print(f"✅ Search successful!")
        print(f"📊 Found {result['total_results']} results in {result['response_time']:.2f}s")
        print(f"🔍 Engine: {result['engine']}")
        print("\n📋 Results:")
        for i, res in enumerate(result["results"][:3], 1):
            print(f"{i}. {res.get('title', 'No title')}")
            print(f"   🔗 {res.get('link', 'No link')}")
            print(f"   📝 {res.get('description', 'No description')[:100]}...")
            print()
    else:
        print(f"❌ Search failed: {result['error']}")
    
    # Show statistics
    stats = search_tool.get_statistics()
    print(f"📈 Statistics: {stats}") 