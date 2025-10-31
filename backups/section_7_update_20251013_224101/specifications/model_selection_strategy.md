# ArchE Model Selection Strategy: Cost-Optimized Intelligence

## Executive Summary

This document defines ArchE's intelligent model selection strategy, optimizing for **cost efficiency** while maintaining cognitive excellence. By matching model capabilities to specific workflow requirements, we achieve up to **97% cost reduction** on routine operations while reserving premium models for complex strategic thinking.

---

## 📊 Google Gemini Model Portfolio Analysis

### Pricing Reference (per million tokens)

| Model | Input (≤128K) | Output (≤128K) | Input (>128K) | Output (>128K) | Best For |
|-------|---------------|----------------|---------------|----------------|----------|
| **gemini-2.5-pro** | $1.25 | $10.00 | $2.50 | $15.00 | Complex reasoning, large context |
| **gemini-2.5-flash** | $0.075 | $0.30 | $0.15 | $0.60 | Fast responses, medium complexity |
| **gemini-2.5-flash-lite** | ~$0.04 | ~$0.15 | ~$0.08 | ~$0.30 | Simple tasks, high volume |
| **gemini-2.0-flash-thinking** | $0.075 | $0.30 | $0.15 | $0.60 | Step-by-step reasoning |

**Cost Comparison Example** (1M input + 1M output tokens):
- `gemini-2.5-pro`: $11.25 💰💰💰
- `gemini-2.5-flash`: $0.375 💰
- `gemini-2.5-flash-lite`: $0.19 ✅ (97% savings!)

---

## 🎯 ArchE Workflow Classification & Model Mapping

### Tier 1: Strategic Deep Thought (Use `gemini-2.5-pro`)
**Characteristics**: High complexity, large context windows, multi-step reasoning, novel problem solving

**Cost Justification**: These are the "moments that matter" - complex strategic analysis where quality directly impacts outcomes.

**ArchE Workflows**:
1. **Phase B: Fused Strategy Synthesis** (`workflows/strategy_fusion.json`)
   - Temperature: 0.5, Max Tokens: 2500
   - Synthesizes analytical, creative, and specialist insights
   - **Recommendation**: `gemini-2.5-pro` 
   - **Rationale**: Large context (combines multiple prior analyses), requires deep synthesis

2. **Phase C: High-Stakes Vetting** (`workflows/high_stakes_vetting.json`) - Final Strategy Generation
   - Temperature: 0.4, Max Tokens: 2000
   - Integrates vetting dossier feedback into refined strategy
   - **Recommendation**: `gemini-2.5-pro`
   - **Rationale**: Mission-critical quality assurance, extensive context

3. **Phase A: Forge Specialist Agent** (`workflows/knowledge_scaffolding.json` - final task)
   - Temperature: 0.3, Max Tokens: 2500
   - Creates complete specialized agent persona
   - **Recommendation**: `gemini-2.5-pro`
   - **Rationale**: Large output requirement, critical for downstream quality

**Estimated Usage**: ~15% of total LLM calls
**Cost Impact**: High per-call, but represents only core strategic moments

---

### Tier 2: Analytical Processing (Use `gemini-2.5-flash`)
**Characteristics**: Medium complexity, standard reasoning, structured analysis, moderate output

**Cost Justification**: 97% cheaper than Pro, but still maintains excellent analytical capabilities.

**ArchE Workflows**:
1. **Phase A: Problem Deconstruction** (`workflows/knowledge_scaffolding.json`)
   - Temperature: 0.3, Max Tokens: 2000
   - Analyzes problem into core components
   - **Recommendation**: `gemini-2.5-flash`
   - **Rationale**: Structured analysis, not requiring massive context

2. **Phase A: Specialization Requirements Analysis**
   - Temperature: 0.4, Max Tokens: 2000
   - Identifies required expertise
   - **Recommendation**: `gemini-2.5-flash`

3. **Phase B: Pathway Insights** (Analytical/Specialist)
   - Temperature: 0.1-0.5, Max Tokens: 1500
   - Structured perspective analysis
   - **Recommendation**: `gemini-2.5-flash`

4. **Phase C: Red Team Analysis**
   - Temperature: 0.8, Max Tokens: 1500
   - Critical review (requires creativity but not massive context)
   - **Recommendation**: `gemini-2.5-flash`

5. **Phase C: Ethical Review**
   - Temperature: 0.5, Max Tokens: 1500
   - Bias and ethics assessment
   - **Recommendation**: `gemini-2.5-flash`

6. **Phase D: SPR Distillation** (`workflows/distill_spr.json`)
   - Temperature: 0.3, Max Tokens: 1000
   - Knowledge compression
   - **Recommendation**: `gemini-2.5-flash`

**Estimated Usage**: ~60% of total LLM calls
**Cost Impact**: Medium volume, but dramatically cheaper than Pro

---

### Tier 3: Fast Operations (Use `gemini-2.5-flash-lite` or `gemini-flash-latest`)
**Characteristics**: Simple extraction, validation, formatting, low token count

**Cost Justification**: 98% cheaper than Pro. Perfect for high-volume, low-complexity operations.

**ArchE Workflows**:
1. **Phase A: Domain Extraction** (`workflows/knowledge_scaffolding.json`)
   - Temperature: 0.1, Max Tokens: 100 ⚡
   - Simple JSON field extraction
   - **Recommendation**: `gemini-2.5-flash-lite`
   - **Rationale**: Tiny output, simple task - no need for premium model

2. **Phase A: Validate Search Results**
   - Temperature: 0.2, Max Tokens: 500
   - Binary quality check
   - **Recommendation**: `gemini-flash-latest`

3. **Phase A: Validate Specialist Agent**
   - Temperature: 0.2, Max Tokens: 1500
   - Structured validation checklist
   - **Recommendation**: `gemini-flash-latest`

4. **Metamorphosis: Validate Agent Structure**
   - Temperature: 0.1, Max Tokens: 1000
   - JSON validation and fixing
   - **Recommendation**: `gemini-2.5-flash-lite`

**Estimated Usage**: ~25% of total LLM calls
**Cost Impact**: High volume, but negligible cost

---

### Tier 4: Experimental/Specialized (Use case-specific)

**`gemini-2.0-flash-thinking-exp`**:
- **Use For**: Complex multi-step reasoning where showing work is valuable
- **ArchE Application**: Could replace Pro for certain strategic analysis tasks
- **Cost**: Same as Flash ($0.075/$0.30)
- **Trade-off**: Longer latency but potentially better quality at Flash pricing
- **Recommendation**: Experimental for Phase B pathway analysis

**`gemini-2.5-flash-preview-tts`**:
- **Use For**: Voice-enabled Nexus Dashboard (future)
- **ArchE Application**: Audio output for Guardian interaction
- **Status**: Future enhancement

---

## 🛠️ Implementation Strategy

### 1. Workflow-Level Model Override System

Create a **tiered configuration** file:

```json
{
  "model_tiers": {
    "strategic": "gemini-2.5-pro",
    "analytical": "gemini-2.5-flash", 
    "operational": "gemini-flash-latest",
    "experimental": "gemini-2.0-flash-thinking-exp"
  },
  "workflow_model_mapping": {
    "knowledge_scaffolding": {
      "deconstruct_problem": "analytical",
      "extract_domain_from_deconstruction": "operational",
      "acquire_domain_knowledge": "analytical",
      "validate_search_results": "operational",
      "analyze_specialization_requirements": "analytical",
      "forge_specialist_agent": "strategic",
      "validate_specialist_agent": "operational"
    },
    "strategy_fusion": {
      "pathway_analytical_insight": "analytical",
      "pathway_creative_insight": "analytical",
      "pathway_specialist_consultation": "analytical",
      "synthesize_fused_dossier": "strategic"
    },
    "high_stakes_vetting": {
      "red_team_analysis": "analytical",
      "ethical_and_bias_review": "analytical",
      "dystopian_simulation": "analytical",
      "generate_final_strategy": "strategic"
    },
    "distill_spr": {
      "format_distillation_prompt": "operational",
      "distill_spr_with_llm": "analytical",
      "parse_and_validate_spr": "operational"
    }
  },
  "fallback_model": "gemini-2.5-flash"
}
```

### 2. Enhanced Model Selection Hierarchy

**Updated Priority**:
1. **Explicit task-level override**: `"model": "gemini-2.5-pro"` (highest)
2. **Workflow tier mapping**: Uses config above
3. **CLI argument**: `--model gemini-2.5-flash`
4. **Provider default**: `gemini-2.5-flash` (fallback)

### 3. Implementation Files to Modify

**`Three_PointO_ArchE/model_config.json`** (new file):
```json
{
  "cost_optimization_enabled": true,
  "model_tiers": { ... },
  "workflow_model_mapping": { ... }
}
```

**`Three_PointO_ArchE/action_registry.py`**:
- Add model tier lookup before auto-injection
- Check if task_key + workflow_name has a tier mapping
- Resolve tier to actual model name

**`Three_PointO_ArchE/llm_providers/__init__.py`**:
- Update `get_model_for_provider()` default to `gemini-2.5-flash`
- Add `get_model_for_tier(tier: str)` function

---

## 📈 Cost Impact Analysis

### Scenario: Project Janus Business Plan (Full RISE Workflow)

**Without Optimization** (all calls use `gemini-2.5-pro`):
- Average tokens per call: 3,000 input + 1,500 output
- Total LLM calls in RISE: ~50
- **Cost per run**: 
  - Input: 50 × 3K × $1.25/1M = $0.1875
  - Output: 50 × 1.5K × $10/1M = $0.75
  - **Total**: ~$0.94 per query

**With Optimization** (tiered model selection):
- Strategic calls (15%): 8 calls × $0.01875 = $0.15
- Analytical calls (60%): 30 calls × $0.001125 = $0.034
- Operational calls (25%): 12 calls × $0.000475 = $0.006
- **Total**: ~$0.19 per query

**💰 Savings**: **80% cost reduction** ($0.94 → $0.19)

**Annual Impact** (assuming 1000 RISE queries/year):
- Before: $940/year
- After: $190/year
- **Savings**: $750/year

For a system running **10,000 queries/year** across all query types:
- **Before**: ~$9,400/year
- **After**: ~$1,900/year
- **🎉 Total Savings: $7,500/year**

---

## 🚀 Rollout Plan

### Phase 1: Foundation (Immediate)
1. ✅ Update default model to `gemini-2.5-flash` in `llm_providers/__init__.py`
2. ✅ Verify all workflows work with Flash model
3. ✅ Document current model usage in logs

### Phase 2: Intelligent Routing (Week 1)
1. Create `model_config.json` with tier definitions
2. Implement tier lookup in `action_registry.py`
3. Add tier resolution logging for monitoring

### Phase 3: Optimization (Week 2)
1. Update specific workflow tasks with explicit model overrides
2. A/B test: Pro vs Flash on analytical tasks (quality validation)
3. Monitor cost reduction vs quality metrics

### Phase 4: Advanced Features (Future)
1. Dynamic model selection based on query complexity detection
2. Automatic cost tracking dashboard in Nexus UI
3. Budget-aware query routing (throttle to cheaper models near limit)

---

## 🎓 Best Practices for Guardians

### When to Use Each Tier

**Use `gemini-2.5-pro` when**:
- Query requires synthesizing 5+ sources
- Output quality directly impacts business decisions
- Context window > 50K tokens
- Novel problem with no established patterns

**Use `gemini-2.5-flash` when**:
- Standard analytical tasks
- Structured data processing
- Temperature < 0.6 (deterministic output)
- 90% of your use cases ✅

**Use `gemini-flash-latest` when**:
- Simple extractions (pull one field from JSON)
- Validation/verification tasks
- Template filling
- Max tokens < 500

### CLI Usage Examples

```bash
# Let system use optimized tier selection (recommended)
python arche_cli.py "Analyze market trends"

# Force Flash for cost-sensitive queries
python arche_cli.py "Analyze market trends" --model gemini-2.5-flash

# Force Pro for critical strategic decisions
python arche_cli.py "Create 3-year business plan" --model gemini-2.5-pro

# Use thinking model for complex reasoning
python arche_cli.py "Debug this algorithm" --model gemini-2.0-flash-thinking-exp
```

---

## 📋 Summary: Recommended Defaults

| Context | Recommended Model | Rationale |
|---------|------------------|-----------|
| **System Default** | `gemini-2.5-flash` | Best balance of cost/quality |
| **CLI Override** | User's choice | Explicit control when needed |
| **Strategic Tasks** | `gemini-2.5-pro` | Quality-critical decisions |
| **Routine Tasks** | `gemini-flash-latest` | High volume, low cost |
| **Experimental** | `gemini-2.0-flash-thinking-exp` | Complex reasoning at Flash pricing |

---

## 🔍 Monitoring & Validation

Track these metrics in ThoughtTrail:
1. **Cost per query** (by model tier)
2. **Quality score** (confidence ratings)
3. **Latency** (response time by model)
4. **Tier distribution** (% of calls per tier)

**Success Criteria**:
- ✅ 70%+ cost reduction vs all-Pro baseline
- ✅ No degradation in confidence scores for analytical tasks
- ✅ Strategic tasks maintain >0.9 confidence
- ✅ Average query cost < $0.25

---

## 🎯 Next Actions

1. **Immediate**: Update `get_model_for_provider()` to return `gemini-2.5-flash` ✅
2. **This Week**: Create `model_config.json` and implement tier lookup
3. **Test**: Run Project Janus with optimized routing
4. **Validate**: Compare quality metrics between Pro and Flash on sample tasks
5. **Document**: Add cost savings to system health metrics

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-25  
**Author**: ArchE Cognitive System  
**Status**: Ready for Implementation

