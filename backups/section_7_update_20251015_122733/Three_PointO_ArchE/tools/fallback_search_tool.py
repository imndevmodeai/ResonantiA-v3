"""
Fallback Search Tool - Simple HTTP-based search
Temporary solution while browser automation is being configured
"""

import subprocess
import json
import re
import logging
from typing import Dict, List, Any
import time
import urllib.parse

class FallbackSearchTool:
    """
    Fallback search tool using simple HTTP requests.
    Provides basic search functionality when browser automation is not available.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.search_stats = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "average_response_time": 0.0
        }
    
    def search(self, query: str, engine: str = "duckduckgo", **kwargs) -> Dict[str, Any]:
        """
        Perform a web search using HTTP requests.
        
        Args:
            query: Search query string
            engine: Search engine to use (only "duckduckgo" supported)
            debug: Enable debug mode
            
        Returns:
            Dictionary containing search results and metadata
        """
        start_time = time.time()
        self.search_stats["total_searches"] += 1
        
        try:
            self.logger.info(f"Performing fallback search: '{query}' on {engine}")
            
            if engine.lower() == "duckduckgo":
                results = self._search_duckduckgo(query)
            else:
                return self._create_error_result(query, engine, f"Engine '{engine}' not supported in fallback mode")
            
            # Calculate response time
            response_time = time.time() - start_time
            
            if results:
                # Update statistics
                self.search_stats["successful_searches"] += 1
                self._update_average_response_time(response_time)
                
                # Format results for ArchE system
                formatted_results = self._format_results(results, query, engine, response_time)
                
                self.logger.info(f"Fallback search completed: {len(results)} results in {response_time:.2f}s")
                return formatted_results
            else:
                return self._create_error_result(query, engine, "No results found")
                
        except Exception as e:
            self.logger.error(f"Fallback search error: {e}")
            self.search_stats["failed_searches"] += 1
            return self._create_error_result(query, engine, f"Search error: {e}")
    
    def _search_duckduckgo(self, query: str) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo using simple HTTP request.
        """
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://duckduckgo.com/html/?q={encoded_query}"
            
            # Use wget to fetch the page
            cmd = [
                "wget", 
                "-q", 
                "-O", "-",
                "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "--timeout=30",
                url
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                self.logger.error(f"wget failed: {result.stderr}")
                return []
            
            # Parse the HTML response
            html = result.stdout
            return self._parse_duckduckgo_html(html)
            
        except subprocess.TimeoutExpired:
            self.logger.error("wget timeout")
            return []
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
            return []
    
    def _parse_duckduckgo_html(self, html: str) -> List[Dict[str, str]]:
        """
        Parse DuckDuckGo HTML to extract search results.
        """
        results = []
        
        try:
            # Look for result patterns in the HTML
            # This is a basic regex-based approach
            
            # Pattern for links and titles
            link_pattern = r'<a[^>]*href="([^"]*)"[^>]*class="[^"]*result__title[^"]*"[^>]*>([^<]*)</a>'
            matches = re.findall(link_pattern, html, re.IGNORECASE | re.DOTALL)
            
            for match in matches[:10]:  # Limit to 10 results
                link, title = match
                
                # Clean up the title
                title = re.sub(r'<[^>]*>', '', title).strip()
                
                # Skip if empty
                if not title or not link:
                    continue
                
                # Try to find description near this result
                description = self._find_description_near_title(html, title)
                
                results.append({
                    "title": title,
                    "link": link,
                    "description": description
                })
            
            # If no results with the above pattern, try alternative patterns
            if not results:
                # Alternative pattern
                alt_pattern = r'<h2[^>]*class="[^"]*result__title[^"]*"[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>'
                alt_matches = re.findall(alt_pattern, html, re.IGNORECASE | re.DOTALL)
                
                for match in alt_matches[:10]:
                    link, title = match
                    title = re.sub(r'<[^>]*>', '', title).strip()
                    
                    if title and link:
                        results.append({
                            "title": title,
                            "link": link,
                            "description": ""
                        })
            
        except Exception as e:
            self.logger.error(f"HTML parsing error: {e}")
        
        return results
    
    def _find_description_near_title(self, html: str, title: str) -> str:
        """
        Try to find a description snippet near the title.
        """
        try:
            # Look for snippet patterns
            snippet_patterns = [
                r'class="[^"]*result__snippet[^"]*"[^>]*>([^<]*)</span>',
                r'class="[^"]*snippet[^"]*"[^>]*>([^<]*)</span>',
                r'<span[^>]*>([^<]{50,200})</span>'
            ]
            
            for pattern in snippet_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                if matches:
                    return matches[0].strip()
            
            return ""
            
        except Exception:
            return ""
    
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
            "tool": "fallback_search_tool",
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
            "tool": "fallback_search_tool",
            "version": "1.0.0"
        }
    
    def _update_average_response_time(self, response_time: float) -> None:
        """Update the running average response time."""
        current_avg = self.search_stats["average_response_time"]
        successful_searches = self.search_stats["successful_searches"]
        
        if successful_searches == 1:
            self.search_stats["average_response_time"] = response_time
        else:
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
    Drop-in replacement for the existing web search function using fallback method.
    
    Args:
        query: Search query string
        engine: Search engine to use
        debug: Enable debug mode
        
    Returns:
        Search results in ArchE-compatible format
    """
    search_tool = FallbackSearchTool()
    return search_tool.search(query, engine, debug)


if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create search tool
    search_tool = FallbackSearchTool()
    
    # Test query
    test_query = sys.argv[1] if len(sys.argv) > 1 else "artificial intelligence"
    
    print(f"Testing Fallback Search Tool with query: '{test_query}'")
    print("=" * 60)
    
    # Perform test search
    result = search_tool.search(test_query)
    
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