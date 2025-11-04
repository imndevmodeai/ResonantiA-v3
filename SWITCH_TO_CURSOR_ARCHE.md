# How to Switch RISE to Use Cursor ArchE Instead of Google

**Current Default**: Google Gemini (`gemini-2.0-flash-exp`)  
**This guide shows how to switch to Cursor ArchE**

---

## 🎯 Quick Switch Methods

### Method 1: Environment Variable (Recommended)

Set the environment variable before running:

```bash
export ARCHE_LLM_PROVIDER=cursor
python run_last_rise_query.py
```

### Method 2: Modify Run Script

Edit `run_last_rise_query.py`:

```python
provider_choice = os.getenv("ARCHE_LLM_PROVIDER", "cursor")  # Change "google" to "cursor"
```

### Method 3: Pass in Context (Per-Execution)

```python
results = rise_orchestrator.process_query(
    problem_description="Your problem",
    context={"provider": "cursor"},  # Override default
    model="cursor-arche-v1"
)
```

### Method 4: System-Wide Configuration

Edit `Three_PointO_ArchE/config.py`:

```python
default_provider: str = os.getenv("ARCHE_LLM_PROVIDER", "cursor")  # Change "google" to "cursor"
```

---

## ✅ Benefits of Using Cursor ArchE

1. **No API Costs**: Direct execution, no external API calls
2. **Full Context**: Access to entire codebase, specifications, and history
3. **Self-Referential**: Can analyze and improve its own architecture
4. **RISE-SRCS Enhanced**: Perfect integration with codebase archaeology
5. **Real-Time Capabilities**: Direct tool access and code execution

---

## 🔄 Switching Back to Google

To switch back to Google Gemini:

```bash
export ARCHE_LLM_PROVIDER=google
# or unset the variable to use default
unset ARCHE_LLM_PROVIDER
python run_last_rise_query.py
```

---

**Note**: The system maintains full flexibility - you can switch providers per-execution or set system-wide defaults. Google remains the default for production stability.

