#!/usr/bin/env python3
"""
Raw Gemini API test to isolate the issue.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

def main():
    print("=== Raw Gemini API Test ===")
    
    # Load environment variables
    load_dotenv()
    
    # Configure API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set.")
        return
    
    genai.configure(api_key=api_key)
    
    # Test with a very simple prompt
    prompt = "Write a simple Python function called 'hello_world' that returns 'Hello, World!'. ONLY output the Python code."
    
    print(f"Prompt: {prompt}")
    print("\n" + "="*50 + "\n")
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.1)
        )
        
        print("Raw Response:")
        print("="*50)
        print(response.text)
        print("="*50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()