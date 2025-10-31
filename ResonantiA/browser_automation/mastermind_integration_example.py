#!/usr/bin/env python3
"""
Mastermind.interact Integration Example
Shows how to integrate the unified search engine into mastermind.interact
"""

import asyncio
import json
import sys
import os
from typing import Dict, List, Any

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_search_python import MastermindSearchIntegration, quick_search_sync

class MastermindSearchHandler:
    """
    Handler for integrating unified search with mastermind.interact
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the search handler
        
        Args:
            config: Configuration for the search engine
        """
        self.config = config or {
            'debug': True,
            'enable_human_handoff': True,
            'headless': False,
            'timeout': 300,
            'max_results': 10
        }
        
        self.integration = MastermindSearchIntegration(self.config)
        self.search_cache = {}
    
    async def handle_search_request(self, 
                                  query: str, 
                                  engines: List[str] = None,
                                  use_handoff: bool = True) -> Dict[str, Any]:
        """
        Handle a search request from mastermind.interact
        
        Args:
            query: Search query
            engines: Search engines to use
            use_handoff: Enable human CAPTCHA handoff
            
        Returns:
            Formatted search results for mastermind.interact
        """
        
        # Check cache first
        cache_key = f"{query}_{','.join(engines or ['duckduckgo'])}"
        if cache_key in self.search_cache:
            print(f"Returning cached results for: {query}")
            return self.search_cache[cache_key]
        
        print(f"Performing search: {query}")
        print(f"Engines: {engines or ['duckduckgo']}")
        print(f"Human handoff: {use_handoff}")
        
        try:
            # Perform the search
            results = await self.integration.search(
                query=query,
                engines=engines,
                use_handoff=use_handoff,
                save_results=True
            )
            
            # Format results for mastermind.interact
            formatted_results = self._format_for_mastermind(results)
            
            # Cache the results
            self.search_cache[cache_key] = formatted_results
            
            return formatted_results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query,
                'results': [],
                'suggestions': [
                    'Try a different search query',
                    'Check your internet connection',
                    'Try using only DuckDuckGo engine',
                    'Disable human handoff if not needed'
                ]
            }
    
    def _format_for_mastermind(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format search results for mastermind.interact consumption
        """
        
        if 'error' in results:
            return {
                'success': False,
                'error': results['error'],
                'query': results.get('query', ''),
                'results': [],
                'metadata': results.get('metadata', {})
            }
        
        # Extract and format results from all engines
        all_results = []
        engine_stats = {}
        
        for engine, engine_data in results.get('results', {}).items():
            if isinstance(engine_data, dict) and 'results' in engine_data:
                engine_results = engine_data['results']
                engine_stats[engine] = {
                    'count': len(engine_results),
                    'status': engine_data.get('status', 'unknown')
                }
                
                # Add engine info to each result
                for result in engine_results:
                    result['source_engine'] = engine
                    all_results.append(result)
        
        # Sort by relevance (you could implement more sophisticated ranking)
        all_results.sort(key=lambda x: len(x.get('title', '')), reverse=True)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        for result in all_results:
            url = result.get('link', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return {
            'success': True,
            'query': results.get('query', ''),
            'results': unique_results[:self.config.get('max_results', 10)],
            'statistics': {
                'total_results': len(unique_results),
                'engine_stats': engine_stats,
                'engines_used': list(engine_stats.keys())
            },
            'metadata': results.get('metadata', {}),
            'suggestions': self._generate_suggestions(unique_results)
        }
    
    def _generate_suggestions(self, results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate search suggestions based on results
        """
        suggestions = []
        
        if not results:
            suggestions.extend([
                'Try a more specific search term',
                'Check your spelling',
                'Try using different keywords'
            ])
        else:
            # Extract common themes from titles
            titles = [r.get('title', '') for r in results]
            words = []
            for title in titles:
                words.extend(title.lower().split())
            
            # Find common words (simple approach)
            word_counts = {}
            for word in words:
                if len(word) > 3:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            # Suggest related searches
            common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for word, count in common_words:
                if count > 1:
                    suggestions.append(f'Try searching for "{word}"')
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get search statistics for monitoring
        """
        return self.integration.get_statistics()
    
    def clear_cache(self):
        """
        Clear the search cache
        """
        self.search_cache.clear()
        print("Search cache cleared")


# Integration function for mastermind.interact
async def mastermind_search(query: str, 
                           engines: List[str] = None,
                           use_handoff: bool = True,
                           config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Main integration function for mastermind.interact
    
    Args:
        query: Search query
        engines: Search engines to use
        use_handoff: Enable human CAPTCHA handoff
        config: Search configuration
        
    Returns:
        Formatted search results
    """
    
    handler = MastermindSearchHandler(config)
    return await handler.handle_search_request(query, engines, use_handoff)


def mastermind_search_sync(query: str, 
                          engines: List[str] = None,
                          use_handoff: bool = True,
                          config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Synchronous version for non-async contexts
    """
    return asyncio.run(mastermind_search(query, engines, use_handoff, config))


# Example usage in mastermind.interact context
def example_mastermind_integration():
    """
    Example of how to use this in mastermind.interact
    """
    
    # Configuration
    config = {
        'debug': True,
        'enable_human_handoff': True,
        'headless': False,
        'timeout': 300,
        'max_results': 10
    }
    
    # Example search queries
    test_queries = [
        "quantum computing applications 2024",
        "AI trends and developments",
        "python web scraping best practices",
        "machine learning tutorials"
    ]
    
    print("=== Mastermind Search Integration Example ===\n")
    
    for query in test_queries:
        print(f"Searching for: {query}")
        print("-" * 50)
        
        try:
            # Perform search
            results = mastermind_search_sync(
                query=query,
                engines=['duckduckgo', 'google'],
                use_handoff=True,
                config=config
            )
            
            # Display results
            if results['success']:
                print(f"✅ Search successful!")
                print(f"📊 Found {len(results['results'])} results")
                print(f"🔍 Engines used: {', '.join(results['statistics']['engines_used'])}")
                
                # Show top 3 results
                for i, result in enumerate(results['results'][:3], 1):
                    print(f"\n{i}. {result.get('title', 'No title')}")
                    print(f"   URL: {result.get('link', 'No URL')}")
                    print(f"   Source: {result.get('source_engine', 'Unknown')}")
                    if result.get('description'):
                        desc = result['description'][:100] + "..." if len(result['description']) > 100 else result['description']
                        print(f"   Description: {desc}")
                
                # Show suggestions
                if results.get('suggestions'):
                    print(f"\n💡 Suggestions:")
                    for suggestion in results['suggestions'][:3]:
                        print(f"   • {suggestion}")
                
            else:
                print(f"❌ Search failed: {results.get('error', 'Unknown error')}")
                if results.get('suggestions'):
                    print("💡 Suggestions:")
                    for suggestion in results['suggestions']:
                        print(f"   • {suggestion}")
            
        except Exception as e:
            print(f"❌ Exception occurred: {e}")
        
        print("\n" + "=" * 60 + "\n")
    
    # Show final statistics
    handler = MastermindSearchHandler(config)
    stats = handler.get_search_statistics()
    print(f"📈 Final Statistics:")
    print(f"   Total searches: {stats['total_searches']}")
    print(f"   Successful searches: {stats['successful_searches']}")
    print(f"   Success rate: {stats['success_rate']:.2%}")


# Direct integration with mastermind.interact
def integrate_with_mastermind():
    """
    Function to be called from mastermind.interact
    """
    
    # This would be called from mastermind.interact
    # The actual query would come from the user input
    
    def search_handler(user_query: str) -> Dict[str, Any]:
        """
        Handler function for mastermind.interact
        
        Args:
            user_query: The search query from the user
            
        Returns:
            Search results formatted for mastermind.interact
        """
        
        # Determine if human handoff is needed based on query complexity
        use_handoff = any(keyword in user_query.lower() for keyword in [
            'google', 'captcha', 'blocked', 'verify'
        ])
        
        # Choose engines based on query
        if 'google' in user_query.lower():
            engines = ['google']
        elif 'duckduckgo' in user_query.lower():
            engines = ['duckduckgo']
        else:
            engines = ['duckduckgo', 'google']  # Default to both
        
        # Perform search
        results = mastermind_search_sync(
            query=user_query,
            engines=engines,
            use_handoff=use_handoff,
            config={
                'debug': False,  # Disable debug in production
                'enable_human_handoff': True,
                'headless': not use_handoff,
                'timeout': 120,
                'max_results': 5
            }
        )
        
        return results
    
    return search_handler


if __name__ == "__main__":
    # Run the example
    example_mastermind_integration() 