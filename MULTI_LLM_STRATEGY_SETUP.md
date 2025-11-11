# Multi-LLM Strategy Setup Guide

**Status**: ✅ Fully Implemented  
**Purpose**: Intelligent multi-provider LLM system with quota tracking and automatic fallback

---

## 🎯 Features

1. **Multiple Groq API Keys**: Support for multiple Groq keys with automatic rotation
2. **Quota Tracking**: Real-time tracking of usage and limits for all providers
3. **Intelligent Selection**: Automatically selects best available provider
4. **Automatic Fallback**: Switches providers when rate limits are hit
5. **Unified Interface**: Handles provider-specific syntax differences automatically

---

## 🚀 Quick Setup

### Step 1: Configure Multiple Groq API Keys

Add to your `.env` file:

```bash
# Primary Groq key
GROQ_API_KEY=your_primary_groq_key_here

# Additional Groq keys (optional)
GROQ_API_KEY_1=your_second_groq_key_here
GROQ_API_KEY_2=your_third_groq_key_here
# ... add as many as you have
```

**Note**: You can create multiple Groq accounts to get more free tier quota. Each account gets:
- 14,400 requests/day
- 100,000 tokens/day

### Step 2: Use the Intelligent Orchestrator

**Option A: Environment Variable**
```bash
export ARCHE_LLM_PROVIDER=intelligent
python run_analysis.sh
```

**Option B: In Code**
```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Use intelligent orchestrator
provider = get_llm_provider("intelligent")
response = provider.generate("Your prompt here")
```

**Option C: Update Config**
```python
# In Three_PointO_ArchE/config.py
default_provider: str = "intelligent"
```

---

## 📊 How It Works

### 1. Provider Selection Priority

The orchestrator tries providers in this order:
1. **Groq** (free tier, fast) - with multi-key support
2. **Mistral** (free tier, fast)
3. **Google Gemini** (free tier available, high quality)
4. **OpenAI** (paid, high quality)

### 2. Quota Management

- **Tracks usage** for each provider and API key
- **Monitors limits**: requests/day, tokens/day, requests/minute
- **Automatic rotation**: Switches to best available key/provider
- **Persistent storage**: Saves quota data to `outputs/llm_quota_tracker.json`

### 3. Automatic Fallback

When a provider hits rate limits:
1. **Multi-key Groq**: Automatically switches to next available key
2. **Provider fallback**: Switches to next available provider
3. **Error handling**: Graceful degradation with detailed logging

### 4. Parameter Normalization

The orchestrator automatically handles provider-specific differences:
- `max_tokens` vs `max_output_tokens` (Google uses max_output_tokens)
- Model name differences
- Temperature and other parameter variations

---

## 🔧 Configuration Options

### Enable/Disable Multi-Key Groq

```python
from Three_PointO_ArchE.llm_providers import IntelligentLLMOrchestrator

# Enable multi-key (default)
orchestrator = IntelligentLLMOrchestrator(enable_multi_key_groq=True)

# Disable multi-key (use single key)
orchestrator = IntelligentLLMOrchestrator(enable_multi_key_groq=False)
```

### Set Preferred Provider

```python
# Prefer Google Gemini
orchestrator = IntelligentLLMOrchestrator(preferred_provider="google")

# Prefer Mistral
orchestrator = IntelligentLLMOrchestrator(preferred_provider="mistral")
```

---

## 📈 Usage Statistics

Get statistics about provider usage:

```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

provider = get_llm_provider("intelligent")
response = provider.generate("Test prompt")

# Get statistics
stats = provider.get_stats()
print(stats)
# {
#     "total_calls": 10,
#     "provider_calls": {"groq": 7, "google": 3},
#     "fallbacks": 2,
#     "errors": 0,
#     "current_provider": "groq",
#     "available_providers": ["groq", "google", "mistral"],
#     "quota_summary": {...}
# }
```

---

## 🔍 Quota Tracking

### View Quota Status

```python
from Three_PointO_ArchE.llm_providers.quota_tracker import get_quota_tracker

tracker = get_quota_tracker()

# Get summary for all providers
summary = tracker.get_usage_summary()
print(summary)

# Get summary for specific provider
groq_summary = tracker.get_usage_summary(provider="groq")
print(groq_summary)
```

### Example Output

```json
{
  "groq": {
    "groq_key_1": {
      "tokens_per_day": {
        "used": 85000,
        "limit": 100000,
        "remaining": 15000,
        "usage_percent": 85.0,
        "available": true,
        "reset_time": "2025-11-10T00:00:00"
      }
    },
    "groq_key_2": {
      "tokens_per_day": {
        "used": 25000,
        "limit": 100000,
        "remaining": 75000,
        "usage_percent": 25.0,
        "available": true,
        "reset_time": "2025-11-10T00:00:00"
      }
    }
  }
}
```

---

## 🎛️ Advanced Usage

### Manual Provider Selection

You can still use specific providers directly:

```python
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Use specific provider
groq_provider = get_llm_provider("groq")
google_provider = get_llm_provider("google")
mistral_provider = get_llm_provider("mistral")
```

### Multi-Key Groq Direct Usage

```python
from Three_PointO_ArchE.llm_providers import MultiKeyGroqProvider

# Initialize with multiple keys
provider = MultiKeyGroqProvider(api_keys=[
    "key1",
    "key2",
    "key3"
])

# Get usage summary
summary = provider.get_usage_summary()
print(summary)
```

---

## 🛠️ Troubleshooting

### Issue: "No available LLM providers"

**Solution**: 
1. Check that at least one API key is set in `.env`
2. Check quota status: `tracker.get_usage_summary()`
3. Wait for quota reset (typically midnight UTC for daily limits)

### Issue: "All Groq API keys have hit rate limits"

**Solution**:
1. Add more Groq API keys (create additional accounts)
2. Wait for quota reset
3. The orchestrator will automatically use other providers (Mistral, Google)

### Issue: Provider not switching automatically

**Solution**:
1. Check that multiple providers are configured
2. Verify API keys are set correctly
3. Check logs for error messages

---

## 📝 Best Practices

1. **Multiple Groq Keys**: Create 2-3 Groq accounts for redundancy
2. **Monitor Quotas**: Regularly check `get_stats()` to track usage
3. **Provider Diversity**: Configure multiple providers (Groq, Mistral, Google)
4. **Error Handling**: The orchestrator handles errors automatically, but monitor logs
5. **Cost Optimization**: The system prefers free tier providers automatically

---

## 🔄 Migration from Single Provider

If you're currently using a single provider:

**Before**:
```python
provider = get_llm_provider("groq")
response = provider.generate(prompt)
```

**After** (just change provider name):
```python
provider = get_llm_provider("intelligent")
response = provider.generate(prompt)
```

The orchestrator will automatically:
- Use Groq if available
- Fall back to other providers if needed
- Handle all provider-specific differences

---

## ✅ Verification

Test the system:

```bash
source arche_env/bin/activate
python -c "
from Three_PointO_ArchE.llm_providers import get_llm_provider

# Test intelligent orchestrator
provider = get_llm_provider('intelligent')
response = provider.generate('Say hello!')
print(f'Response: {response}')

# Check stats
stats = provider.get_stats()
print(f'Stats: {stats}')
"
```

---

## 📊 Expected Behavior

1. **First call**: Uses Groq (if available)
2. **Rate limit hit**: Automatically switches to next Groq key or next provider
3. **All Groq exhausted**: Falls back to Mistral, then Google
4. **Quota reset**: Automatically detects reset and uses provider again

---

**Status**: ✅ Ready to use! Just configure multiple API keys and use `provider="intelligent"`.


