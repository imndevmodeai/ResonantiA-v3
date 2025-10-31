#!/usr/bin/env python3
"""
Test different Gemini models to identify which ones block RISE workflow prompts.

This script tests:
1. gemini-2.0-flash-exp (current default)
2. gemini-2.5-flash (newer, faster)
3. gemini-1.5-pro (older, more permissive?)
4. gemini-1.5-flash (older flash)

Testing with the EXACT prompt that gets blocked: "define_agent_persona"
"""

import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from Three_PointO_ArchE.llm_providers.google import GoogleProvider

# Test prompt that we know triggers blocking
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

# Models to test
MODELS_TO_TEST = [
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-thinking-exp",
    "gemini-2.5-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]

def test_model(provider: GoogleProvider, model: str, prompt_name: str, prompt: str):
    """Test a specific model with a specific prompt."""
    print(f"\n{'='*80}")
    print(f"Testing: {model}")
    print(f"Prompt: {prompt_name}")
    print(f"{'='*80}")
    
    try:
        response = provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=500,
            temperature=0.7
        )
        
        result = {
            "status": "✅ SUCCESS",
            "model": model,
            "prompt": prompt_name,
            "response_length": len(response),
            "response_preview": response[:200] + "..." if len(response) > 200 else response
        }
        print(f"✅ SUCCESS - Generated {len(response)} characters")
        print(f"Preview: {result['response_preview']}")
        return result
        
    except Exception as e:
        result = {
            "status": "❌ BLOCKED/ERROR",
            "model": model,
            "prompt": prompt_name,
            "error": str(e)
        }
        print(f"❌ BLOCKED/ERROR: {e}")
        return result

def main():
    """Run the test suite."""
    print("="*80)
    print("GEMINI MODEL COMPARISON TEST")
    print("Testing different models with RISE workflow prompts")
    print("="*80)
    
    # Initialize provider
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set")
        sys.exit(1)
    
    provider = GoogleProvider(api_key=api_key)
    
    # Store all results
    results = []
    
    # Test each model with each prompt
    for model in MODELS_TO_TEST:
        for prompt_name, prompt in TEST_PROMPTS.items():
            try:
                result = test_model(provider, model, prompt_name, prompt)
                results.append(result)
            except Exception as e:
                print(f"⚠️ Unexpected error testing {model} with {prompt_name}: {e}")
                results.append({
                    "status": "⚠️ ERROR",
                    "model": model,
                    "prompt": prompt_name,
                    "error": str(e)
                })
    
    # Summary report
    print("\n" + "="*80)
    print("SUMMARY REPORT")
    print("="*80)
    
    # Group by model
    for model in MODELS_TO_TEST:
        model_results = [r for r in results if r.get("model") == model]
        successes = sum(1 for r in model_results if r["status"] == "✅ SUCCESS")
        failures = sum(1 for r in model_results if "BLOCKED" in r["status"] or "ERROR" in r["status"])
        
        print(f"\n{model}:")
        print(f"  Successes: {successes}/{len(TEST_PROMPTS)}")
        print(f"  Failures:  {failures}/{len(TEST_PROMPTS)}")
        
        # Show which prompts failed
        failed_prompts = [r["prompt"] for r in model_results if "BLOCKED" in r["status"] or "ERROR" in r["status"]]
        if failed_prompts:
            print(f"  Failed on: {', '.join(failed_prompts)}")
    
    # Best model recommendation
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    # Find models with highest success rate
    model_scores = {}
    for model in MODELS_TO_TEST:
        model_results = [r for r in results if r.get("model") == model]
        successes = sum(1 for r in model_results if r["status"] == "✅ SUCCESS")
        model_scores[model] = successes
    
    best_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("\nModel Rankings (by success rate):")
    for i, (model, score) in enumerate(best_models, 1):
        percentage = (score / len(TEST_PROMPTS)) * 100
        print(f"  {i}. {model}: {score}/{len(TEST_PROMPTS)} ({percentage:.0f}%)")
    
    # Save detailed results
    output_file = Path(__file__).parent / "gemini_model_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "results": results,
            "summary": {
                "models_tested": MODELS_TO_TEST,
                "prompts_tested": list(TEST_PROMPTS.keys()),
                "best_model": best_models[0][0] if best_models else None,
                "best_score": best_models[0][1] if best_models else 0
            }
        }, f, indent=2)
    
    print(f"\n✅ Detailed results saved to: {output_file}")
    
    # Final recommendation
    if best_models and best_models[0][1] == len(TEST_PROMPTS):
        print(f"\n🎯 RECOMMENDED: Switch to {best_models[0][0]} (100% success rate)")
    elif best_models:
        print(f"\n⚠️ PARTIAL SUCCESS: {best_models[0][0]} worked best ({best_models[0][1]}/{len(TEST_PROMPTS)} prompts)")
        print("   Consider additional solutions (Claude API or self-hosted LLM)")
    else:
        print("\n❌ NO MODELS WORKED: All Gemini models blocked RISE workflow prompts")
        print("   Recommendation: Switch to Claude API or self-hosted LLM")

if __name__ == "__main__":
    main()


