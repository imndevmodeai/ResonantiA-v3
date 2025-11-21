# Multi-Key Groq Integration with Fallback System

## Overview

The system now automatically detects and uses multiple Groq API keys when available, providing intelligent key rotation and seamless integration with the fallback system.

## How It Works

### 1. Automatic Multi-Key Detection

When `get_llm_provider('groq')` is called, the system:

1. **Checks for multiple API keys** in environment variables:
   - `GROQ_API_KEY` (primary key)
   - `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, etc. (numbered keys)
   - `GROQ_API_KEY_2` (direct secondary key)

2. **Automatically uses `MultiKeyGroqProvider`** if multiple keys are detected

3. **Falls back to single-key provider** if only one key is available

### 2. MultiKeyGroqProvider Features

The `MultiKeyGroqProvider` automatically:

- **Rotates between keys** when one hits a rate limit
- **Selects the best key** based on remaining quota
- **Tracks usage** for each key individually
- **Handles rate limits** by switching to the next available key

### 3. Fallback System Integration

When all Groq keys are exhausted:

1. **MultiKeyGroqProvider** raises an error: `"All Groq API keys have hit rate limits"`
2. **Fallback Provider** detects this as a rate limit error
3. **Cooldown is registered** for the entire "groq" provider
4. **System automatically skips Groq** until cooldown expires
5. **Falls back to next provider** (e.g., Google, OpenAI)

## Example Flow

```
Query Request
    ↓
Try Groq (Key 1)
    ↓ (Rate limit hit)
Try Groq (Key 2)  ← MultiKeyGroqProvider automatically switches
    ↓ (Rate limit hit)
All Groq keys exhausted
    ↓
Fallback Provider detects rate limit
    ↓
Register cooldown for "groq" provider
    ↓
Skip Groq (cooldown active)
    ↓
Try Google (fallback provider)
    ↓
Success! ✅
```

## Configuration

### Environment Variables

Set your Groq API keys in environment variables:

```bash
export GROQ_API_KEY="your-first-key"
export GROQ_API_KEY_2="your-second-key"
# Or use numbered format:
export GROQ_API_KEY_1="your-first-key"
export GROQ_API_KEY_2="your-second-key"
```

### Using in Code

The system automatically detects and uses multiple keys:

```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Automatically uses MultiKeyGroqProvider if multiple keys detected
provider = get_llm_provider('groq')

# Or use with fallback system
from Three_PointO_ArchE.llm_providers import FallbackLLMProvider

fallback = FallbackLLMProvider(
    primary_provider='groq',  # Will use MultiKeyGroqProvider automatically
    fallback_chain=['google', 'openai']
)
```

## Benefits

1. **Increased Capacity**: 2 keys = 2x the daily token limit
2. **Automatic Failover**: Seamless switching between keys
3. **Smart Selection**: Chooses key with most remaining quota
4. **Cooldown Management**: Automatically skips exhausted providers
5. **Zero Configuration**: Works automatically when multiple keys are detected

## Logging

The system logs key usage:

```
🔑 Using MultiKeyGroqProvider with 2 API keys
Groq client initialized with key 1/2
Switched to Groq API key 2/2
⏸️ Rate limit detected for groq. Cooldown until 2025-11-21 02:40:39
⏭️ Skipping groq (rate limit cooldown, 18.5 minutes remaining)
```

## Rate Limit Handling

### Individual Key Rate Limits

When a single key hits a rate limit:
- `MultiKeyGroqProvider` automatically switches to the next key
- No cooldown is registered (other keys still available)
- Request continues with the new key

### All Keys Exhausted

When all Groq keys are exhausted:
- `MultiKeyGroqProvider` raises: `"All Groq API keys have hit rate limits"`
- Fallback system detects this as a rate limit
- Cooldown is registered for the entire "groq" provider
- System skips Groq until cooldown expires
- Falls back to next provider in chain

## Testing

To test the multi-key integration:

1. Set multiple Groq API keys in environment
2. Run a query that will hit rate limits
3. Observe logs showing key rotation
4. Verify fallback to other providers when all keys exhausted

```bash
export GROQ_API_KEY="key1"
export GROQ_API_KEY_2="key2"
python3 ask_arche_enhanced_v2.py "your query"
```

## Summary

The system now intelligently handles multiple Groq API keys:

- ✅ **Automatic detection** of multiple keys
- ✅ **Smart rotation** between keys
- ✅ **Seamless fallback** when all keys exhausted
- ✅ **Cooldown management** prevents wasted attempts
- ✅ **Zero configuration** required

This maximizes your API capacity while maintaining robust fallback behavior.

