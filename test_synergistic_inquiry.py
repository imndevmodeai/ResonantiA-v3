#!/usr/bin/env python3
"""
Test the complete Synergistic Inquiry and Synthesis Protocol
"""

import sys
import os
sys.path.append('/media/newbu/3626C55326C514B1/Happier')

from Three_PointO_ArchE.enhanced_perception_engine import EnhancedPerceptionEngine

def test_synergistic_inquiry():
    """Test the full Synergistic Inquiry Protocol"""
    print("🚀 Testing Synergistic Inquiry and Synthesis Protocol...")
    
    # Initialize the Enhanced Perception Engine (now the orchestrator)
    engine = EnhancedPerceptionEngine()
    
    # A query designed to hit multiple specialized domains
    query = "advanced retrieval-augmented generation techniques"
    
    print(f"📝 Genius-Level Query: '{query}'")
    
    try:
        # Execute the protocol
        result, iar = engine.search_and_analyze(query, max_results=3)
        
        print(f"\n✅ Synergistic Inquiry Completed!")
        print(f"🔢 Total Results Found: {result.get('results_count', 0)}")
        
        # Display results grouped by source
        if result.get('results_by_source'):
            print(f"\n📋 Synthesized Results by Source:")
            
            for source, results in result['results_by_source'].items():
                print(f"\n🏢 {source} ({len(results)} results):")
                for i, res in enumerate(results, 1):
                    print(f"  {i}. {res.get('title', 'No title')}")
                    print(f"     🔗 URL: {res.get('url', 'No URL')}")
                    print(f"     📝 Snippet: {res.get('snippet', 'No snippet')[:120]}...")
        
        # Display IAR reflection
        print(f"\n🧠 Meta-Cognitive Reflection (IAR):")
        print(f"   Status: {iar.get('status', 'Unknown')}")
        print(f"   Confidence: {iar.get('confidence', 0)}")
        print(f"   Summary: {iar.get('summary', 'No summary')}")
        if iar.get('potential_issues'):
            print(f"   ⚠️  Issues: {iar.get('potential_issues')}")
        
    except Exception as e:
        print(f"❌ A critical error occurred in the test script: {e}")

if __name__ == "__main__":
    test_synergistic_inquiry()
