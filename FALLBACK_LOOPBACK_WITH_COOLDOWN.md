# Fallback Loopback with Rate Limit Cooldown

## Overview

The fallback system now implements a **circuit breaker pattern with time-based cooldowns**. When a rate limit is detected, the provider is automatically skipped for a period of time (until tokens renew) rather than trying it again on every call.

## How It Works

### 1. Rate Limit Detection

When an LLM call fails, the system checks if it's a rate limit error:
- Detects patterns like "rate limit", "429", "quota", "tokens per day", "TPD"
- Extracts reset time from error messages
- Registers the provider in a cooldown period

### 2. Cooldown Period

Once a rate limit is detected:
- **Extracts reset time** from error message (e.g., "Please try again in 3m2.304s")
- **Sets cooldown** until the reset time
- **Skips provider** automatically during cooldown
- **Resumes provider** when cooldown expires

### 3. Automatic Loopback

During cooldown:
- Provider is **automatically skipped** in the fallback chain
- System **tries next provider** immediately
- **No wasted attempts** on rate-limited providers
- **Efficient resource usage**

## Example Flow

```
Call 1: Groq (rate limit hit)
  → Detects: "Rate limit reached, try again in 23m51s"
  → Registers cooldown until 2025-11-21 03:00:00
  → Tries Google (succeeds)

Call 2 (5 minutes later): Groq (still in cooldown)
  → Checks cooldown: 18 minutes remaining
  → Skips Groq automatically
  → Tries Google directly (succeeds)

Call 3 (25 minutes later): Groq (cooldown expired)
  → Checks cooldown: expired
  → Tries Groq (succeeds)
  → Cooldown cleared
```

## Usage

### Basic Usage

```python
from Three_PointO_ArchE.llm_providers.fallback_provider import FallbackLLMProvider

# Create fallback provider
provider = FallbackLLMProvider(
    primary_provider='groq',
    fallback_chain=['groq', 'google', 'openai', 'mistral']
)

# Use normally - cooldown happens automatically
response = provider.generate(
    prompt="Your prompt here",
    model="llama-3.3-70b-versatile"
)
```

### Check Cooldown Status

```python
# Check which providers are in cooldown
status = provider.get_cooldown_status()
for provider_name, info in status.items():
    if info.get('in_cooldown'):
        print(f"{provider_name}: {info['remaining_minutes']:.1f} minutes remaining")

# Get full statistics
stats = provider.get_fallback_stats()
print(f"Rate limit cooldowns: {stats['rate_limit_cooldowns']}")
```

### Manual Cooldown Management

```python
# Clear cooldown for specific provider
provider.clear_cooldown('groq')

# Clear all cooldowns
provider.clear_cooldown()
```

## Rate Limit Detection

The system detects rate limits from various error formats:

### Groq Format
```
Rate limit reached for model `llama-3.3-70b-versatile` in organization 
`org_xxx` service tier `on_demand` on tokens per day (TPD): Limit 100000, 
Used 99980, Requested 223. Please try again in 23m51.648s.
```
→ Extracts: 23 minutes, 51.648 seconds
→ Cooldown until: now + 23m51.648s

### Generic Format
```
Rate limit exceeded. Please try again in 3m2.304s
```
→ Extracts: 3 minutes, 2.304 seconds
→ Cooldown until: now + 3m2.304s

### Fallback
If reset time cannot be parsed:
→ Default cooldown: 1 hour

## Integration

### Automatic in Synthesis Tool

The `synthesis_tool.py` automatically uses fallback provider when enabled:

```python
# Environment variable
ARCHE_ENABLE_LLM_FALLBACK=true

# Or in code
response = invoke_llm_for_synthesis(
    prompt="...",
    provider="groq",
    enable_fallback=True  # Enables cascading fallback with cooldown
)
```

### In RISE Orchestrator

The fallback provider can be used in RISE:

```python
from Three_PointO_ArchE.llm_providers.fallback_provider import FallbackLLMProvider

# In RISE context
context = {
    'provider': FallbackLLMProvider(
        primary_provider='groq',
        fallback_chain=['groq', 'google', 'openai']
    )
}
```

## Benefits

1. **Efficiency**: No wasted API calls to rate-limited providers
2. **Automatic**: Cooldown management is transparent
3. **Smart**: Extracts actual reset times from error messages
4. **Resilient**: Automatically resumes when cooldown expires
5. **Observable**: Full statistics and cooldown status available

## Statistics

The fallback provider tracks:
- Total calls
- Primary successes
- Fallback activations
- Fallback successes
- Provider usage counts
- Rate limit cooldowns (active and expired)
- Rate limit detection history

## Configuration

### Environment Variables

```bash
# Enable fallback provider
ARCHE_ENABLE_LLM_FALLBACK=true

# Enable Zepto compression with fallback
ARCHE_ENABLE_ZEPTO_LLM=true
```

### Code Configuration

```python
provider = FallbackLLMProvider(
    primary_provider='groq',
    fallback_chain=['groq', 'google', 'openai', 'mistral', 'cursor'],
    enable_zepto=True,  # Also compress prompts
    api_keys={
        'groq': 'your_groq_key',
        'google': 'your_google_key',
        # ... etc
    }
)
```

## Files Modified

- `Three_PointO_ArchE/llm_providers/fallback_provider.py`: Added cooldown tracking
- `Three_PointO_ArchE/tools/synthesis_tool.py`: Integrated fallback provider
- `Three_PointO_ArchE/llm_providers/zepto_llm_wrapper.py`: Enhanced error handling for fallback

## Example Output

```
🔄 Trying provider: groq
⚠️  Provider groq rate limited: Rate limit reached...
⏸️  Rate limit detected for groq. Cooldown until 2025-11-21 03:00:00 (23.9 minutes remaining).
🔄 Looping back to next provider in chain (will skip groq until cooldown expires)...
🔄 Trying provider: google
✅ Provider google succeeded
```

On next call:
```
⏭️  Skipping groq (rate limit cooldown, 18.5 minutes remaining)
🔄 Trying provider: google
✅ Provider google succeeded
```

## Next Steps

1. **Test with Rate Limits**: Verify cooldown works correctly
2. **Monitor Cooldowns**: Track cooldown effectiveness
3. **Optimize Reset Time Parsing**: Improve extraction accuracy
4. **Add Persistence**: Save cooldowns across restarts (optional)

