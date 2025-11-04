# Groq Default Configuration Guide

**Date**: 2025-11-03  
**Status**: ✅ ACTIVE - Groq is now the default LLM provider

## Summary of Changes

ArchE has been configured to use **Groq** as the default LLM provider throughout the RISE workflow, replacing the previous Google/Gemini default. This change provides:
- ✅ Faster inference (500+ tokens/sec)
- ✅ Cost-effective free tier
- ✅ High-quality models (Llama 3.3 70B)
- ✅ Seamless integration with existing workflows

## Changes Made

### 1. RISE Orchestrator (`Three_PointO_ArchE/rise_orchestrator.py`)
- **Default Provider**: Changed from `"google"` to `"groq"`
- **Default Model**: Changed from `"gemini-2.0-flash-exp"` to `"llama-3.3-70b-versatile"`
- **All Phases**: Phase A, B, C, and D now default to Groq
- **Fallback Logic**: If Groq model doesn't match, automatically uses provider default

### 2. Ask Arche Enhanced (`ask_arche_enhanced_v2.py`)
- **Default Provider**: Changed from `"google"` to `"groq"`
- **Default Model**: Changed from `"gemini-2.0-flash-exp"` to `"llama-3.3-70b-versatile"`
- **Auto-Configuration**: Still supports cursor detection but defaults to Groq

### 3. Groq Provider (`Three_PointO_ArchE/llm_providers/groq_provider.py`)
- ✅ Already configured to inherit from `BaseLLMProvider`
- ✅ Uses correct Groq API syntax
- ✅ Proper error handling

## How to Use

### Default Behavior (Groq)
Simply run ArchE as normal - it will use Groq automatically:
```bash
source arche_env/bin/activate
python3 ask_arche_enhanced_v2.py "Your query here"
```

### Switching to Gemini/Google (When Needed)
You can still use Gemini/Google by setting environment variables:

**Option 1: Environment Variable (Temporary)**
```bash
export ARCHE_LLM_PROVIDER="google"
export ARCHE_LLM_MODEL="gemini-2.0-flash-exp"
python3 ask_arche_enhanced_v2.py "Your query here"
```

**Option 2: Config File (Persistent)**
Modify `Three_PointO_ArchE/config.py` to set:
```python
llm.default_provider = "google"
llm.default_model = "gemini-2.0-flash-exp"
```

**Option 3: Per-Query Override**
The RISE orchestrator accepts provider/model parameters in the context:
```python
context = {
    "provider": "google",
    "model": "gemini-2.0-flash-exp"
}
```

## Groq Models Available

The system is configured to use `llama-3.3-70b-versatile` by default, but other Groq models are available:

**Recommended Models:**
- `llama-3.3-70b-versatile` - Latest, best quality, 128K context (DEFAULT)
- `llama-3.1-8b-instant` - Fastest, 131K context
- `groq/compound` - Groq's proprietary model
- `meta-llama/llama-4-maverick-17b-128e-instruct` - NEW: Llama 4 (128 experts MoE)

**To use a different Groq model:**
```bash
export ARCHE_LLM_MODEL="llama-3.1-8b-instant"
python3 ask_arche_enhanced_v2.py "Your query"
```

## Configuration Priority

The system checks for provider/model in this order:
1. **Explicit parameter** (passed in context/direct call)
2. **Config file** (`config.py` with `llm.default_provider` and `llm.default_model`)
3. **Environment variable** (`ARCHE_LLM_PROVIDER`, `ARCHE_LLM_MODEL`)
4. **Default** (Groq with `llama-3.3-70b-versatile`)

## Verification

To verify Groq is being used, check the logs for:
```
📡 RISE LLM Provider: groq | Model: llama-3.3-70b-versatile
```

Or check the output for:
```
✅ GroqProvider initialized successfully.
```

## Benefits of Groq

1. **Speed**: 500+ tokens/sec vs ~50-100 tokens/sec for Gemini
2. **Cost**: Free tier available, pay-as-you-go pricing
3. **Quality**: Llama 3.3 70B provides excellent reasoning
4. **Context**: 128K context window (larger than Gemini Flash)
5. **Reliability**: LPU (Language Processing Unit) architecture

## Troubleshooting

**Issue**: Groq API errors
- **Solution**: Ensure `GROQ_API_KEY` is set in `.env` file
- Get API key from: https://console.groq.com/keys

**Issue**: Want to switch back to Gemini
- **Solution**: Set `ARCHE_LLM_PROVIDER="google"` environment variable

**Issue**: Model not found errors
- **Solution**: Verify model name matches Groq's available models (see list above)

## Future Compatibility

✅ Gemini/Google support is **fully preserved** and can be re-enabled via:
- Environment variables
- Config file settings
- Explicit context parameters

The system is designed to seamlessly switch between providers without code changes.


