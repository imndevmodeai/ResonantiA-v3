#!/usr/bin/env python3
"""
List all available Google Gemini models via API.
"""
import os
import sys
from pathlib import Path
import google.generativeai as genai

# Load env
if Path('.env').exists():
    with open('.env') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not set")
    sys.exit(1)

genai.configure(api_key=api_key)

print("="*80)
print("AVAILABLE GOOGLE GEMINI MODELS")
print("="*80)

models = []
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        models.append({
            'name': m.name,
            'display_name': m.display_name,
            'description': m.description[:100] if m.description else "N/A",
            'input_token_limit': m.input_token_limit,
            'output_token_limit': m.output_token_limit,
        })
        print(f"\n✅ {m.name}")
        print(f"   Display: {m.display_name}")
        print(f"   Input: {m.input_token_limit:,} | Output: {m.output_token_limit:,}")
        if m.description:
            print(f"   Desc: {m.description[:200]}...")

print(f"\n{'='*80}")
print(f"Total models supporting generateContent: {len(models)}")
print(f"{'='*80}")

# Extract model IDs (without 'models/' prefix)
model_ids = [m['name'].replace('models/', '') for m in models]
print("\nModel IDs for testing:")
for mid in model_ids:
    print(f"  - {mid}")
