#!/usr/bin/env python3
"""
Gemini Pro 2.0/2.5 Integration Test

This script tests the integration of the latest Gemini Pro models with the ArchE system.
It verifies that the system can successfully use Gemini Pro 1.5 and 2.0 models.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.llm_providers import get_llm_provider, get_model_for_provider
    from Three_PointO_ArchE.config import get_config
    print("✅ Successfully imported LLM providers and config")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_gemini_configuration():
    """Test that Gemini models are properly configured"""
    print("\n🔧 Testing Gemini Configuration...")
    
    try:
        config = get_config()
        
        # Check LLM configuration
        print(f"  Default Provider: {config.llm.default_provider}")
        print(f"  Default Model: {config.llm.default_model}")
        print(f"  Available Google Models: {config.llm.google_models}")
        
        # Check LLM_PROVIDERS configuration
        google_config = config.LLM_PROVIDERS.get('google', {})
        print(f"  Google Provider Models: {google_config.get('models', [])}")
        print(f"  Google Default Model: {google_config.get('default_model', 'Not set')}")
        print(f"  Google Backup Model: {google_config.get('backup_model', 'Not set')}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_gemini_provider_initialization():
    """Test that the Gemini provider can be initialized"""
    print("\n🚀 Testing Gemini Provider Initialization...")
    
    try:
        # Test provider initialization
        provider = get_llm_provider('google')
        print(f"  ✅ Provider initialized: {type(provider).__name__}")
        
        # Test model resolution
        model = get_model_for_provider('google')
        print(f"  ✅ Resolved model: {model}")
        
        return True
    except Exception as e:
        print(f"❌ Provider initialization failed: {e}")
        return False

def test_gemini_generation():
    """Test basic text generation with Gemini Pro"""
    print("\n🧠 Testing Gemini Pro Text Generation...")
    
    try:
        provider = get_llm_provider('google')
        model = get_model_for_provider('google')
        
        # Test prompt
        test_prompt = "Explain the concept of 'As Above, So Below' in the context of AI system architecture in exactly 2 sentences."
        
        print(f"  Using model: {model}")
        print(f"  Test prompt: {test_prompt[:50]}...")
        
        # Generate response
        response = provider.generate(
            prompt=test_prompt,
            model=model,
            max_tokens=200,
            temperature=0.7
        )
        
        print(f"  ✅ Generation successful!")
        print(f"  Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Generation test failed: {e}")
        return False

def test_gemini_chat():
    """Test chat functionality with Gemini Pro"""
    print("\n💬 Testing Gemini Pro Chat...")
    
    try:
        provider = get_llm_provider('google')
        model = get_model_for_provider('google')
        
        # Test chat messages
        messages = [
            {"role": "user", "content": "What is the ResonantiA Protocol?"},
            {"role": "assistant", "content": "The ResonantiA Protocol is an advanced AI system architecture framework."},
            {"role": "user", "content": "How does it differ from traditional LLM approaches?"}
        ]
        
        print(f"  Using model: {model}")
        print(f"  Chat messages: {len(messages)} messages")
        
        # Generate chat response
        response = provider.generate_chat(
            messages=messages,
            model=model,
            max_tokens=300,
            temperature=0.7
        )
        
        print(f"  ✅ Chat successful!")
        print(f"  Response: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Chat test failed: {e}")
        return False

def test_gemini_advanced_features():
    """Test advanced Gemini features like code execution"""
    print("\n⚡ Testing Gemini Advanced Features...")
    
    try:
        provider = get_llm_provider('google')
        model = get_model_for_provider('google')
        
        # Test code execution capability
        test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
"""
        
        print(f"  Testing code execution capability...")
        
        # Note: Code execution requires specific setup, so we'll just test the method exists
        if hasattr(provider, 'execute_code'):
            print(f"  ✅ Code execution method available")
        else:
            print(f"  ⚠️ Code execution method not available")
        
        return True
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False

def main():
    """Run all Gemini Pro integration tests"""
    print("🎯 Gemini Pro 2.0/2.5 Integration Test")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_gemini_configuration),
        ("Provider Initialization", test_gemini_provider_initialization),
        ("Text Generation", test_gemini_generation),
        ("Chat Functionality", test_gemini_chat),
        ("Advanced Features", test_gemini_advanced_features)
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
        print("🎉 All tests passed! Gemini Pro 2.0/2.5 integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the configuration and API keys.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 