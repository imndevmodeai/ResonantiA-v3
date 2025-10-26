"""
Unified Search Tool - Intelligent search with fallback capability
Combines browser automation and HTTP-based search methods for maximum reliability
"""

import logging
from typing import Dict, Any, Optional
import time
from pathlib import Path
import os

# Import our search implementations
try:
    from enhanced_search_tool import EnhancedSearchTool
    BROWSER_AUTOMATION_AVAILABLE = True
except ImportError:
    BROWSER_AUTOMATION_AVAILABLE = False

try:
    from fallback_search_tool import FallbackSearchTool
    FALLBACK_SEARCH_AVAILABLE = True
except ImportError:
    FALLBACK_SEARCH_AVAILABLE = False


class UnifiedSearchTool:
    """
    Unified search tool that intelligently selects the best available search method.
    
    Search Strategy:
    1. Try browser automation (if available and configured)
    2. Fall back to HTTP-based search (if browser automation fails)
    3. Return comprehensive error if all methods fail
    """
    
    def __init__(self, prefer_browser_automation: bool = True):
        """
        Initialize the unified search tool.
        
        Args:
            prefer_browser_automation: Whether to prefer browser automation over fallback
        """
        self.logger = logging.getLogger(__name__)
        self.prefer_browser_automation = prefer_browser_automation
        
        # Initialize available search tools
        self.browser_search = None
        self.fallback_search = None
        
        if BROWSER_AUTOMATION_AVAILABLE:
            try:
                self.browser_search = EnhancedSearchTool()
                self.logger.info("Browser automation search tool initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize browser automation: {e}")
                self.browser_search = None
        
        if FALLBACK_SEARCH_AVAILABLE:
            try:
                self.fallback_search = FallbackSearchTool()
                self.logger.info("Fallback search tool initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize fallback search: {e}")
                self.fallback_search = None
        
        # Validate that at least one search method is available
        if not self.browser_search and not self.fallback_search:
            raise RuntimeError("No search tools available - both browser automation and fallback failed to initialize")
        
        # Statistics tracking
        self.search_stats = {
            "total_searches": 0,
            "browser_automation_successes": 0,
            "fallback_successes": 0,
            "total_failures": 0,
            "average_response_time": 0.0
        }
    
    def search(self, query: str, engine: str = "duckduckgo", debug: bool = False, 
               force_method: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a web search using the best available method.
        
        Args:
            query: Search query string
            engine: Search engine to use
            debug: Enable debug mode
            force_method: Force a specific method ("browser", "fallback", or None for auto)
            
        Returns:
            Dictionary containing search results and metadata
        """
        start_time = time.time()
        self.search_stats["total_searches"] += 1
        
        self.logger.info(f"Unified search for: '{query}' on {engine}")
        
        # Determine search strategy
        methods_to_try = self._determine_search_methods(force_method)
        
        last_error = None
        
        for method_name, search_tool in methods_to_try:
            if search_tool is None:
                continue
                
            try:
                self.logger.info(f"Attempting search with {method_name}")
                
                # Perform search
                result = search_tool.search(query, engine, debug)
                
                # Check if successful
                if result.get("success", False) and result.get("results"):
                    # Update statistics
                    response_time = time.time() - start_time
                    self._update_stats(method_name, response_time)
                    
                    # Add method information to result
                    result["search_method"] = method_name
                    result["unified_tool_stats"] = self.get_statistics()
                    
                    self.logger.info(f"Search successful with {method_name}: {len(result['results'])} results")
                    return result
                else:
                    last_error = result.get("error", f"{method_name} returned no results")
                    self.logger.warning(f"{method_name} failed: {last_error}")
                    
            except Exception as e:
                last_error = f"{method_name} exception: {e}"
                self.logger.error(f"{method_name} failed with exception: {e}")
                continue
        
        # All methods failed
        self.search_stats["total_failures"] += 1
        return self._create_unified_error_result(query, engine, last_error or "All search methods failed")
    
    def _determine_search_methods(self, force_method: Optional[str]) -> list:
        """
        Determine which search methods to try and in what order.
        
        Args:
            force_method: Forced method name or None for auto-selection
            
        Returns:
            List of (method_name, search_tool) tuples in order of preference
        """
        if force_method == "browser":
            return [("browser_automation", self.browser_search)]
        elif force_method == "fallback":
            return [("fallback_search", self.fallback_search)]
        else:
            # Auto-selection based on preference and availability
            methods = []
            
            if self.prefer_browser_automation:
                if self.browser_search:
                    methods.append(("browser_automation", self.browser_search))
                if self.fallback_search:
                    methods.append(("fallback_search", self.fallback_search))
            else:
                if self.fallback_search:
                    methods.append(("fallback_search", self.fallback_search))
                if self.browser_search:
                    methods.append(("browser_automation", self.browser_search))
            
            return methods
    
    def _update_stats(self, method_name: str, response_time: float) -> None:
        """Update statistics for successful search."""
        if method_name == "browser_automation":
            self.search_stats["browser_automation_successes"] += 1
        elif method_name == "fallback_search":
            self.search_stats["fallback_successes"] += 1
        
        # Update average response time
        total_successes = (self.search_stats["browser_automation_successes"] + 
                          self.search_stats["fallback_successes"])
        
        if total_successes == 1:
            self.search_stats["average_response_time"] = response_time
        else:
            current_avg = self.search_stats["average_response_time"]
            self.search_stats["average_response_time"] = (
                (current_avg * (total_successes - 1)) + response_time
            ) / total_successes
    
    def _create_unified_error_result(self, query: str, engine: str, error_message: str) -> Dict[str, Any]:
        """Create a standardized error result for the unified tool."""
        return {
            "success": False,
            "query": query,
            "engine": engine,
            "error": error_message,
            "results": [],
            "timestamp": time.time(),
            "tool": "unified_search_tool",
            "search_method": "none",
            "available_methods": {
                "browser_automation": self.browser_search is not None,
                "fallback_search": self.fallback_search is not None
            },
            "unified_tool_stats": self.get_statistics(),
            "version": "1.0.0"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive search statistics."""
        total_successes = (self.search_stats["browser_automation_successes"] + 
                          self.search_stats["fallback_successes"])
        
        success_rate = 0.0
        if self.search_stats["total_searches"] > 0:
            success_rate = (total_successes / self.search_stats["total_searches"]) * 100
        
        return {
            **self.search_stats,
            "total_successes": total_successes,
            "success_rate": success_rate,
            "browser_automation_available": self.browser_search is not None,
            "fallback_search_available": self.fallback_search is not None
        }
    
    def get_method_preferences(self) -> Dict[str, Any]:
        """Get information about method preferences and availability."""
        return {
            "prefer_browser_automation": self.prefer_browser_automation,
            "browser_automation_available": self.browser_search is not None,
            "fallback_search_available": self.fallback_search is not None,
            "recommended_method": self._get_recommended_method()
        }
    
    def _get_recommended_method(self) -> str:
        """Get the currently recommended search method based on performance."""
        stats = self.get_statistics()
        
        if stats["total_searches"] == 0:
            return "fallback_search" if self.fallback_search else "browser_automation"
        
        # Recommend based on success rates
        browser_rate = 0.0
        fallback_rate = 0.0
        
        if stats["total_searches"] > 0:
            browser_rate = (stats["browser_automation_successes"] / stats["total_searches"]) * 100
            fallback_rate = (stats["fallback_successes"] / stats["total_searches"]) * 100
        
        if fallback_rate > browser_rate:
            return "fallback_search"
        else:
            return "browser_automation" if self.browser_search else "fallback_search"


# Global instance for easy access
_unified_search_instance = None

def get_unified_search_tool() -> UnifiedSearchTool:
    """Get a singleton instance of the unified search tool."""
    global _unified_search_instance
    if _unified_search_instance is None:
        # Allow environment override to prefer fallback search (HTTP) over browser automation.
        # Default to fallback preference to avoid heavy dependencies/timeouts unless explicitly enabled.
        prefer_env = os.environ.get("ARCHE_PREFER_BROWSER_AUTOMATION", os.environ.get("ARCH_E_PREFER_BROWSER_AUTOMATION", "false")).strip().lower()
        prefer_browser = prefer_env in ("1", "true", "yes", "on")
        _unified_search_instance = UnifiedSearchTool(prefer_browser_automation=prefer_browser)
    return _unified_search_instance


# Integration function for existing ArchE system
def perform_web_search(query: str, engine: str = "duckduckgo", debug: bool = False) -> Dict[str, Any]:
    """
    Drop-in replacement for the existing web search function.
    Uses the unified search tool with intelligent method selection.
    
    Args:
        query: Search query string
        engine: Search engine to use
        debug: Enable debug mode
        
    Returns:
        Search results in ArchE-compatible format
    """
    search_tool = get_unified_search_tool()
    return search_tool.search(query, engine, debug)


if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create unified search tool
    search_tool = UnifiedSearchTool()
    
    # Test query
    test_query = sys.argv[1] if len(sys.argv) > 1 else "artificial intelligence"
    
    print(f"Testing Unified Search Tool with query: '{test_query}'")
    print("=" * 60)
    
    # Show method preferences
    prefs = search_tool.get_method_preferences()
    print(f"🔧 Method Preferences:")
    print(f"   Browser Automation Available: {prefs['browser_automation_available']}")
    print(f"   Fallback Search Available: {prefs['fallback_search_available']}")
    print(f"   Preferred Method: {'Browser' if prefs['prefer_browser_automation'] else 'Fallback'}")
    print(f"   Recommended Method: {prefs['recommended_method']}")
    print()
    
    # Perform test search
    result = search_tool.search(test_query, debug=True)
    
    # Display results
    if result["success"]:
        print(f"✅ Search successful!")
        print(f"🔍 Method Used: {result['search_method']}")
        print(f"📊 Found {result['total_results']} results in {result['response_time']:.2f}s")
        print(f"🌐 Engine: {result['engine']}")
        print("\n📋 Results:")
        for i, res in enumerate(result["results"][:3], 1):
            print(f"{i}. {res.get('title', 'No title')}")
            print(f"   🔗 {res.get('link', 'No link')}")
            print(f"   📝 {res.get('description', 'No description')[:100]}...")
            print()
    else:
        print(f"❌ Search failed: {result['error']}")
        print(f"🔧 Available Methods: {result['available_methods']}")
    
    # Show comprehensive statistics
    stats = search_tool.get_statistics()
    print(f"📈 Comprehensive Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}") 