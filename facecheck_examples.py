#!/usr/bin/env python3
"""
FaceCheck.ID API Usage Examples
Demonstrates various ways to interact with the FaceCheck.ID API
"""

import requests
import json
import time
from facecheck_api_client import FaceCheckAPIClient

def example_1_basic_search():
    """Example 1: Basic search by ID"""
    print("=== Example 1: Basic Search by ID ===")
    
    client = FaceCheckAPIClient()
    search_id = "Gsf3wAtgu2U"
    
    result = client.search_by_id(search_id)
    print(f"Search ID: {search_id}")
    print(f"Status: {result.get('status', 'Unknown')}")
    print(f"Has Items: {result.get('HasItems', False)}")
    
    if result.get('HasItems'):
        items = result.get('items', [])
        print(f"Found {len(items)} matches")
        for i, item in enumerate(items[:3]):  # Show first 3 results
            print(f"  {i+1}. Score: {item.get('score', 'N/A')}, URL: {item.get('url', 'N/A')}")
    
    return result

def example_2_wait_for_completion():
    """Example 2: Wait for search completion"""
    print("\n=== Example 2: Wait for Completion ===")
    
    client = FaceCheckAPIClient()
    search_id = "Gsf3wAtgu2U"
    
    print(f"Waiting for search completion: {search_id}")
    result = client.wait_for_completion(search_id, max_wait=60, check_interval=2)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Search completed successfully!")
        print(f"Performance: {result.get('Performance', 'N/A')}")
    
    return result

def example_3_analyze_results():
    """Example 3: Analyze search results"""
    print("\n=== Example 3: Analyze Results ===")
    
    client = FaceCheckAPIClient()
    search_id = "Gsf3wAtgu2U"
    
    result = client.search_by_id(search_id, status_only=False)
    
    if result.get('HasItems'):
        items = result.get('items', [])
        
        # Group by score ranges
        score_groups = {
            "High Confidence (90-100)": [],
            "Confident Match (83-89)": [],
            "Uncertain Match (70-82)": [],
            "Weak Match (50-69)": [],
            "Very Weak (<50)": []
        }
        
        for item in items:
            score = item.get('score', 0)
            if score >= 90:
                score_groups["High Confidence (90-100)"].append(item)
            elif score >= 83:
                score_groups["Confident Match (83-89)"].append(item)
            elif score >= 70:
                score_groups["Uncertain Match (70-82)"].append(item)
            elif score >= 50:
                score_groups["Weak Match (50-69)"].append(item)
            else:
                score_groups["Very Weak (<50)"].append(item)
        
        print("Results by confidence level:")
        for group_name, group_items in score_groups.items():
            if group_items:
                print(f"  {group_name}: {len(group_items)} matches")
                for item in group_items[:2]:  # Show first 2 in each group
                    print(f"    - Score: {item.get('score')}, URL: {item.get('url', 'N/A')[:50]}...")
    
    return result

def example_4_export_results():
    """Example 4: Export results to file"""
    print("\n=== Example 4: Export Results ===")
    
    client = FaceCheckAPIClient()
    search_id = "Gsf3wAtgu2U"
    
    result = client.search_by_id(search_id, status_only=False)
    
    # Export to JSON
    filename = f"facecheck_results_{search_id}.json"
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"Results exported to: {filename}")
    
    # Export summary to text
    summary_filename = f"facecheck_summary_{search_id}.txt"
    with open(summary_filename, 'w') as f:
        f.write(f"FaceCheck.ID Search Results\n")
        f.write(f"Search ID: {search_id}\n")
        f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Status: {result.get('status', 'Unknown')}\n")
        f.write(f"Performance: {result.get('Performance', 'N/A')}\n")
        f.write(f"Has Items: {result.get('HasItems', False)}\n")
        
        if result.get('HasItems'):
            items = result.get('items', [])
            f.write(f"\nFound {len(items)} matches:\n")
            for i, item in enumerate(items, 1):
                f.write(f"{i}. Score: {item.get('score', 'N/A')}\n")
                f.write(f"   URL: {item.get('url', 'N/A')}\n")
                f.write(f"   Group: {item.get('group', 'N/A')}\n\n")
    
    print(f"Summary exported to: {summary_filename}")
    
    return result

if __name__ == "__main__":
    print("FaceCheck.ID API Examples")
    print("=" * 50)
    
    try:
        # Run examples
        example_1_basic_search()
        example_2_wait_for_completion()
        example_3_analyze_results()
        example_4_export_results()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")

