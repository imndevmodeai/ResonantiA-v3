"""
Enhanced Search Tool - HTTP-Based Integration with Fallback Reliability
Replaces browser automation with proven HTTP-based search using enhanced perception engine
"""

import subprocess
import json
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import time
import sys

# Add the current directory to path to import our enhanced perception engine
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from enhanced_perception_engine_with_fallback import enhanced_web_search_with_fallback
    ENHANCED_PERCEPTION_AVAILABLE = True
except ImportError:
    ENHANCED_PERCEPTION_AVAILABLE = False

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
        
        # --- UPDATED PATH ---
        # The new script is in a different location. We'll construct the path
        # relative to this file's location.
        current_dir = Path(__file__).parent.parent.parent # Navigate up to the project root
        self.browser_search_dir = current_dir / "ResonantiA" / "browser_automationz_clone"
        
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
        
        # Check for the new puppeteer_search.js script
        puppeteer_search_script = self.browser_search_dir / "puppeteer_search.js"
        if not puppeteer_search_script.exists():
            raise FileNotFoundError(f"Puppeteer search script not found: {puppeteer_search_script}")
        
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
            
            # --- UPDATED COMMAND ---
            # Call the new script with its expected arguments.
            # The new script expects: node <script> <query> [numResults] [searchEngine] [--debug]
            script_name = "puppeteer_search.js"
            cmd = ["node", script_name, query, "5", engine]
            if debug:
                cmd.append("--debug")
            
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
        """Format search results for ArchE system compatibility with IAR compliance."""
        from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
        
        result_data = {
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
        
        return {
            "status": "success",
            "message": f"Successfully retrieved {len(results)} results from {engine}",
            **result_data,
            "reflection": {
                "status": "Success",
                "summary": f"Web search for '{query}' using {engine} returned {len(results)} results in {response_time:.2f}s",
                "confidence": 0.95 if len(results) >= 3 else 0.7 if len(results) > 0 else 0.3,
                "alignment_check": {
                    "objective_alignment": 1.0,
                    "protocol_alignment": 1.0
                },
                "potential_issues": [] if len(results) >= 3 else ["Low number of search results returned"],
                "raw_output_preview": f'{{"total_results": {len(results)}, "engine": "{engine}"}}',
                "action_name": "perform_web_search",
                "timestamp_utc": now_iso() + "Z",
                "execution_time_seconds": response_time
            }
        }
    
    def _create_error_result(self, query: str, engine: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error result with IAR compliance."""
        from datetime import datetime
        
        self.search_stats["failed_searches"] += 1
        
        return {
            "status": "error",
            "success": False,
            "query": query,
            "engine": engine,
            "error": error_message,
            "message": f"Search failed: {error_message}",
            "results": [],
            "timestamp": time.time(),
            "tool": "enhanced_search_tool",
            "version": "1.0.0",
            "reflection": {
                "status": "Failed",
                "summary": f"Web search for '{query}' using {engine} failed: {error_message}",
                "confidence": 0.0,
                "alignment_check": {
                    "objective_alignment": 0.0,
                    "protocol_alignment": 1.0
                },
                "potential_issues": [
                    error_message,
                    f"Failed to retrieve results from {engine}"
                ],
                "raw_output_preview": f'{{"error": "{error_message}", "query": "{query}"}}',
                "action_name": "perform_web_search",
                "timestamp_utc": now_iso() + "Z",
                "execution_time_seconds": 0.0
            }
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
def perform_web_search(query: str, engine: str = "duckduckgo", debug: bool = False, num_results: int = 5) -> Dict[str, Any]:
    """
    Drop-in replacement for the existing web search function using enhanced perception engine with fallback.
    
    Args:
        query: Search query string
        engine: Search engine to use
        debug: Enable debug mode
        num_results: The number of results to return
        
    Returns:
        Search results in ArchE-compatible format
    """
    logger = logging.getLogger(__name__)
    
    try:
        if ENHANCED_PERCEPTION_AVAILABLE:
            logger.info(f"Using Enhanced Perception Engine with Fallback for query: '{query}'")
            
            # Use our new enhanced perception engine with fallback
            result, iar = enhanced_web_search_with_fallback({
                "query": query,
                "context": {"engine": engine, "debug": debug},
                "max_results": num_results
            })
            
            # Convert to ArchE-compatible format
            if result.get("success"):
                return {
                    "success": True,
                    "query": query,
                    "engine": engine,
                    "results": result.get("results", []),
                    "total_results": result.get("total_results", 0),
                    "response_time": result.get("response_time", 0.0),
                    "analysis": result.get("analysis", {}),
                    "session_stats": result.get("session_stats", {}),
                    "iar": iar
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "engine": engine,
                    "error": result.get("error", "Unknown error"),
                    "results": [],
                    "iar": iar
                }
        else:
            # Fallback to original implementation
            logger.warning("Enhanced Perception Engine not available, using fallback")
            search_tool = EnhancedSearchTool()
            return search_tool.search(query, engine, debug)
            
    except Exception as e:
        logger.error(f"Error in perform_web_search: {e}")
        return {
            "success": False,
            "query": query,
            "engine": engine,
            "error": f"Search error: {str(e)}",
            "results": []
        }


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