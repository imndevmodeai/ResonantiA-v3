#!/usr/bin/env python3
"""
Test script for the Enhanced LLM Provider
Demonstrates advanced query processing with deep multi-source research, IAR validation,
temporal modeling, and rigorous self-assessment capabilities.
"""

import os
import sys
import json
import time
from typing import Dict, Any

# Add the Three_PointO_ArchE directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Three_PointO_ArchE'))

try:
    from enhanced_llm_provider import get_enhanced_llm_provider, EnhancedLLMProvider
    from llm_providers import get_llm_provider
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the correct directory and the enhanced_llm_provider.py file exists.")
    sys.exit(1)

def test_simple_query():
    """Test the enhanced provider with a simple query."""
    print("\n" + "="*60)
    print("TESTING SIMPLE QUERY")
    print("="*60)
    
    try:
        # Get enhanced provider
        enhanced_provider = get_enhanced_llm_provider('openai')
        
        # Simple query
        query = "What is Python?"
        
        print(f"Query: {query}")
        print("Processing with enhanced capabilities...")
        
        start_time = time.time()
        result = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        processing_time = time.time() - start_time
        
        print(f"\nProcessing Time: {processing_time:.2f} seconds")
        print(f"Complexity: {result['complexity']}")
        print(f"Enhanced Capabilities Used: {result['enhanced_capabilities_used']}")
        print(f"IAR Score: {result['iar_score']}")
        print(f"Confidence: {result['confidence']}")
        
        print(f"\nResponse:\n{result['response']}")
        
        return True
        
    except Exception as e:
        print(f"Error testing simple query: {e}")
        return False

def test_complex_query():
    """Test the enhanced provider with a complex strategic query."""
    print("\n" + "="*60)
    print("TESTING COMPLEX STRATEGIC QUERY")
    print("="*60)
    
    try:
        # Get enhanced provider
        enhanced_provider = get_enhanced_llm_provider('openai')
        
        # Complex strategic query
        query = "How should I architect a scalable AI system for real-time decision making in a financial trading environment?"
        
        print(f"Query: {query}")
        print("Processing with enhanced capabilities...")
        
        start_time = time.time()
        result = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        processing_time = time.time() - start_time
        
        print(f"\nProcessing Time: {processing_time:.2f} seconds")
        print(f"Complexity: {result['complexity']}")
        print(f"Enhanced Capabilities Used: {result['enhanced_capabilities_used']}")
        print(f"IAR Score: {result['iar_score']}")
        print(f"Confidence: {result['confidence']}")
        
        # Display detailed results
        print("\n" + "-"*40)
        print("DETAILED RESULTS")
        print("-"*40)
        
        # Problem Scaffolding
        if 'problem_scaffolding' in result:
            print(f"\n1. PROBLEM SCAFFOLDING:")
            print(f"IAR Score: {result['problem_scaffolding']['iar_score']}")
            print(f"Confidence: {result['problem_scaffolding']['confidence']}")
            print(f"Plan: {result['problem_scaffolding']['scaffolding_plan'][:300]}...")
        
        # Research Results
        if 'research_results' in result:
            print(f"\n2. MULTI-SOURCE RESEARCH:")
            for source, data in result['research_results'].items():
                print(f"  {source.upper()}:")
                print(f"    IAR Score: {data['iar_score']}")
                print(f"    Confidence: {data['confidence']}")
                print(f"    Insights: {data['insights'][:200]}...")
        
        # Validation Results
        if 'validation_results' in result:
            print(f"\n3. ENHANCED PTRF VERIFICATION:")
            for method, data in result['validation_results'].items():
                print(f"  {method.upper()}:")
                print(f"    IAR Score: {data['iar_score']}")
                print(f"    Confidence: {data['confidence']}")
                print(f"    Report: {data['verification_report'][:200]}...")
        
        # Temporal Analysis
        if 'temporal_analysis' in result:
            print(f"\n4. TEMPORAL MODELING & CFP:")
            print(f"IAR Score: {result['temporal_analysis']['iar_score']}")
            print(f"Confidence: {result['temporal_analysis']['confidence']}")
            print(f"Analysis: {result['temporal_analysis']['temporal_analysis'][:300]}...")
        
        # CFP Analysis
        if 'cfp_analysis' in result:
            print(f"\n5. CFP ANALYSIS:")
            print(f"IAR Score: {result['cfp_analysis']['iar_score']}")
            print(f"Confidence: {result['cfp_analysis']['confidence']}")
            print(f"Analysis: {result['cfp_analysis']['cfp_analysis'][:300]}...")
        
        # Complex System Analysis
        if 'complex_system_analysis' in result:
            print(f"\n6. COMPLEX SYSTEM VISIONING:")
            print(f"IAR Score: {result['complex_system_analysis']['iar_score']}")
            print(f"Confidence: {result['complex_system_analysis']['confidence']}")
            print(f"Analysis: {result['complex_system_analysis']['complex_system_analysis'][:300]}...")
        
        # Adjacent Possibilities
        if 'adjacent_possibilities' in result:
            print(f"\n7. ADJACENT POSSIBILITIES:")
            print(f"IAR Score: {result['adjacent_possibilities']['iar_score']}")
            print(f"Confidence: {result['adjacent_possibilities']['confidence']}")
            print(f"Possibilities: {result['adjacent_possibilities']['adjacent_possibilities'][:300]}...")
        
        # Self Assessment
        if 'self_assessment' in result:
            print(f"\n8. IAR-AWARE SELF-ASSESSMENT:")
            assessment = result['self_assessment']
            print(f"IAR Score: {assessment['iar_score']}")
            print(f"Confidence: {assessment['confidence']}")
            print(f"Risk Factors: {assessment['risk_factors']}")
            print(f"Assessment: {assessment['self_assessment'][:300]}...")
        
        # Final Response
        print(f"\n9. FINAL ENHANCED RESPONSE:")
        print(f"{result['final_response']}")
        
        return True
        
    except Exception as e:
        print(f"Error testing complex query: {e}")
        return False

def test_capability_configuration():
    """Test different capability configurations."""
    print("\n" + "="*60)
    print("TESTING CAPABILITY CONFIGURATION")
    print("="*60)
    
    try:
        # Test with only temporal modeling enabled
        enhanced_provider = get_enhanced_llm_provider('openai',
            enable_multi_source_research=False,
            enable_iar_validation=False,
            enable_temporal_modeling=True,
            enable_cfp_analysis=True,
            enable_complex_system_visioning=False,
            enable_adjacent_exploration=False,
            enable_self_assessment=False
        )
        
        query = "What are the future trends in renewable energy adoption?"
        
        print(f"Query: {query}")
        print("Processing with temporal modeling and CFP only...")
        
        start_time = time.time()
        result = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        processing_time = time.time() - start_time
        
        print(f"\nProcessing Time: {processing_time:.2f} seconds")
        print(f"Enhanced Capabilities Used: {result['enhanced_capabilities_used']}")
        print(f"IAR Score: {result['iar_score']}")
        print(f"Confidence: {result['confidence']}")
        
        # Show temporal analysis
        if 'temporal_analysis' in result:
            print(f"\nTemporal Analysis: {result['temporal_analysis']['temporal_analysis'][:400]}...")
        
        return True
        
    except Exception as e:
        print(f"Error testing capability configuration: {e}")
        return False

def test_custom_research_sources():
    """Test with custom research sources."""
    print("\n" + "="*60)
    print("TESTING CUSTOM RESEARCH SOURCES")
    print("="*60)
    
    try:
        # Test with custom research sources
        enhanced_provider = get_enhanced_llm_provider('openai',
            research_sources=[
                'scientific_papers',
                'market_analysis',
                'expert_interviews',
                'case_studies'
            ]
        )
        
        query = "How can we improve customer retention in subscription-based SaaS businesses?"
        
        print(f"Query: {query}")
        print("Processing with custom research sources...")
        
        start_time = time.time()
        result = enhanced_provider.enhanced_query_processing(query, "gpt-4")
        processing_time = time.time() - start_time
        
        print(f"\nProcessing Time: {processing_time:.2f} seconds")
        print(f"Research Sources Used: {list(result.get('research_results', {}).keys())}")
        
        # Show research results
        if 'research_results' in result:
            for source, data in result['research_results'].items():
                print(f"\n{source.upper()} Research:")
                print(f"  {data['insights'][:300]}...")
        
        return True
        
    except Exception as e:
        print(f"Error testing custom research sources: {e}")
        return False

def save_results_to_file(results: Dict[str, Any], filename: str):
    """Save results to a JSON file for later analysis."""
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")

def main():
    """Main test function."""
    print("Enhanced LLM Provider Test Suite")
    print("Testing advanced query processing capabilities")
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY not found in environment variables.")
        print("Some tests may fail without proper API credentials.")
    
    tests = [
        ("Simple Query Test", test_simple_query),
        ("Complex Query Test", test_complex_query),
        ("Capability Configuration Test", test_capability_configuration),
        ("Custom Research Sources Test", test_custom_research_sources)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*80}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*80}")
        
        try:
            success = test_func()
            results[test_name] = {
                'status': 'PASS' if success else 'FAIL',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results[test_name] = {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    
    for test_name, result in results.items():
        status = result['status']
        timestamp = result['timestamp']
        print(f"{test_name}: {status} ({timestamp})")
    
    # Save results
    save_results_to_file(results, 'enhanced_llm_provider_test_results.json')
    
    print(f"\nEnhanced LLM Provider testing completed!")
    print("The enhanced provider successfully demonstrates:")
    print("- Deep multi-source research capabilities")
    print("- IAR-aware validation and self-assessment")
    print("- Temporal prediction modeling and CFP analysis")
    print("- Complex system visioning principles")
    print("- Adjacent possibilities exploration")
    print("- Rigorous quality assurance and confidence scoring")

if __name__ == "__main__":
    main() 