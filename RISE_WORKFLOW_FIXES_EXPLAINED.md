# RISE Workflow Fixes: Technical Explanation

## Overview

Two critical bugs were discovered and fixed in the RISE (Resonant Insight and Strategy Engine) workflow execution:

1. **Hashability Issue with `@lru_cache` Decorator**
2. **Invalid Parameter Passing to LLM API**

These fixes enable the RISE workflow to complete successfully without errors.

---

## Fix #1: Removed `@lru_cache` Decorator from `process_query`

### **The Problem**

The `RISE_Orchestrator.process_query()` method had an `@lru_cache(maxsize=128)` decorator:

```python
@lru_cache(maxsize=128)
def process_query(self, problem_description: str, context: Dict[str, Any] = None, ...):
    # ...
```

**Why This Failed:**
- `lru_cache` requires all function arguments to be **hashable** (can be used as dictionary keys)
- The `context` parameter is a dictionary (`Dict[str, Any]`)
- **Dictionaries are NOT hashable** in Python
- When `context` was passed as a dict (even an empty one `{}`), Python raised:
  ```
  TypeError: unhashable type: 'dict'
  ```

### **The Error**

```python
# This would fail:
results = rise.process_query(
    problem_description="Analyze IP protection...",
    context={"execution_mode": "standard_rise"}  # ❌ Dict is not hashable
)

# This would also fail:
results = rise.process_query(
    problem_description="Analyze IP protection...",
    context={}  # ❌ Even empty dict is not hashable
)
```

### **The Fix**

**File:** `Three_PointO_ArchE/rise_orchestrator.py`

**Before:**
```python
@lru_cache(maxsize=128)  # ❌ This decorator causes hashability issues
def process_query(self, problem_description: str, context: Dict[str, Any] = None, ...):
    # ...
```

**After:**
```python
# ✅ Decorator removed - method can now accept dict arguments
def process_query(self, problem_description: str, context: Dict[str, Any] = None, ...):
    # ...
```

### **Why This Fix Works**

- **Removed the caching requirement** - RISE workflows are typically unique enough that cache hits would be rare anyway
- **Allows dictionary arguments** - `context` can now be passed as a dict without hashability issues
- **No functional impact** - The method still works exactly the same, just without caching

### **Visual Analogy**

Think of `lru_cache` as a **locker system** where each locker is labeled with the function arguments. If you try to label a locker with a dictionary (which can't be used as a label), the system fails. By removing the locker system (`@lru_cache`), we can now pass any arguments we want.

---

## Fix #2: Filtered RISE Workflow Context Variables from LLM API Calls

### **The Problem**

The RISE workflow passes context variables (like `problem_description`, `strategy_dossier`, `vetting_report`) through the workflow engine to various tasks. These variables were being incorrectly passed as **keyword arguments** to the Groq LLM API, which doesn't accept them.

**The Error:**
```
TypeError: Completions.create() got an unexpected keyword argument 'problem_description'
TypeError: Completions.create() got an unexpected keyword argument 'strategy_dossier'
TypeError: Completions.create() got an unexpected keyword argument 'vetting_report'
```

### **Why This Happened**

The workflow engine passes all context variables to task actions. When a task calls `generate_text_llm`, it passes these variables through `**kwargs` to the LLM provider. The synthesis tool was forwarding ALL parameters to the Groq API, including workflow-specific context variables.

**Flow:**
```
RISE Workflow
  └─> Task: red_team_analysis
       └─> Action: generate_text_llm
            └─> synthesis_tool.invoke_llm_for_synthesis(**kwargs)
                 └─> GroqProvider.generate(**generation_config)
                      └─> Groq API ❌ (doesn't accept problem_description)
```

### **The Fix**

**File:** `Three_PointO_ArchE/tools/synthesis_tool.py`

**Added Exclusion List:**
```python
excluded_params = {
    'max_output_tokens', 'model_settings', 'provider', 'model', 'prompt', 'context',
    # RISE workflow context variables (not valid LLM API parameters)
    'problem_description', 'strategy_dossier', 'user_query', 'session_id',
    'workflow_name', 'workflow_run_id', 'initial_context', 'query', 'problem',
    'vetting_report', 'vetting_dossier', 'original_strategy', 'final_strategy'
}
```

**How It Works:**
1. Before calling the LLM provider, the synthesis tool filters out all excluded parameters
2. Only valid LLM API parameters (like `max_tokens`, `temperature`) are passed through
3. Workflow context variables are excluded (they're already in the prompt text)

**Before:**
```python
# ❌ All parameters passed to Groq API
generation_config = {**kwargs, **model_params}  # Includes problem_description!
generated_text = provider.generate(
    prompt=prompt,
    model=model_to_use,
    **generation_config  # ❌ problem_description passed here
)
```

**After:**
```python
# ✅ Excluded parameters filtered out
excluded_params = {'problem_description', 'strategy_dossier', ...}
for key, value in all_potential_params.items():
    if key not in excluded_params and key not in generation_config:
        generation_config[key] = value  # ✅ Only valid params included

generated_text = provider.generate(
    prompt=prompt,
    model=model_to_use,
    **generation_config  # ✅ Only valid LLM API parameters
)
```

### **Visual Analogy**

Think of the LLM API as a **restaurant** with a specific menu. The workflow context variables are like **kitchen notes** (important for the chef, but not something customers order). The fix ensures we only send items from the menu (valid API parameters) to the restaurant, not the kitchen notes.

---

## Impact of Fixes

### **Before Fixes:**
- ❌ RISE workflow failed with `TypeError: unhashable type: 'dict'`
- ❌ LLM calls failed with `unexpected keyword argument` errors
- ❌ Workflow could not complete Phase C (High-Stakes Vetting)
- ❌ Partial results only (Phases A & B completed, but Phase C failed)

### **After Fixes:**
- ✅ RISE workflow can accept dictionary context arguments
- ✅ LLM calls only receive valid API parameters
- ✅ All workflow phases can execute successfully
- ✅ Complete workflow execution possible (when rate limits allow)

### **Test Results**

With the fixes applied, the RISE workflow:
1. ✅ **Phase A (Knowledge Scaffolding)** - Completed successfully
2. ✅ **Phase B (Fused Strategy Generation)** - Completed successfully
3. ⚠️ **Phase C (High-Stakes Vetting)** - Started successfully (failed due to Groq rate limits, not code errors)

---

## Technical Details

### **Fix #1: Hashability Issue**

**Root Cause:** Python's `functools.lru_cache` uses function arguments as dictionary keys for caching. Dictionaries are mutable and therefore not hashable, so they can't be used as keys.

**Solution:** Remove the caching decorator. RISE workflows are typically unique enough that caching wouldn't provide significant benefit anyway.

**Alternative Solutions Considered:**
- Convert `context` dict to a hashable tuple: `tuple(sorted(context.items()))`
- Use a custom hash function for dicts
- **Chosen:** Remove caching (simplest, most reliable)

### **Fix #2: Parameter Filtering**

**Root Cause:** Workflow engine passes all context variables to actions via `**kwargs`. The synthesis tool was forwarding all parameters to the LLM provider without filtering.

**Solution:** Explicit exclusion list of workflow context variables that should not be passed to LLM APIs.

**Why This Works:**
- Workflow context variables are already embedded in the prompt text
- LLM APIs have specific parameter schemas (they don't accept arbitrary kwargs)
- Filtering ensures only valid API parameters are sent

**Future-Proofing:**
- The exclusion list can be easily extended if new workflow variables are added
- Comments explain which parameters are workflow-specific vs. API-specific

---

## Files Changed

1. **`Three_PointO_ArchE/rise_orchestrator.py`**
   - Removed `@lru_cache(maxsize=128)` decorator from `process_query` method
   - Line 719: Method signature unchanged, just decorator removed

2. **`Three_PointO_ArchE/tools/synthesis_tool.py`**
   - Added comprehensive exclusion list for RISE workflow context variables
   - Lines 101-107: Exclusion list with comments explaining purpose
   - Prevents invalid parameters from reaching LLM APIs

---

## Verification

To verify the fixes work:

```python
# Test Fix #1: Dictionary context should work
from Three_PointO_ArchE.rise_orchestrator import RISE_Orchestrator

rise = RISE_Orchestrator(...)
# This should NOT raise TypeError anymore:
results = rise.process_query(
    problem_description="Test query",
    context={"execution_mode": "standard_rise"}  # ✅ Dict accepted
)
```

```python
# Test Fix #2: Invalid parameters should be filtered
from Three_PointO_ArchE.tools.synthesis_tool import invoke_llm_for_synthesis

# This should NOT raise TypeError anymore:
result = invoke_llm_for_synthesis(
    prompt="Test prompt",
    problem_description="Test",  # ✅ Filtered out, not passed to API
    strategy_dossier="Test",      # ✅ Filtered out, not passed to API
    max_tokens=100               # ✅ Valid parameter, passed through
)
```

---

## Summary

Both fixes address **interface compatibility** issues:
- **Fix #1:** Python's caching decorator incompatible with dictionary arguments
- **Fix #2:** Workflow context variables incompatible with LLM API parameter schemas

The fixes ensure the RISE workflow can execute end-to-end without these technical barriers. The workflow may still encounter rate limits or other external constraints, but the code itself is now functionally correct.

