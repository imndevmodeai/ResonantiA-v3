#!/usr/bin/env python3
"""
Comprehensive test of promising Gemini models for RISE compatibility.

Testing strategy:
1. All 2.0 models (more permissive)
2. All experimental models
3. Gemma open models
4. Latest aliases
"""

import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from Three_PointO_ArchE.llm_providers.google import GoogleProvider

# Test prompts
TEST_PROMPTS = {
    "simple": "Explain electric vehicles in 100 words.",
    
    "agent_terminology": """Create a specialized agent profile for market analysis. 
The agent should have expertise in electric vehicles and strategic planning. 
Return a JSON object with keys: 'name', 'expertise', 'background'.""",
    
    "exact_blocked_prompt": """Based on the following knowledge base and problem description, create a detailed persona for a specialized cognitive agent. The persona should be a JSON object with keys: 'name', 'expertise' (list of strings), 'background' (a detailed paragraph), 'analytical_frameworks' (list of strings), and 'strategic_patterns' (list of strings).

== KNOWLEDGE BASE ==
Electric vehicle market data from 2020-2025

== PROBLEM DESCRIPTION ==
Analyze the surge in electric vehicle adoption globally."""
}

# Promising models to test (prioritized by likelihood of success)
MODELS_TO_TEST = [
    # Already proven to work
    "gemini-2.0-flash-exp",
    
    # Stable 2.0 versions (likely to work)
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash-lite-001",
    
    # Pro experimental (worth testing)
    "gemini-2.0-pro-exp",
    "gemini-2.0-pro-exp-02-05",
    "gemini-exp-1206",
    
    # Latest aliases (could point to different models)
    "gemini-flash-latest",
    "gemini-pro-latest",
    
    # 2.5 models (likely to block but test anyway)
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    
    # Gemma open models (very permissive)
    "gemma-3-27b-it",
    "gemma-3-12b-it",
]

def test_model(provider: GoogleProvider, model: str, prompt_name: str, prompt: str):
    """Test a specific model with a specific prompt."""
    try:
        response = provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=500,
            temperature=0.7
        )
        
        return {
            "status": "✅ SUCCESS",
            "model": model,
            "prompt": prompt_name,
            "response_length": len(response),
            "response_preview": response[:150] + "..." if len(response) > 150 else response
        }
        
    except Exception as e:
        error_str = str(e)
        if "blocked" in error_str.lower():
            status = "❌ BLOCKED"
        elif "404" in error_str or "not found" in error_str.lower():
            status = "⚠️ NOT_FOUND"
        else:
            status = "❌ ERROR"
            
        return {
            "status": status,
            "model": model,
            "prompt": prompt_name,
            "error": error_str[:200]
        }

def main():
    """Run comprehensive model test."""
    print("="*100)
    print("COMPREHENSIVE GEMINI MODEL TEST FOR RISE COMPATIBILITY")
    print(f"Testing {len(MODELS_TO_TEST)} models with {len(TEST_PROMPTS)} prompts")
    print("="*100)
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)
    
    provider = GoogleProvider(api_key=api_key)
    results = []
    
    # Quick test mode: only test agent_terminology prompt (the critical one)
    critical_prompt = "agent_terminology"
    
    for i, model in enumerate(MODELS_TO_TEST, 1):
        print(f"\n[{i}/{len(MODELS_TO_TEST)}] Testing: {model}")
        print("-" * 100)
        
        try:
            result = test_model(provider, model, critical_prompt, TEST_PROMPTS[critical_prompt])
            results.append(result)
            
            if result["status"] == "✅ SUCCESS":
                print(f"  ✅ SUCCESS - {result['response_length']} chars")
                print(f"  Preview: {result['response_preview'][:100]}...")
            else:
                print(f"  {result['status']}")
                if "error" in result:
                    print(f"  Error: {result['error'][:150]}...")
                    
        except Exception as e:
            print(f"  ⚠️ Unexpected error: {e}")
            results.append({
                "status": "⚠️ ERROR",
                "model": model,
                "prompt": critical_prompt,
                "error": str(e)
            })
    
    # Summary report
    print("\n" + "="*100)
    print("SUMMARY REPORT - AGENT TERMINOLOGY TEST")
    print("="*100)
    
    successes = [r for r in results if r["status"] == "✅ SUCCESS"]
    blocked = [r for r in results if "BLOCKED" in r["status"]]
    not_found = [r for r in results if "NOT_FOUND" in r["status"]]
    errors = [r for r in results if "ERROR" in r["status"] and "NOT_FOUND" not in r["status"] and "BLOCKED" not in r["status"]]
    
    print(f"\n✅ SUCCESS: {len(successes)}/{len(MODELS_TO_TEST)} models")
    print(f"❌ BLOCKED: {len(blocked)}/{len(MODELS_TO_TEST)} models")
    print(f"⚠️ NOT_FOUND: {len(not_found)}/{len(MODELS_TO_TEST)} models")
    print(f"❌ ERROR: {len(errors)}/{len(MODELS_TO_TEST)} models")
    
    if successes:
        print("\n🎯 WORKING MODELS (RECOMMENDED):")
        for r in successes:
            print(f"  ✅ {r['model']}")
    
    if blocked:
        print("\n❌ BLOCKED MODELS (AVOID):")
        for r in blocked:
            print(f"  ❌ {r['model']}")
    
    # Save results
    output_file = Path(__file__).parent / "comprehensive_model_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "results": results,
            "summary": {
                "total_tested": len(MODELS_TO_TEST),
                "successes": len(successes),
                "blocked": len(blocked),
                "not_found": len(not_found),
                "errors": len(errors),
                "working_models": [r["model"] for r in successes],
                "blocked_models": [r["model"] for r in blocked]
            }
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {output_file}")
    
    # Final recommendation
    print("\n" + "="*100)
    print("FINAL RECOMMENDATIONS")
    print("="*100)
    
    if successes:
        print(f"\n🎯 RECOMMENDED MODELS ({len(successes)} options):")
        for i, r in enumerate(successes, 1):
            print(f"  {i}. {r['model']}")
        
        print(f"\n✅ PRIMARY RECOMMENDATION: {successes[0]['model']}")
        if len(successes) > 1:
            print(f"✅ BACKUP OPTIONS: {', '.join([r['model'] for r in successes[1:]])}")
    else:
        print("\n❌ NO WORKING MODELS FOUND")
        print("   All tested models block RISE workflow agent prompts")
        print("   Recommendation: Use Claude API or self-hosted LLM")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    main()


