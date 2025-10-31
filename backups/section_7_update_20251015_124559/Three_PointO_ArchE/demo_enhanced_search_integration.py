#!/usr/bin/env python3
"""
Enhanced Search Integration Demonstration
Shows the complete integration of browser automation and fallback search methods
"""

import json
import logging
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_web_search_tool():
    """Demonstrate the integrated web search tool."""
    print("=" * 80)
    print("🔍 ENHANCED SEARCH INTEGRATION DEMONSTRATION")
    print("=" * 80)
    
    # Import the web search tool
    from web_search_tool import search_web
    
    # Test queries
    test_queries = [
        {
            "query": "artificial intelligence 2024",
            "num_results": 3,
            "provider": "duckduckgo"
        },
        {
            "query": "machine learning algorithms",
            "num_results": 5,
            "provider": "duckduckgo"
        },
        {
            "query": "quantum computing breakthrough",
            "num_results": 4,
            "provider": "duckduckgo"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['query']}")
        print("-" * 60)
        
        start_time = time.time()
        result = search_web(test_case)
        execution_time = time.time() - start_time
        
        # Display results
        if "result" in result and result["result"]["results"]:
            results = result["result"]["results"]
            reflection = result["reflection"]
            
            print(f"✅ SUCCESS: Found {len(results)} results in {execution_time:.2f}s")
            print(f"🔧 Method: {reflection['outputs_preview'].get('search_method', 'unknown')}")
            print(f"📊 Confidence: {reflection['confidence']}")
            print(f"⚡ Response Time: {reflection['outputs_preview'].get('response_time', 'N/A')}s")
            
            print("\n📋 Results:")
            for j, item in enumerate(results, 1):
                print(f"  {j}. {item['title']}")
                print(f"     🔗 URL: {item['url'][:80]}...")
                if item['snippet']:
                    print(f"     📝 Snippet: {item['snippet'][:100]}...")
                print()
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            if "reflection" in result:
                print(f"   Status: {result['reflection']['status']}")
                print(f"   Issues: {result['reflection']['potential_issues']}")
        
        # Brief pause between tests
        time.sleep(1)

def demo_unified_search_tool():
    """Demonstrate the unified search tool directly."""
    print("\n" + "=" * 80)
    print("🚀 UNIFIED SEARCH TOOL DIRECT DEMONSTRATION")
    print("=" * 80)
    
    # Import the unified search tool
    import sys
    from pathlib import Path
    
    tools_dir = Path(__file__).parent / "tools"
    sys.path.insert(0, str(tools_dir))
    
    try:
        from unified_search_tool import UnifiedSearchTool
        
        # Create unified search tool
        search_tool = UnifiedSearchTool()
        
        # Show capabilities
        prefs = search_tool.get_method_preferences()
        print(f"🔧 Search Tool Capabilities:")
        print(f"   Browser Automation: {'✅' if prefs['browser_automation_available'] else '❌'}")
        print(f"   Fallback Search: {'✅' if prefs['fallback_search_available'] else '❌'}")
        print(f"   Recommended Method: {prefs['recommended_method']}")
        
        # Test with force method selection
        test_query = "neural networks deep learning"
        
        print(f"\n🧪 TESTING: '{test_query}' with method selection")
        print("-" * 60)
        
        # Test fallback method specifically
        print("🔄 Testing fallback method specifically...")
        result = search_tool.search(test_query, force_method="fallback")
        
        if result["success"]:
            print(f"✅ Fallback method: {len(result['results'])} results in {result['response_time']:.2f}s")
            for i, item in enumerate(result["results"][:2], 1):
                print(f"  {i}. {item.get('title', 'No title')}")
        else:
            print(f"❌ Fallback failed: {result['error']}")
        
        # Show statistics
        stats = search_tool.get_statistics()
        print(f"\n📈 Tool Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
    except ImportError as e:
        print(f"❌ Could not import unified search tool: {e}")

def demo_performance_comparison():
    """Compare performance of different search methods."""
    print("\n" + "=" * 80)
    print("⚡ PERFORMANCE COMPARISON")
    print("=" * 80)
    
    import sys
    from pathlib import Path
    
    tools_dir = Path(__file__).parent / "tools"
    sys.path.insert(0, str(tools_dir))
    
    try:
        from fallback_search_tool import FallbackSearchTool
        
        # Test query
        test_query = "blockchain technology applications"
        
        print(f"🧪 Testing performance with query: '{test_query}'")
        print("-" * 60)
        
        # Test fallback search tool
        fallback_tool = FallbackSearchTool()
        
        start_time = time.time()
        result = fallback_tool.search(test_query)
        fallback_time = time.time() - start_time
        
        if result["success"]:
            print(f"🔄 Fallback Search: {len(result['results'])} results in {fallback_time:.2f}s")
        else:
            print(f"❌ Fallback Search failed: {result['error']}")
        
        # Show fallback tool statistics
        stats = fallback_tool.get_statistics()
        print(f"📊 Fallback Tool Stats: Success Rate: {stats['success_rate']:.1f}%")
        
    except ImportError as e:
        print(f"❌ Could not import performance tools: {e}")

def main():
    """Run the complete demonstration."""
    print("🚀 Starting Enhanced Search Integration Demonstration")
    print(f"⏰ Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Demonstrate integrated web search tool
        demo_web_search_tool()
        
        # Demonstrate unified search tool
        demo_unified_search_tool()
        
        # Performance comparison
        demo_performance_comparison()
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("🎯 Key Achievements:")
        print("   • Browser automation integration with intelligent fallback")
        print("   • HTTP-based search as reliable backup method")
        print("   • Full IAR compliance with detailed reflection data")
        print("   • Performance tracking and statistics")
        print("   • Seamless integration with existing ArchE web search tool")
        print("   • Comprehensive error handling and logging")
        print("\n🔧 Technical Implementation:")
        print("   • Unified search tool with method selection")
        print("   • Fallback search using wget and regex parsing")
        print("   • Enhanced search tool with browser automation")
        print("   • Proper import handling for different execution contexts")
        print("   • Statistics tracking across all search methods")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 