#!/usr/bin/env python3
"""
Moonshot AI Platform API Test
Test multiple endpoints and authentication methods
"""

import os
import requests
import json

def test_moonshot_endpoints():
    """Test different Moonshot AI endpoints"""
    
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        print("❌ MOONSHOT_API_KEY not found in environment")
        return False
    
    print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
    
    # Test different endpoints
    endpoints = [
        "https://api.moonshot.cn/v1",
        "https://api.moonshot.ai/v1",
        "https://platform.moonshot.ai/api/v1"
    ]
    
    test_payload = {
        "model": "kimi-k2-instruct",
        "messages": [
            {
                "role": "user",
                "content": "Hello, please respond with 'Test successful'."
            }
        ],
        "temperature": 0.6,
        "max_tokens": 50,
        "stream": False
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        print(f"\n🌐 Testing endpoint: {endpoint}")
        
        try:
            # Test chat completions
            response = requests.post(
                f"{endpoint}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ SUCCESS! Response: {content}")
                print(f"🎯 Working endpoint: {endpoint}")
                return endpoint
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
    
    return None

def test_models_endpoint(working_endpoint):
    """Test models endpoint with working endpoint"""
    
    api_key = os.getenv('MOONSHOT_API_KEY')
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n📋 Testing models at: {working_endpoint}")
        response = requests.get(
            f"{working_endpoint}/models",
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
            print(f"❌ Models failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Models error: {str(e)}")
        return False

def test_key_validation():
    """Test if the key is valid by checking its format and trying different auth methods"""
    
    api_key = os.getenv('MOONSHOT_API_KEY')
    if not api_key:
        return False
    
    print(f"\n🔍 Key Analysis:")
    print(f"Length: {len(api_key)} characters")
    print(f"Prefix: {api_key[:10]}...")
    print(f"Suffix: ...{api_key[-10:]}")
    
    # Test different auth header formats
    auth_formats = [
        f"Bearer {api_key}",
        f"bearer {api_key}",
        api_key,
        f"ApiKey {api_key}",
        f"X-API-Key: {api_key}"
    ]
    
    test_endpoint = "https://api.moonshot.cn/v1"
    
    for auth_format in auth_formats:
        print(f"\n🔐 Testing auth format: {auth_format[:30]}...")
        
        headers = {
            "Authorization": auth_format,
            "Content-Type": "application/json"
        }
        
        test_payload = {
            "model": "kimi-k2-instruct",
            "messages": [{"role": "user", "content": "test"}],
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                f"{test_endpoint}/chat/completions",
                headers=headers,
                json=test_payload,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"✅ SUCCESS with auth format: {auth_format[:30]}...")
                return auth_format
            else:
                print(f"❌ Failed (401): {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return None

def check_platform_status():
    """Check if Moonshot AI platform is accessible"""
    
    print("\n🌐 Checking platform status...")
    
    try:
        # Check main platform
        response = requests.get("https://platform.moonshot.ai", timeout=10)
        print(f"Platform Status: {response.status_code}")
        
        # Check API status
        response = requests.get("https://api.moonshot.cn/v1/models", timeout=10)
        print(f"API Status (no auth): {response.status_code}")
        
    except Exception as e:
        print(f"Platform check error: {str(e)}")

if __name__ == "__main__":
    print("🧪 Moonshot AI Platform Test")
    print("=" * 60)
    
    # Check platform status
    check_platform_status()
    
    # Test key validation
    working_auth = test_key_validation()
    
    # Test endpoints
    working_endpoint = test_moonshot_endpoints()
    
    if working_endpoint:
        print(f"\n🎉 SUCCESS! Found working configuration:")
        print(f"Endpoint: {working_endpoint}")
        if working_auth:
            print(f"Auth Format: {working_auth[:30]}...")
        
        # Test models
        test_models_endpoint(working_endpoint)
        
        print(f"\n✅ Ready to use Kimi-K2!")
        print(f"Update your script to use: {working_endpoint}")
        
    else:
        print(f"\n❌ No working configuration found")
        print(f"\n🔧 Troubleshooting Steps:")
        print(f"1. Verify you're logged into: https://platform.moonshot.ai")
        print(f"2. Check API key generation in console")
        print(f"3. Ensure key has proper permissions")
        print(f"4. Try regenerating the key")
        print(f"5. Contact Moonshot AI support") 