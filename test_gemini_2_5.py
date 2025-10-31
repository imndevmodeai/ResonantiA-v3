#!/usr/bin/env python3
"""
Test Gemini Pro 2.5 Integration

This script tests the integration of Gemini Pro 2.5 with the ArchE system.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv('.env')

def test_gemini_2_5_generation():
    """Test Gemini Pro 2.5 text generation"""
    print("🧠 Testing Gemini Pro 2.5 Generation...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("  ❌ No GEMINI_API_KEY found")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with gemini-2.5-pro
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        prompt = "Explain the ResonantiA Protocol v3.0 and how it implements 'As Above, So Below' principles in AI system architecture. Provide a concise 3-sentence explanation."
        
        print(f"  Testing with gemini-2.5-pro...")
        print(f"  Prompt: {prompt}")
        
        response = model.generate_content(prompt)
        
        print(f"  ✅ Generation successful!")
        print(f"  Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Generation test failed: {e}")
        return False

def test_gemini_2_5_chat():
    """Test Gemini Pro 2.5 chat functionality"""
    print("\n💬 Testing Gemini Pro 2.5 Chat...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("  ❌ No GEMINI_API_KEY found")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with gemini-2.5-pro
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        chat = model.start_chat(history=[])
        
        # First message
        response1 = chat.send_message("What is the SIRC process in the ResonantiA Protocol?")
        print(f"  Response 1: {response1.text[:100]}...")
        
        # Follow-up message
        response2 = chat.send_message("How does it differ from traditional LLM reasoning?")
        print(f"  Response 2: {response2.text[:100]}...")
        
        print(f"  ✅ Chat successful!")
        return True
        
    except Exception as e:
        print(f"  ❌ Chat test failed: {e}")
        return False

def test_arche_integration():
    """Test ArchE system integration with Gemini Pro 2.5"""
    print("\n🔧 Testing ArchE Integration...")
    
    try:
        from Three_PointO_ArchE.llm_providers import get_llm_provider, get_model_for_provider
        from Three_PointO_ArchE.config import get_config
        
        config = get_config()
        print(f"  Default Provider: {config.llm.default_provider}")
        print(f"  Default Model: {config.llm.default_model}")
        
        # Test provider initialization
        provider = get_llm_provider('google')
        model = get_model_for_provider('google')
        
        print(f"  Provider: {type(provider).__name__}")
        print(f"  Resolved Model: {model}")
        
        # Test generation through ArchE system
        test_prompt = "Explain the concept of IAR (Integrated Action Reflection) in the context of AI system architecture."
        
        response = provider.generate(
            prompt=test_prompt,
            model=model,
            max_tokens=300,
            temperature=0.7
        )
        
        print(f"  ✅ ArchE integration successful!")
        if response:
            response_text = str(response)[:100] if len(str(response)) > 100 else str(response)
            print(f"  Response: {response_text}...")
        else:
            print(f"  Response: No response received")
        
        return True
        
    except Exception as e:
        print(f"  ❌ ArchE integration test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🎯 Gemini Pro 2.5 Integration Test")
    print("=" * 50)
    
    tests = [
        ("Gemini 2.5 Generation", test_gemini_2_5_generation),
        ("Gemini 2.5 Chat", test_gemini_2_5_chat),
        ("ArchE Integration", test_arche_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Gemini Pro 2.5 integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 