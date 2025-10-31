#!/usr/bin/env python3
"""
Simple Kimi-K2 API Test
Test the API key and basic connection
"""

import os
import requests
import json

def test_kimi_api():
    """Test Kimi-K2 API connection"""
    
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        print("❌ MOONSHOT_API_KEY not found in environment")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Test payload
    payload = {
        "model": "kimi-k2-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Hello, can you confirm you're working? Please respond with 'Kimi-K2 is operational'."
            }
        ],
        "temperature": 0.6,
        "max_tokens": 100,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("🌐 Testing API connection...")
        response = requests.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ API Test Successful!")
            print(f"🤖 Response: {content}")
            return True
        else:
            print(f"❌ API Test Failed: {response.status_code}")
            print(f"📄 Error Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {str(e)}")
        return False

def test_models_list():
    """Test getting available models"""
    
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n📋 Testing models list...")
        response = requests.get(
            "https://api.moonshot.cn/v1/models",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Available Models:")
            for model in models.get('data', []):
                print(f"  • {model.get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ Models list failed: {response.status_code}")
            print(f"📄 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Models list error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Kimi-K2 API Test")
    print("=" * 50)
    
    # Test basic connection
    if test_kimi_api():
        # Test models list
        test_models_list()
    else:
        print("\n🔧 Troubleshooting Tips:")
        print("1. Verify API key is correct")
        print("2. Check if key has proper permissions")
        print("3. Ensure key is not expired")
        print("4. Try regenerating the key")
        print("5. Check Moonshot AI platform status") 