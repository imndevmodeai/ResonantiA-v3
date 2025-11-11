#!/usr/bin/env python3
"""
Test script to re-run the Mike Tyson vs George Foreman query
using the Enhanced LLM Provider exactly as done before.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.llm_providers import get_llm_provider
from Three_PointO_ArchE.enhanced_llm_provider import EnhancedLLMProvider

def main():
    """Execute the exact query as done before."""
    
    # The exact query from the specifications
    query = """Who would win in a boxing match between Mike Tyson in his prime (circa 1986-1988, age 20-22) and George Foreman in his prime (circa 1973-1974, age 24-25)? Provide a comprehensive, temporally-aware analysis that considers historical context, causal mechanisms, emergent fight dynamics, and predictive modeling across multiple time horizons."""
    
    print("=" * 80)
    print("MIKE TYSON vs GEORGE FOREMAN - Enhanced LLM Provider Query")
    print("=" * 80)
    print(f"\nQuery: {query}\n")
    print("=" * 80)
    print("\nInitializing Enhanced LLM Provider with GROQ...")
    
    try:
        # Initialize base provider (Groq - faster, no rate limits)
        base_provider = get_llm_provider("groq")
        print(f"✅ Base provider initialized: {base_provider._provider_name}")
        
        # Initialize enhanced provider with all capabilities enabled
        enhanced_provider = EnhancedLLMProvider(
            base_provider=base_provider,
            enable_multi_source_research=True,
            enable_iar_validation=True,
            enable_temporal_modeling=True,
            enable_cfp_analysis=True,
            enable_complex_system_visioning=True,
            enable_adjacent_exploration=True,
            enable_self_assessment=True,
            enable_caching=False  # Disable caching for fresh results
        )
        print(f"✅ Enhanced provider initialized with capabilities: {enhanced_provider._get_enabled_capabilities()}")
        
        print("\n" + "=" * 80)
        print("EXECUTING ENHANCED QUERY PROCESSING...")
        print("=" * 80 + "\n")
        
        # Execute the enhanced query processing with Groq model
        result = enhanced_provider.enhanced_query_processing(
            query=query,
            model="llama-3.3-70b-versatile",  # Groq's best model
            max_tokens=4000,
            temperature=0.7
        )
        
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        # Display results
        print(f"\n📊 Complexity: {result.get('complexity', 'Unknown')}")
        print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f} seconds")
        print(f"🎯 IAR Score: {result.get('iar_score', 'N/A')}")
        print(f"💯 Confidence: {result.get('confidence', 'N/A')}")
        
        if 'enhanced_capabilities_used' in result:
            print(f"\n🔧 Enhanced Capabilities Used:")
            for capability in result['enhanced_capabilities_used']:
                print(f"   - {capability}")
        
        # Display the main response
        print("\n" + "=" * 80)
        print("FINAL RESPONSE")
        print("=" * 80)
        
        if 'final_response' in result:
            print(result['final_response'])
        elif 'response' in result:
            print(result['response'])
        else:
            print("No response found in results")
        
        # Display research results if available
        if 'research_results' in result and result['research_results']:
            print("\n" + "=" * 80)
            print("RESEARCH RESULTS")
            print("=" * 80)
            for source, content in result['research_results'].items():
                print(f"\n📚 {source.upper()}:")
                if isinstance(content, dict):
                    print(json.dumps(content, indent=2))
                else:
                    print(str(content)[:500] + "..." if len(str(content)) > 500 else str(content))
        
        # Display validation results if available
        if 'validation_results' in result and result['validation_results']:
            print("\n" + "=" * 80)
            print("VALIDATION RESULTS")
            print("=" * 80)
            for method, content in result['validation_results'].items():
                print(f"\n✅ {method.upper()}:")
                if isinstance(content, dict):
                    print(json.dumps(content, indent=2))
                else:
                    print(str(content)[:500] + "..." if len(str(content)) > 500 else str(content))
        
        # Display temporal analysis if available
        if 'temporal_analysis' in result and result['temporal_analysis']:
            print("\n" + "=" * 80)
            print("TEMPORAL ANALYSIS")
            print("=" * 80)
            if isinstance(result['temporal_analysis'], dict):
                print(json.dumps(result['temporal_analysis'], indent=2))
            else:
                print(str(result['temporal_analysis']))
        
        # Display CFP analysis if available
        if 'cfp_analysis' in result and result['cfp_analysis']:
            print("\n" + "=" * 80)
            print("CFP ANALYSIS")
            print("=" * 80)
            if isinstance(result['cfp_analysis'], dict):
                print(json.dumps(result['cfp_analysis'], indent=2))
            else:
                print(str(result['cfp_analysis']))
        
        # Display complex system analysis if available
        if 'complex_system_analysis' in result and result['complex_system_analysis']:
            print("\n" + "=" * 80)
            print("COMPLEX SYSTEM ANALYSIS")
            print("=" * 80)
            if isinstance(result['complex_system_analysis'], dict):
                print(json.dumps(result['complex_system_analysis'], indent=2))
            else:
                print(str(result['complex_system_analysis']))
        
        # Display self-assessment if available
        if 'self_assessment' in result and result['self_assessment']:
            print("\n" + "=" * 80)
            print("SELF-ASSESSMENT")
            print("=" * 80)
            if isinstance(result['self_assessment'], dict):
                print(json.dumps(result['self_assessment'], indent=2))
            else:
                print(str(result['self_assessment']))
        
        # Save full results to file
        output_file = "tyson_foreman_query_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
        
        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

