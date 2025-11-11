# Free Tier LLM Alternatives - Comprehensive Guide (2025)

**Date**: 2025-11-09  
**Purpose**: Comprehensive guide to free tier LLM APIs for ArchE when Groq rate limits are hit  
**Current Issue**: Groq hit 100,000 tokens/day limit (resets in ~16 minutes)

---

## 🚨 Current Status

**Groq Rate Limit**: 100,000 tokens/day (TPD)  
**Used**: 99,951 tokens  
**Reset Time**: ~16 minutes 42 seconds from error time  
**Note**: The 14,400 requests/day limit is separate from the 100,000 tokens/day limit

---

## ⚡ Immediate Solutions (No Implementation Needed)

### 1. **Wait for Groq Reset** (~16 minutes)
- Groq limits reset daily at midnight UTC
- Current limit: 100,000 tokens/day
- **Action**: Wait ~16 minutes or switch to another provider temporarily

### 2. **Use Google Gemini** (Already Implemented)
- **Status**: ✅ Fully implemented in ArchE
- **Free Tier**: Varies by model
- **Setup**: Already configured if `GOOGLE_API_KEY` is set
- **Usage**: Set `ARCHE_LLM_PROVIDER=google` or use in workflows

```bash
export ARCHE_LLM_PROVIDER=google
# Or in code:
provider = get_llm_provider("google")
```

---

## 🆕 New Free Tier Options (2025)

### 1. **Mistral AI** ⭐ NEW (Recommended for Quick Implementation)

**Status**: Recently launched free tier (September 2024)  
**Free Tier Details**:
- Free tier for developers to test and prototype
- Fine-tuning capabilities
- Option to upgrade for production use

**Registration**: https://console.mistral.ai  
**API Documentation**: https://docs.mistral.ai

**Implementation Priority**: ⭐⭐⭐ HIGH (Easy to implement, similar to Groq)

**Quick Setup**:
```bash
pip install mistralai
```

**Provider Implementation** (to add to `Three_PointO_ArchE/llm_providers/mistral_provider.py`):
```python
from mistralai import Mistral
from .base import BaseLLMProvider, LLMProviderError
import os

class MistralProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise LLMProviderError("MISTRAL_API_KEY not set")
        self.client = Mistral(api_key=api_key)
        super().__init__(api_key=api_key)
    
    def generate(self, prompt: str, model: str = "mistral-small-latest", **kwargs) -> str:
        try:
            response = self.client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMProviderError(f"Mistral API error: {e}")
```

**Models Available**:
- `mistral-small-latest` (recommended for free tier)
- `mistral-medium-latest`
- `mistral-large-latest`

---

### 2. **Cohere API** ⭐ NEW

**Status**: Free tier with trial tokens  
**Free Tier Details**:
- Trial tokens for new users
- Natural language processing models
- Text generation, classification, embeddings

**Registration**: https://cohere.com  
**API Documentation**: https://docs.cohere.com

**Implementation Priority**: ⭐⭐ MEDIUM

**Quick Setup**:
```bash
pip install cohere
```

**Provider Implementation**:
```python
import cohere
from .base import BaseLLMProvider, LLMProviderError
import os

class CohereProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None):
        api_key = api_key or os.getenv("COHERE_API_KEY")
        if not api_key:
            raise LLMProviderError("COHERE_API_KEY not set")
        self.client = cohere.Client(api_key=api_key)
        super().__init__(api_key=api_key)
    
    def generate(self, prompt: str, model: str = "command", **kwargs) -> str:
        try:
            response = self.client.generate(
                model=model,
                prompt=prompt,
                **kwargs
            )
            return response.generations[0].text
        except Exception as e:
            raise LLMProviderError(f"Cohere API error: {e}")
```

---

### 3. **Hugging Face Inference API** (Already Documented)

**Status**: ⚠️ Documented but not implemented  
**Free Tier**: Limited by model availability  
**Implementation Priority**: ⭐⭐ MEDIUM

**Quick Setup**:
```bash
pip install huggingface_hub
```

**Provider Implementation**: See `specifications/free_model_options.md` (Option 3)

**Models Available**: Thousands of community models
- `meta-llama/Llama-3-8b`
- `mistralai/Mistral-7B-Instruct-v0.2`
- `google/gemma-7b-it`

---

### 4. **Together AI** (Already Documented)

**Status**: ⚠️ Documented but not implemented  
**Free Tier**: $25 free credits for new users  
**Implementation Priority**: ⭐⭐ MEDIUM

**Quick Setup**:
```bash
pip install together
```

**Provider Implementation**: See `specifications/free_model_options.md` (Option 4)

**Models Available**:
- `meta-llama/Llama-3-8b-chat-hf`
- `mistralai/Mixtral-8x7B-Instruct-v0.1`

---

### 5. **Ollama** (Local, Completely Free)

**Status**: ⚠️ Documented but not implemented  
**Free Tier**: 100% free, runs locally  
**Implementation Priority**: ⭐ LOW (requires local resources)

**Quick Setup**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
ollama pull mistral
```

**Provider Implementation**: See `specifications/free_model_options.md` (Option 2)

**Resource Requirements**:
- 8B models: ~8GB RAM
- 70B models: ~40GB RAM or 2x GPU

---

## 📊 Comparison Matrix

| Provider | Free Tier | Speed | Quality | Implementation | Priority |
|----------|-----------|-------|---------|----------------|----------|
| **Groq** | 100k tokens/day | ⚡⚡⚡ Ultra Fast | ⭐⭐⭐⭐ Excellent | ✅ Implemented | ⭐⭐⭐⭐⭐ |
| **Google Gemini** | Varies | ⚡⚡ Fast | ⭐⭐⭐⭐⭐ Best | ✅ Implemented | ⭐⭐⭐⭐⭐ |
| **Mistral AI** | Free tier (new) | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | ⚠️ Not Implemented | ⭐⭐⭐ HIGH |
| **Cohere** | Trial tokens | ⚡⚡ Medium | ⭐⭐⭐ Good | ⚠️ Not Implemented | ⭐⭐ MEDIUM |
| **Hugging Face** | Limited | ⚡ Slow | ⭐⭐ Varies | ⚠️ Not Implemented | ⭐⭐ MEDIUM |
| **Together AI** | $25 credits | ⚡⚡ Medium | ⭐⭐⭐ Good | ⚠️ Not Implemented | ⭐⭐ MEDIUM |
| **Ollama** | 100% Free | ⚡⚡ Medium | ⭐⭐⭐ Good | ⚠️ Not Implemented | ⭐ LOW |

---

## 🎯 Recommended Implementation Order

### Phase 1: Quick Wins (Immediate)
1. **Use Google Gemini** (already implemented) - Set `ARCHE_LLM_PROVIDER=google`
2. **Wait for Groq reset** (~16 minutes)

### Phase 2: Fast Implementation (1-2 hours)
1. **Mistral AI** - Similar API to Groq, easy to implement
2. **Cohere** - Simple API, good for fallback

### Phase 3: Medium Priority (2-4 hours)
1. **Hugging Face** - Access to many models, but slower
2. **Together AI** - Good for startup credits

### Phase 4: Long-term (Optional)
1. **Ollama** - If local/offline capability needed

---

## 🔧 Quick Implementation Guide

### For Mistral AI (Recommended First):

1. **Install package**:
```bash
source arche_env/bin/activate
pip install mistralai
```

2. **Get API key**: https://console.mistral.ai

3. **Add to `.env`**:
```bash
MISTRAL_API_KEY=your_api_key_here
```

4. **Create provider file**: `Three_PointO_ArchE/llm_providers/mistral_provider.py` (see code above)

5. **Register in `__init__.py`**:
```python
from .mistral_provider import MistralProvider
# Add to provider registry
```

6. **Update `config.py`**:
```python
"mistral": {
    "api_key": os.getenv("MISTRAL_API_KEY"),
    "default_model": "mistral-small-latest",
    "temperature": 0.7,
    "max_tokens": 4096
}
```

7. **Use it**:
```python
provider = get_llm_provider("mistral")
```

---

## 💡 Multi-Provider Fallback Strategy

Implement automatic fallback when one provider hits rate limits:

```python
def get_llm_provider_with_fallback(provider_name: str = None):
    """Get LLM provider with automatic fallback on rate limits."""
    providers = ["groq", "google", "mistral", "cohere"]
    
    if provider_name:
        providers.insert(0, provider_name)
    
    for provider in providers:
        try:
            return get_llm_provider(provider)
        except (RateLimitError, LLMProviderError) as e:
            logger.warning(f"{provider} unavailable: {e}, trying next...")
            continue
    
    raise LLMProviderError("All providers unavailable")
```

---

## 📝 Notes

- **Groq Reset**: Daily limits reset at midnight UTC
- **Token vs Request Limits**: Groq has both 14,400 requests/day AND 100,000 tokens/day limits
- **Multiple Accounts**: Creating multiple Groq accounts may violate ToS - use alternative providers instead
- **Best Practice**: Implement multiple providers for redundancy

---

## ✅ Action Items

1. **Immediate**: Switch to Google Gemini (`export ARCHE_LLM_PROVIDER=google`)
2. **Short-term**: Implement Mistral AI provider (1-2 hours)
3. **Medium-term**: Implement Cohere provider (1-2 hours)
4. **Long-term**: Implement multi-provider fallback system

---

**Last Updated**: 2025-11-09  
**Next Review**: When new free tier options become available


