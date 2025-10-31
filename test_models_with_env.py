#!/usr/bin/env python3
"""
Test Available Models with Environment Variables

This script loads environment variables from .env files and tests what models
are available from different LLM providers.
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
load_dotenv('.env.local')

def test_gemini_models():
    """Test Gemini models with the available API key"""
    print("🔍 Testing Google Gemini Models...")
    
    try:
        import google.generativeai as genai
        
        # Check if API key is available
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("  ❌ No GEMINI_API_KEY or GOOGLE_API_KEY found")
            return []
        
        print(f"  ✅ Found API key: {api_key[:8]}...{api_key[-4:]}")
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List available models
        models = genai.list_models()
        available_models = []
        
        for model in models:
            if 'gemini' in model.name.lower():
                available_models.append({
                    'name': model.name,
                    'display_name': model.display_name,
                    'description': model.description,
                    'generation_methods': model.supported_generation_methods
                })
        
        print(f"  ✅ Found {len(available_models)} Gemini models:")
        for model in available_models:
            print(f"    - {model['name']}")
            print(f"      Display: {model['display_name']}")
            print(f"      Methods: {', '.join(model['generation_methods'])}")
        
        return [model['name'] for model in available_models]
        
    except ImportError:
        print("  ❌ Google Generative AI library not installed")
        return []
    except Exception as e:
        print(f"  ❌ Error checking Google models: {e}")
        return []

def test_openai_models():
    """Test OpenAI models if API key is available"""
    print("\n🔍 Testing OpenAI Models...")
    
    try:
        import openai
        from openai import OpenAI
        
        # Check if API key is available
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key or 'your_openai_api_key_here' in api_key:
            print("  ⚠️ No valid OPENAI_API_KEY found")
            return []
        
        print(f"  ✅ Found API key: {api_key[:8]}...{api_key[-4:]}")
        
        client = OpenAI(api_key=api_key)
        
        # List available models
        models = client.models.list()
        available_models = []
        
        for model in models.data:
            if model.id.startswith('gpt-'):
                available_models.append({
                    'id': model.id,
                    'created': model.created,
                    'owned_by': model.owned_by
                })
        
        # Sort by creation date (newest first)
        available_models.sort(key=lambda x: x['created'], reverse=True)
        
        print(f"  ✅ Found {len(available_models)} GPT models:")
        for model in available_models[:10]:  # Show top 10
            print(f"    - {model['id']} (created: {model['created']})")
        
        return [model['id'] for model in available_models]
        
    except ImportError:
        print("  ❌ OpenAI library not installed")
        return []
    except Exception as e:
        print(f"  ❌ Error checking OpenAI models: {e}")
        return []

def test_model_generation():
    """Test actual model generation with Gemini"""
    print("\n🧠 Testing Model Generation...")
    
    try:
        import google.generativeai as genai
        
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("  ❌ No API key available for testing")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test with gemini-1.5-pro
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        prompt = "Explain the concept of 'As Above, So Below' in exactly 2 sentences."
        
        print(f"  Testing with gemini-1.5-pro...")
        print(f"  Prompt: {prompt}")
        
        response = model.generate_content(prompt)
        
        print(f"  ✅ Generation successful!")
        print(f"  Response: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Generation test failed: {e}")
        return False

def check_environment_variables():
    """Check what environment variables are loaded"""
    print("🔍 Checking Loaded Environment Variables...")
    
    env_vars = {
        'GEMINI_API_KEY': os.environ.get('GEMINI_API_KEY'),
        'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY'),
    }
    
    for key_name, key_value in env_vars.items():
        if key_value and 'your_' not in key_value.lower():
            # Show first 8 characters and last 4 characters
            masked_key = f"{key_value[:8]}...{key_value[-4:]}" if len(key_value) > 12 else "***"
            print(f"  ✅ {key_name}: {masked_key}")
        else:
            print(f"  ❌ {key_name}: Not set or placeholder")
    
    return env_vars

def main():
    """Main function to test all available models"""
    print("🎯 API Models Test with Environment Variables")
    print("=" * 60)
    
    # Check environment variables
    env_vars = check_environment_variables()
    
    # Test available models
    gemini_models = test_gemini_models()
    openai_models = test_openai_models()
    
    # Test actual generation
    generation_success = test_model_generation()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    print(f"  Gemini Models Available: {len(gemini_models)}")
    print(f"  OpenAI Models Available: {len(openai_models)}")
    print(f"  Generation Test: {'✅ PASS' if generation_success else '❌ FAIL'}")
    
    if gemini_models:
        print(f"\n🎯 Available Gemini Models:")
        for model in gemini_models:
            print(f"    - {model}")
    
    if openai_models:
        print(f"\n🎯 Available OpenAI Models:")
        for model in openai_models[:5]:  # Show top 5
            print(f"    - {model}")
    
    if generation_success:
        print("\n🎉 System is ready to use Gemini Pro models!")
    else:
        print("\n⚠️ Some tests failed. Check API keys and configuration.")

if __name__ == "__main__":
    main() 