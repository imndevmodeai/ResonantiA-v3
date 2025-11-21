# Groq to Cursor Fallback Configuration

## Overview

The fallback system has been configured to use **Cursor** as the primary fallback after both Groq API keys are exhausted.

## Fallback Chain Order

1. **Groq (Key 1)** - Primary provider, first key
2. **Groq (Key 2)** - Automatic rotation when Key 1 hits rate limit (handled by MultiKeyGroqProvider)
3. **Cursor** - Primary fallback after both Groq keys exhausted
4. **Google** - Secondary fallback
5. **OpenAI** - Tertiary fallback
6. **Mistral** - Final fallback

## How It Works

### Step 1: Groq Multi-Key Rotation
- System tries `GROQ_API_KEY` first
- If rate limit hit, automatically switches to `GROQ_API_KEY_2`
- No fallback to other providers yet - still using Groq

### Step 2: Both Groq Keys Exhausted
- When both Groq keys hit rate limits
- `MultiKeyGroqProvider` raises: `"All Groq API keys have hit rate limits"`
- Fallback system detects this as rate limit error
- Registers cooldown for entire "groq" provider
- **Falls back to Cursor** (not Google/OpenAI)

### Step 3: Cursor Fallback
- System tries Cursor ArchE provider
- If Cursor fails, continues to Google, then OpenAI, then Mistral
- During Groq cooldown, skips Groq and uses Cursor

### Step 4: Cooldown Management
- Groq is skipped until cooldown expires
- After cooldown, resumes using Groq keys
- Cursor remains available as fallback

## Configuration Files Updated

### 1. `Three_PointO_ArchE/llm_providers/fallback_provider.py`
- Updated `DEFAULT_FALLBACK_CHAIN` to: `['groq', 'cursor', 'google', 'openai', 'mistral']`
- Cursor now comes right after Groq

### 2. `Three_PointO_ArchE/tools/synthesis_tool.py`
- Explicitly sets fallback chain: `['groq', 'cursor', 'google', 'openai', 'mistral']`
- Ensures Cursor is used after Groq

## Benefits

1. **Cost Efficiency**: Cursor is free (no API costs)
2. **Reliability**: Cursor doesn't have rate limits like API providers
3. **Seamless Transition**: Automatic fallback when Groq exhausted
4. **Smart Cooldown**: Remembers to skip Groq until tokens renew

## Example Flow

```
Request 1: Try Groq Key 1 → Success ✅
Request 2: Try Groq Key 1 → Rate Limit → Switch to Key 2 → Success ✅
Request 3: Try Groq Key 2 → Rate Limit → Both keys exhausted
          → Register Groq cooldown
          → Fallback to Cursor → Success ✅
Request 4: Groq in cooldown → Skip Groq → Use Cursor → Success ✅
Request 5: Groq cooldown expired → Resume Groq Key 1 → Success ✅
```

## Testing

To verify the fallback chain:

```python
from Three_PointO_ArchE.llm_providers.fallback_provider import FallbackLLMProvider

provider = FallbackLLMProvider(primary_provider='groq')
print(f"Fallback chain: {provider.fallback_chain}")
# Expected: ['groq', 'cursor', 'google', 'openai', 'mistral']
```

## Summary

✅ **Groq Key 1** → **Groq Key 2** → **Cursor** → Google → OpenAI → Mistral

The system now intelligently uses both Groq keys, then seamlessly falls back to Cursor when both are exhausted, providing maximum capacity and reliability.

