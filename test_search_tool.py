#!/usr/bin/env python3
"""
Test script to verify the search tool functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Three_PointO_ArchE.tools.search_tool import SearchTool

def test_search_tool():
    """Test the search tool with a simple query"""
    print("🔍 Testing Search Tool...")
    
    search_tool = SearchTool()
    
    # Test search
    query = "Alexandra Marie Dean Florida"
    print(f"Searching for: {query}")
    
    try:
        results = search_tool.search(query, num_results=3)
        print(f"Search results: {results}")
        
        if "results" in results:
            search_results = results["results"]
            print(f"Found {len(search_results)} results:")
            for i, result in enumerate(search_results, 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   URL: {result.get('href', result.get('url', 'No URL'))}")
                print(f"   Summary: {result.get('body', result.get('snippet', 'No summary'))[:100]}...")
                print()
        else:
            print("No results found or error occurred")
            
    except Exception as e:
        print(f"Error during search: {e}")

if __name__ == "__main__":
    test_search_tool() 