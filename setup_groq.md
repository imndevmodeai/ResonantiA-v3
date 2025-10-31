# Groq Setup Guide for ArchE

## Quick Start

### 1. Get Your Groq API Key

Sign up at https://console.groq.com

Free tier: 14,400 requests/day (incredibly generous!)

### 2. Set the API Key

Add to your `.env` file:

```bash
GROQ_API_KEY=your_api_key_here
```

Or export it:

```bash
export GROQ_API_KEY=your_api_key_here
```

### 3. Use Groq in ArchE

You can now use Groq in two ways:

#### Option A: CLI (Command Line)

```bash
# Use Groq as provider
python -m Three_PointO_ArchE.main \
    --provider groq \
    --model llama-3.1-70b-versatile \
    your_query
```

#### Option B: In Workflows

Update any workflow to specify groq as the provider:

```json
{
  "inputs": {
    "prompt": "Your prompt here",
    "provider": "groq",
    "model": "llama-3.1-70b-versatile"
  }
}
```

### 4. Available Models

- `llama-3.1-70b-versatile` (Best quality, recommended)
- `llama-3.1-8b-instant` (Faster, smaller)
- `mixtral-8x7b-32768` (Alternative)
- `gemma-7b-it` (Good for code)

### 5. Test It!

Run this to test:

```bash
source arche_env/bin/activate
python -c "
from Three_PointO_ArchE.llm_providers import get_llm_provider
provider = get_llm_provider('groq')
response = provider.generate('Say hello!')
print(response)
"
```

## Cost Comparison

| Provider | Daily Free Requests | Speed | Quality |
|----------|---------------------|-------|---------|
| **Groq** | 14,400 | ⚡⚡⚡ Ultra Fast | ⭐⭐⭐⭐ Excellent |
| Google Gemini | Varies | ⚡⚡ Fast | ⭐⭐⭐⭐⭐ Best |

## Benefits

✅ **100% Free** (generous limits)  
✅ **Ultra-fast inference** (optimized hardware)  
✅ **High-quality models** (Llama 3.1, Mixtral)  
✅ **Automatic logging** to ThoughtTrail via `@log_to_thought_trail`

## Notes

- All Groq calls are automatically logged to `Three_PointO_ArchE/ledgers/thought_trail.db`
- The model selection hierarchy supports Groq
- Works seamlessly with existing workflows
- No code changes needed - just specify `provider: groq`

---

**Installation**: Already done! The `groq` package is installed in `arche_env`.




