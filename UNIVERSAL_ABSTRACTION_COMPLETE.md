# Universal Abstraction - Complete Refactoring

## Problem Identified

The original implementation had **hardcoded domain-specific logic** in `ask_arche_enhanced_v2.py`:
- `_generate_monetization_analysis()` - hardcoded monetization prompts
- `_generate_market_analysis()` - hardcoded market analysis
- `_generate_quantum_analysis()` - hardcoded quantum analysis
- `_generate_system_analysis()` - hardcoded system analysis
- `_generate_default_analysis()` - generic fallback

This violated the principle of **universal abstraction** - the system should work for ANY query type, not just specific domains.

## Solution: Universal Capability-Driven Approach

### New Architecture

1. **Query Analysis Phase** (`_analyze_query_for_response_strategy`)
   - Uses the Query Enhancement Engine to analyze ANY query
   - Extracts: intent, complexity, required capabilities, analysis types, temporal scope
   - No hardcoded domain logic

2. **Universal Response Generation** (`_generate_universal_response`)
   - Dynamically constructs LLM prompt based on query analysis
   - Works for ANY query type (monetization, market, quantum, system, or any other)
   - Leverages discovered capabilities automatically

3. **Dynamic Prompt Construction** (`_construct_dynamic_prompt`)
   - Builds prompt based on:
     - Query intent (detected dynamically)
     - Complexity level (from enhancement engine)
     - Required capabilities (discovered automatically)
     - Analysis types needed (causal, predictive, simulation, etc.)
     - Temporal scope (if applicable)
     - Query structure (if enhanced query has phases)
   - **No hardcoded domain-specific prompts**

4. **Template Fallback** (`_generate_template_response`)
   - Generic template when LLM unavailable
   - Uses query analysis to populate template
   - No domain-specific logic

## Key Improvements

### ✅ Universal Abstraction
- Works for ANY query type
- No hardcoded domain logic
- Completely capability-driven

### ✅ Dynamic Capability Discovery
- Automatically discovers required capabilities
- Leverages SPRs detected in query
- Uses analysis types from enhancement engine

### ✅ Intelligent Prompt Construction
- Builds prompts based on query analysis
- Includes relevant guidance for each analysis type
- Adapts to complexity level

### ✅ Maintainability
- Single code path for all queries
- Easy to extend (just add new capabilities)
- No need to add new domain-specific methods

## How It Works

```
User Query
    ↓
Query Enhancement Engine (analyzes query)
    ↓
Query Analysis (intent, complexity, capabilities, etc.)
    ↓
Dynamic Prompt Construction (based on analysis)
    ↓
LLM Generation (universal, capability-driven)
    ↓
Formatted Response (with metadata)
```

## Example: Monetization Query

**Before (Hardcoded):**
```python
if "monetize" in query:
    return await self._generate_monetization_analysis(query, spr_context)
```

**After (Universal):**
```python
query_analysis = await self._analyze_query_for_response_strategy(query)
# Analysis detects: intent='monetization', complexity='very_complex', 
# required_capabilities=['market_analysis', 'predictive_modeling', ...]
prompt = self._construct_dynamic_prompt(query, query_analysis, spr_context)
# Prompt automatically includes monetization guidance based on analysis
response = await self._generate_universal_response(query, query_analysis, spr_context)
```

## Benefits

1. **Works for ANY query** - not just monetization, market, quantum, system
2. **Automatically adapts** - uses discovered capabilities and analysis types
3. **Easy to extend** - add new capabilities, not new methods
4. **Maintainable** - single code path, no duplication
5. **Intelligent** - leverages query enhancement engine's full analysis

## Deprecated Methods

All domain-specific methods have been marked as `_DEPRECATED`:
- `_generate_monetization_analysis_DEPRECATED`
- `_generate_market_analysis_DEPRECATED`
- `_generate_quantum_analysis_DEPRECATED`
- `_generate_system_analysis_DEPRECATED`
- `_generate_default_analysis_DEPRECATED`

These are kept for reference but are no longer called. All queries now use the universal approach.

## Testing

Test with ANY query type:
- "How to monetize ArchE" → Universal approach
- "Analyze market trends" → Universal approach
- "Quantum computing security" → Universal approach
- "System health check" → Universal approach
- "Any other query" → Universal approach

All queries now go through the same universal, capability-driven pipeline.

---

**Status**: ✅ Complete - System is now universally abstracted to the nth level

