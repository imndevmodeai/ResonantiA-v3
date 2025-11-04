# RISE LLM Provider Selection Guide

**Status**: ✅ Provider selection system implemented  
**Default**: Google Gemini (can be changed via environment variable or context parameter)

---

## 🎯 Provider Selection Options

RISE now supports **multiple LLM providers** with flexible selection mechanisms:

### Available Providers

1. **Google Gemini** (Default)
   - Provider name: `"google"`
   - Models: `gemini-2.0-flash-exp`, `gemini-2.5-pro`, `gemini-1.5-pro-latest`
   - Default model: `gemini-2.0-flash-exp`

2. **Cursor ArchE** (Self-Referential)
   - Provider name: `"cursor"` or `"cursor_arche"` or `"arche"`
   - Model: `cursor-arche-v1`
   - Benefits: No API costs, direct integration, full context access

3. **Groq** (High-Speed, Free Tier)
   - Provider name: `"groq"`
   - Models: `llama-3.1-70b-versatile`
   - Free tier: 14,400 requests/day

4. **OpenAI** (Available)
   - Provider name: `"openai"`
   - Models: `gpt-4o`, `gpt-4-turbo`, `gpt-3.5-turbo`

---

## 🔧 How to Select a Provider

### Method 1: Environment Variable (System-Wide Default)

Set the environment variable before running RISE:

```bash
# Use Cursor ArchE
export ARCHE_LLM_PROVIDER=cursor
python run_last_rise_query.py

# Use Google (default)
export ARCHE_LLM_PROVIDER=google
python run_last_rise_query.py

# Use Groq
export ARCHE_LLM_PROVIDER=groq
python run_last_rise_query.py
```

### Method 2: Context Parameter (Per-Execution)

Pass provider in the context when calling RISE:

```python
results = rise_orchestrator.process_query(
    problem_description="Your problem here",
    context={"provider": "cursor"},  # Override default
    model="cursor-arche-v1"  # Optional: specify model
)
```

### Method 3: Configuration File

Edit `Three_PointO_ArchE/config.py`:

```python
# In LLMConfig dataclass
default_provider: str = "cursor"  # or "google", "groq", "openai"
```

---

## 📊 Provider Selection Priority

The system selects provider in this order:

1. **Context Parameter** (highest priority)
   - `context.get("provider")` in `process_query()`

2. **Explicit Model Parameter**
   - If model contains "cursor", uses cursor provider
   - If model contains "gemini", uses google provider
   - If model contains "llama", uses groq provider

3. **Configuration Default**
   - `config.llm_config.default_provider`

4. **Environment Variable**
   - `ARCHE_LLM_PROVIDER` environment variable

5. **System Default**
   - Falls back to `"google"` if nothing specified

---

## 🎛️ Current Configuration

**System Default**: `google` (Gemini)  
**Vetting Provider**: Uses same as default (can be overridden with `ARCHE_VETTING_PROVIDER`)  
**Per-Execution Override**: Available via context parameter

---

## ✅ Benefits of Provider Selection

1. **Flexibility**: Choose the best provider for each use case
2. **Cost Optimization**: Use Cursor ArchE for self-referential queries (no API costs)
3. **Performance**: Use Groq for high-speed inference when needed
4. **Quality**: Use Google Gemini for production quality analysis
5. **Fallback**: Automatic failover capability (future enhancement)

---

## 📝 Example Usage

### Example 1: Use Cursor ArchE for Self-Referential Analysis

```python
results = rise_orchestrator.process_query(
    problem_description="Analyze ArchE's own architecture",
    context={"provider": "cursor"},
    model="cursor-arche-v1"
)
```

### Example 2: Use Google for External Analysis

```python
results = rise_orchestrator.process_query(
    problem_description="Analyze market trends in AI industry",
    context={"provider": "google"},
    model="gemini-2.0-flash-exp"
)
```

### Example 3: Use Groq for Fast Iterations

```python
results = rise_orchestrator.process_query(
    problem_description="Quick prototype analysis",
    context={"provider": "groq"},
    model="llama-3.1-70b-versatile"
)
```

---

## 🔄 Provider Propagation

Once selected, the provider is:
- Stored in `rise_state.effective_provider`
- Passed to all workflow phases (A, B, C, D)
- Used by all `generate_text_llm` actions
- Available in workflow context as `{{ provider }}` and `{{ model }}`

---

**Summary**: The system now supports flexible provider selection while maintaining Google Gemini as the default. You can override per-execution or set system-wide defaults via environment variables.

