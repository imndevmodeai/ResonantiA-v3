import os
import google.generativeai as genai
import textwrap

# --- Configuration ---
# This script reuses the same secure method of loading the API key from an environment variable.
try:
    GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
except KeyError:
    print("FATAL: GEMINI_API_KEY environment variable not set. This script cannot run.")
    exit(1)

def list_available_models():
    """
    Queries the Google Generative AI SDK to get a list of all available models
    and prints their key attributes in a structured format.
    """
    print("--- Querying for Available Google LLM Models ---")
    
    model_count = 0
    for m in genai.list_models():
        # We are primarily interested in models that support 'generateContent',
        # which is the core method our LLM Provider uses.
        if 'generateContent' in m.supported_generation_methods:
            model_count += 1
            print("\n" + "="*60)
            print(f"Model Name       : {m.name}")
            print(f"Display Name     : {m.display_name}")
            print(f"Description      : {textwrap.fill(m.description, width=60)}")
            print(f"Input Token Limit: {m.input_token_limit}")
            print(f"Output Token Limit: {m.output_token_limit}")
            print(f"Supported Methods: {m.supported_generation_methods}")
            print("="*60)

    print(f"\n--- Found {model_count} models supporting 'generateContent' ---")
    print("\nRegarding 'Templates':")
    print("The concept of 'templates' in this context typically refers to pre-defined prompt structures or 'recipes' for specific tasks (e.g., summarization, JSON generation, chatbot persona). These are implemented in the code that calls the model, not as separate API entities. We can design and store these prompt templates within our own 'Prompt Manager' as per the ResonantiA Protocol.")


if __name__ == "__main__":
    list_available_models()

