#!/usr/bin/env python3
"""
Test Moonshot AI using OpenAI client
Using the correct model name and client library
"""

import os
from openai import OpenAI

def test_moonshot_openai():
    """Test Moonshot AI using OpenAI client"""
    
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        print("❌ MOONSHOT_API_KEY not found in environment")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Initialize client
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    try:
        print("🌐 Testing Moonshot AI with OpenAI client...")
        
        # Test basic chat completion
        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Hello, please respond with 'Moonshot AI test successful'."
                }
            ],
            temperature=0.3,
            max_tokens=100,
            stream=False
        )
        
        print("✅ SUCCESS! Moonshot AI is working!")
        print(f"🤖 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_gemini_search():
    """Test Gemini model search using Moonshot AI"""
    
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return False
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    try:
        print("\n🔍 Testing Gemini model search...")
        
        response = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI researcher specializing in large language models and AI technology. Provide accurate, comprehensive, and up-to-date information about AI models, particularly focusing on Google's Gemini series."
                },
                {
                    "role": "user",
                    "content": """
                    Please provide comprehensive information about the latest Gemini models from Google AI in 2025. 
                    Include the following details:
                    
                    1. Latest Gemini model names and versions
                    2. Key features and capabilities
                    3. Performance benchmarks and comparisons
                    4. Release dates and availability
                    5. Technical specifications
                    6. Use cases and applications
                    7. Pricing and access information
                    8. Integration methods and APIs
                    
                    Please provide a detailed, well-structured response with accurate, up-to-date information.
                    """
                }
            ],
            temperature=0.6,
            max_tokens=2000,
            stream=False
        )
        
        print("✅ Gemini search successful!")
        content = response.choices[0].message.content
        print(f"\n📄 Response Preview:")
        print("-" * 50)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 50)
        
        return content
        
    except Exception as e:
        print(f"❌ Gemini search failed: {e}")
        return None

def test_available_models():
    """Test getting available models"""
    
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return False
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.moonshot.ai/v1"
    )
    
    try:
        print("\n📋 Testing models list...")
        models = client.models.list()
        
        print("✅ Available Models:")
        for model in models.data:
            print(f"  • {model.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Models list failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Moonshot AI OpenAI Client Test")
    print("=" * 60)
    
    # Test basic functionality
    if test_moonshot_openai():
        # Test models list
        test_available_models()
        
        # Test Gemini search
        gemini_info = test_gemini_search()
        
        if gemini_info:
            print(f"\n🎉 SUCCESS! Moonshot AI is fully operational!")
            print(f"Ready to use for comprehensive Gemini model research.")
            
            # Save the response
            with open("moonshot_gemini_response.txt", "w", encoding="utf-8") as f:
                f.write(gemini_info)
            print(f"📁 Response saved to: moonshot_gemini_response.txt")
        else:
            print(f"\n⚠️ Basic test passed, but Gemini search failed.")
    else:
        print(f"\n❌ Moonshot AI test failed.")
        print(f"Please check your API key and try again.") 