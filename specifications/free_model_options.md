# Free LLM Model Options for ArchE

**Date**: 2025-10-28  
**Purpose**: Document free alternatives to Google API for ArchE

## Overview

ArchE currently uses Google's Gemini API, but free alternatives exist for development and cost control.

## Option 1: Groq API (RECOMMENDED)

**Why**: Fast inference, generous free tier, excellent for development

### Setup

```bash
pip install groq
```

### Configuration

Add to `Three_PointO_ArchE/llm_providers/groq.py`:

```python
import groq
from .base import BaseLLMProvider, LLMProviderError

class GroqProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMProviderError("GROQ_API_KEY not set")
        self.client = groq.Groq(api_key=api_key)
    
    def generate(self, prompt: str, model: str = "llama-3.1-70b-versatile", **kwargs) -> str:
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"Groq API error: {e}")
```

### Free Tier
- Models: llama-3.1-70b, mixtral-8x7b
- **Rate**: 14,400 requests/day (with auth)
- **Speed**: Very fast (inference optimized)
- **Registration**: https://console.groq.com

### Model Selection
Update `config.py`:

```python
llm_providers = {
    "groq": {
        "api_key": os.getenv("GROQ_API_KEY"),
        "default_model": "llama-3.1-70b-versatile",
        "temperature": 0.7,
        "max_tokens": 8192
    }
}
```

## Option 2: Ollama (Local, Completely Free)

**Why**: Runs entirely on your machine, zero API costs

### Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama3
ollama pull mistral
```

### Configuration

Add to `Three_PointO_ArchE/llm_providers/ollama.py`:

```python
import requests
from .base import BaseLLMProvider, LLMProviderError

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    def generate(self, prompt: str, model: str = "llama3", **kwargs) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            raise LLMProviderError(f"Ollama API error: {e}")
```

### Models Available
- `llama3` (8B params)
- `llama3:70b` (70B params)
- `mistral` (7B params)
- `codellama` (code-specific)

### Resources Required
- **8B models**: ~8GB RAM minimum
- **70B models**: ~40GB RAM or 2x GPU

## Option 3: Hugging Face Inference API

**Why**: Access to thousands of models, moderate free tier

### Setup

```bash
pip install huggingface_hub
```

### Configuration

```python
from huggingface_hub import InferenceClient

class HuggingFaceProvider(BaseLLMProvider):
    def __init__(self):
        self.client = InferenceClient(
            token=os.getenv("HF_API_KEY")
        )
    
    def generate(self, prompt: str, model: str = "meta-llama/Llama-3-8b", **kwargs) -> str:
        try:
            response = self.client.text_generation(
                prompt,
                model=model,
                max_new_tokens=kwargs.get("max_tokens", 512)
            )
            return response
        except Exception as e:
            raise LLMProviderError(f"HF API error: {e}")
```

### Free Tier
- **Requests**: Limited by model availability
- **Models**: Community-hosted (varying performance)
- **API Key**: https://huggingface.co/settings/tokens

## Option 4: Together AI (Free Credits)

**Why**: Simple API, free startup credits

### Setup

```bash
pip install together
```

### Configuration

```python
import together

class TogetherProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv("TOGETHER_API_KEY")
        together.api_key = api_key
    
    def generate(self, prompt: str, model: str = "meta-llama/Llama-3-8b-chat-hf", **kwargs) -> str:
        try:
            response = together.Complete.create(
                prompt=prompt,
                model=model,
                **kwargs
            )
            return response["output"]["choices"][0]["text"]
        except Exception as e:
            raise LLMProviderError(f"Together API error: {e}")
```

### Free Credits
- **New users**: $25 free credits
- **Registration**: https://together.ai

## Implementation Priority

1. **Groq** - Fastest to implement, best free tier
2. **Ollama** - If you want local/offline capability
3. **HuggingFace** - For experimentation with many models
4. **Together AI** - Simple, good for startups

## Integration with ArchE

All providers implement the `BaseLLMProvider` interface:

```python
from .llm_providers import get_llm_provider

# Automatically works with any provider
provider = get_llm_provider("groq")  # or "ollama", "huggingface", etc.
response = provider.generate(prompt, model="llama-3.1-70b")
```

The ThoughtTrail decorator (`@log_to_thought_trail`) ensures all LLM calls are logged to the database with full IAR entries.

## Next Steps

1. Choose a provider (recommend **Groq**)
2. Add the provider implementation to `llm_providers/`
3. Register it in `llm_providers/__init__.py`
4. Set environment variable (e.g., `GROQ_API_KEY`)
5. Update `config.py` to add the provider
6. Test with `generate_text_llm` action

## Cost Comparison

| Provider | Monthly Cost | Speed | Quality |
|----------|--------------|-------|---------|
| **Groq** (free tier) | $0 | ⚡⚡⚡ Fast | ⭐⭐⭐ Good |
| **Ollama** (local) | $0 | ⚡⚡ Medium | ⭐⭐⭐ Good |
| **HuggingFace** (free) | $0 | ⚡ Slow | ⭐⭐ Varies |
| **Together AI** (credits) | $0-$10 | ⚡⚡ Medium | ⭐⭐⭐ Good |
| **Google Gemini** | $0-$20+ | ⚡⚡ Medium | ⭐⭐⭐⭐ Excellent |

---

**Note**: All LLM actions are now logged to ThoughtTrail via `@log_to_thought_trail` decorator on `generate_text_llm`.

