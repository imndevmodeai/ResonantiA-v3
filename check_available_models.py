#!/usr/bin/env python3
"""
Check Available API Models

This script checks what models are currently available from different LLM providers
and compares them with the configured models in the ArchE system.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_openai_models():
    """Check available OpenAI models"""
    print("🔍 Checking OpenAI Models...")
    
    try:
        import openai
        from openai import OpenAI
        
        # Check if API key is available
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("  ⚠️ No OPENAI_API_KEY found in environment")
            return []
        
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

def check_google_models():
    """Check available Google Gemini models"""
    print("\n🔍 Checking Google Gemini Models...")
    
    try:
        import google.generativeai as genai
        
        # Check if API key is available
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            print("  ⚠️ No GOOGLE_API_KEY found in environment")
            return []
        
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

def check_anthropic_models():
    """Check available Anthropic Claude models"""
    print("\n🔍 Checking Anthropic Claude Models...")
    
    try:
        import anthropic
        
        # Check if API key is available
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            print("  ⚠️ No ANTHROPIC_API_KEY found in environment")
            return []
        
        client = anthropic.Anthropic(api_key=api_key)
        
        # List available models
        models = client.models.list()
        available_models = []
        
        for model in models.data:
            if 'claude' in model.id.lower():
                available_models.append({
                    'id': model.id,
                    'name': model.name,
                    'created': model.created
                })
        
        # Sort by creation date (newest first)
        available_models.sort(key=lambda x: x['created'], reverse=True)
        
        print(f"  ✅ Found {len(available_models)} Claude models:")
        for model in available_models:
            print(f"    - {model['id']} ({model['name']})")
        
        return [model['id'] for model in available_models]
        
    except ImportError:
        print("  ❌ Anthropic library not installed")
        return []
    except Exception as e:
        print(f"  ❌ Error checking Anthropic models: {e}")
        return []

def check_configured_models():
    """Check what models are configured in the ArchE system"""
    print("\n🔍 Checking Configured Models in ArchE...")
    
    try:
        from Three_PointO_ArchE.config import get_config
        
        config = get_config()
        
        print("  📋 LLM Configuration:")
        print(f"    Default Provider: {config.llm.default_provider}")
        print(f"    Default Model: {config.llm.default_model}")
        print(f"    Temperature: {config.llm.temperature}")
        print(f"    Max Tokens: {config.llm.max_tokens}")
        
        print("\n  📋 Available Models by Provider:")
        for provider, config_data in config.LLM_PROVIDERS.items():
            print(f"    {provider.upper()}:")
            print(f"      Models: {config_data.get('models', [])}")
            print(f"      Default: {config_data.get('default_model', 'Not set')}")
            if 'backup_model' in config_data:
                print(f"      Backup: {config_data['backup_model']}")
        
        return config.LLM_PROVIDERS
        
    except Exception as e:
        print(f"  ❌ Error checking configured models: {e}")
        return {}

def check_environment_variables():
    """Check what API keys are available in environment"""
    print("\n🔍 Checking Environment Variables...")
    
    api_keys = {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'GOOGLE_API_KEY': os.environ.get('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY'),
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            # Show first 8 characters and last 4 characters
            masked_key = f"{key_value[:8]}...{key_value[-4:]}" if len(key_value) > 12 else "***"
            print(f"  ✅ {key_name}: {masked_key}")
        else:
            print(f"  ❌ {key_name}: Not set")
    
    return api_keys

def compare_available_vs_configured():
    """Compare available models vs configured models"""
    print("\n🔍 Comparing Available vs Configured Models...")
    
    # Get available models
    openai_models = check_openai_models()
    google_models = check_google_models()
    anthropic_models = check_anthropic_models()
    
    # Get configured models
    configured = check_configured_models()
    
    print("\n📊 Comparison Results:")
    
    # Check OpenAI
    if 'openai' in configured:
        configured_openai = configured['openai'].get('models', [])
        missing_openai = [model for model in configured_openai if model not in openai_models]
        new_openai = [model for model in openai_models if model not in configured_openai]
        
        print(f"  OpenAI:")
        print(f"    Configured: {configured_openai}")
        print(f"    Available: {openai_models}")
        if missing_openai:
            print(f"    ⚠️ Missing: {missing_openai}")
        if new_openai:
            print(f"    🆕 New available: {new_openai}")
    
    # Check Google
    if 'google' in configured:
        configured_google = configured['google'].get('models', [])
        missing_google = [model for model in configured_google if model not in google_models]
        new_google = [model for model in google_models if model not in configured_google]
        
        print(f"  Google:")
        print(f"    Configured: {configured_google}")
        print(f"    Available: {google_models}")
        if missing_google:
            print(f"    ⚠️ Missing: {missing_google}")
        if new_google:
            print(f"    🆕 New available: {new_google}")

def main():
    """Main function to check all available models"""
    print("🎯 API Models Availability Check")
    print("=" * 60)
    
    # Check environment variables first
    api_keys = check_environment_variables()
    
    # Check configured models
    configured = check_configured_models()
    
    # Check available models from APIs
    compare_available_vs_configured()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Summary:")
    print("=" * 60)
    
    total_keys = len(api_keys)
    available_keys = sum(1 for key in api_keys.values() if key is not None)
    
    print(f"  API Keys: {available_keys}/{total_keys} available")
    print(f"  Configured Providers: {len(configured)}")
    
    if available_keys == 0:
        print("\n⚠️ No API keys found! Please set the required environment variables:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("  export GOOGLE_API_KEY='your-key-here'")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
    else:
        print("\n✅ Ready to use available models!")

if __name__ == "__main__":
    main() 