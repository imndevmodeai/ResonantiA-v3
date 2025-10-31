# Optimal Token Limits by Task Complexity

## 🎯 Core Principle

**All Gemini models (Pro, Flash, Flash-Lite) support 65,536 output tokens.**

Our goal: **Match token limits to task complexity**, not arbitrary conservative values from legacy configurations.

---

## 📊 Recommended Token Limits by Task Type

### Extraction Tasks (Simple → Fast)
**Characteristics**: Pull specific data, format conversion, single-field extraction

**Optimal Settings**:
```json
{
  "max_tokens": 500,
  "temperature": 0.1
}
```

**ArchE Examples**:
- `extract_domain_from_deconstruction`: Extract single domain name
- `parse_and_validate_spr`: Extract JSON fields
- Simple yes/no validation

**Rationale**: These tasks require minimal output. Setting higher limits wastes processing time.

---

### Validation Tasks (Medium → Structured)
**Characteristics**: Check quality, verify structure, provide feedback

**Optimal Settings**:
```json
{
  "max_tokens": 1500,
  "temperature": 0.2
}
```

**ArchE Examples**:
- `validate_search_results`: Quality assessment
- `validate_specialist_agent`: Completeness check
- `validate_agent_structure`: JSON validation

**Rationale**: Validation reports need enough space for detailed feedback but don't require essays.

---

### Analytical Tasks (Large → Comprehensive)
**Characteristics**: Deep analysis, structured reasoning, multi-point findings

**Optimal Settings**:
```json
{
  "max_tokens": 8192,
  "temperature": 0.3-0.5
}
```

**ArchE Examples**:
- `deconstruct_problem`: Multi-dimensional problem breakdown
- `analyze_specialization_requirements`: Detailed capability analysis
- `pathway_analytical_insight`: First-principles reasoning
- `red_team_analysis`: Comprehensive vulnerability assessment
- `ethical_and_bias_review`: Detailed ethical review

**Rationale**: Analytical tasks benefit from thoroughness. 8K tokens = ~6000 words, enough for comprehensive analysis without bloat.

---

### Strategic Synthesis (X-Large → Comprehensive)
**Characteristics**: Integrate multiple sources, create actionable plans, detailed strategies

**Optimal Settings**:
```json
{
  "max_tokens": 16384,
  "temperature": 0.4-0.6
}
```

**ArchE Examples**:
- `synthesize_fused_dossier`: Integrate analytical + creative + specialist insights
- `generate_final_strategy`: Create vetted, comprehensive strategy
- `forge_specialist_agent`: Detailed agent persona with frameworks
- **Project Janus Business Plan**: Year-by-year roadmap with detailed actions

**Rationale**: Strategic outputs are the **core value proposition** of ArchE. Don't artificially limit quality. 16K tokens = ~12,000 words = executive-quality strategic document.

---

### Creative Exploration (Large → Divergent)
**Characteristics**: Brainstorming, unconventional ideas, exploratory thinking

**Optimal Settings**:
```json
{
  "max_tokens": 8192,
  "temperature": 0.8-0.9
}
```

**ArchE Examples**:
- `pathway_creative_insight`: Outside-the-box solutions
- `dystopian_simulation`: Creative stress-test narrative

**Rationale**: Creativity needs space to explore, but 8K is sufficient for diverse ideation.

---

## 🔄 Updated Workflow Configurations

### workflows/knowledge_scaffolding.json

**Before** (Overly Conservative):
```json
{
  "deconstruct_problem": {
    "model_settings": {"temperature": 0.3, "max_tokens": 2000}
  }
}
```

**After** (Optimized):
```json
{
  "deconstruct_problem": {
    "model_settings": {"temperature": 0.3, "max_tokens": 8192},
    "model": "{{ model }}"
  },
  "extract_domain_from_deconstruction": {
    "model_settings": {"temperature": 0.1, "max_tokens": 500}
  },
  "validate_search_results": {
    "model_settings": {"temperature": 0.2, "max_tokens": 1500}
  },
  "analyze_specialization_requirements": {
    "model_settings": {"temperature": 0.4, "max_tokens": 8192}
  },
  "forge_specialist_agent": {
    "model_settings": {"temperature": 0.3, "max_tokens": 16384}
  },
  "validate_specialist_agent": {
    "model_settings": {"temperature": 0.2, "max_tokens": 1500}
  }
}
```

---

### workflows/strategy_fusion.json

**Before**:
```json
{
  "pathway_analytical_insight": {
    "model_settings": {"temperature": 0.1, "max_tokens": 1500}
  },
  "synthesize_fused_dossier": {
    "model_settings": {"temperature": 0.5, "max_tokens": 2500}
  }
}
```

**After**:
```json
{
  "pathway_analytical_insight": {
    "model_settings": {"temperature": 0.1, "max_tokens": 8192}
  },
  "pathway_creative_insight": {
    "model_settings": {"temperature": 0.9, "max_tokens": 8192}
  },
  "pathway_specialist_consultation": {
    "model_settings": {"temperature": 0.5, "max_tokens": 8192}
  },
  "synthesize_fused_dossier": {
    "model_settings": {"temperature": 0.5, "max_tokens": 16384}
  }
}
```

---

### workflows/high_stakes_vetting.json

**Before**:
```json
{
  "red_team_analysis": {
    "model_settings": {"temperature": 0.8, "max_tokens": 1500}
  },
  "generate_final_strategy": {
    "model_settings": {"temperature": 0.4, "max_tokens": 2000}
  }
}
```

**After**:
```json
{
  "red_team_analysis": {
    "model_settings": {"temperature": 0.8, "max_tokens": 8192}
  },
  "ethical_and_bias_review": {
    "model_settings": {"temperature": 0.5, "max_tokens": 8192}
  },
  "dystopian_simulation": {
    "model_settings": {"temperature": 0.9, "max_tokens": 8192}
  },
  "generate_final_strategy": {
    "model_settings": {"temperature": 0.4, "max_tokens": 16384}
  }
}
```

---

### workflows/distill_spr.json

**Before**:
```json
{
  "distill_spr_with_llm": {
    "model_settings": {"temperature": 0.3, "max_tokens": 1000}
  }
}
```

**After**:
```json
{
  "distill_spr_with_llm": {
    "model_settings": {"temperature": 0.3, "max_tokens": 4096}
  },
  "parse_and_validate_spr": {
    "model_settings": {"temperature": 0.1, "max_tokens": 500}
  }
}
```

---

## 💰 Cost Impact Analysis

### Key Insight: **We only pay for tokens actually generated, not the limit**

**Scenario**: Strategic synthesis task

**Before**:
- `max_tokens: 2500`
- Model generates: 2400 tokens (hits limit, truncated!)
- Cost: 2400 × $0.30/1M = $0.00072
- **Problem**: Response is truncated, incomplete strategy

**After**:
- `max_tokens: 16384`
- Model generates: 8500 tokens (natural completion)
- Cost: 8500 × $0.30/1M = $0.00255
- **Result**: Complete, high-quality strategy

**Cost Difference**: $0.00183 more (~3x)  
**Value Difference**: Complete vs truncated = **PRICELESS** ✅

### The Math:
- If response naturally completes at 3000 tokens, we pay for 3000 regardless of limit
- If response needs 8000 tokens but limit is 2500, we get garbage
- **Setting appropriate limits costs nothing extra, prevents truncation**

---

## 🎯 Implementation Priority

### Phase 1: Critical Fixes (Immediate)
Update tasks that are **definitely truncating**:

1. ✅ `synthesize_fused_dossier`: 2500 → 16384
2. ✅ `generate_final_strategy`: 2000 → 16384  
3. ✅ `forge_specialist_agent`: 2500 → 16384

**Impact**: Eliminate truncation on most important outputs

---

### Phase 2: Analytical Expansion (Week 1)
Update all analytical tasks:

1. ✅ `deconstruct_problem`: 2000 → 8192
2. ✅ All `pathway_*_insight`: 1500 → 8192
3. ✅ `red_team_analysis`: 1500 → 8192
4. ✅ `ethical_and_bias_review`: 1500 → 8192

**Impact**: Allow thorough analysis without artificial constraints

---

### Phase 3: Optimization (Week 2)
Right-size the simple tasks:

1. ✅ `extract_domain`: 100 → 500 (reasonable headroom)
2. ✅ `validate_*`: Set to 1500 consistently
3. ✅ Add token usage monitoring to ThoughtTrail

**Impact**: Clean, consistent configuration

---

## 📏 Token Limit Reference Guide

| Task Complexity | Token Limit | Word Count | Use Case |
|----------------|-------------|------------|----------|
| **Micro** | 250 | ~180 | Single value extraction |
| **Small** | 500 | ~375 | Simple JSON extraction |
| **Medium** | 1500 | ~1100 | Validation reports |
| **Large** | 4096 | ~3000 | Detailed analysis |
| **X-Large** | 8192 | ~6000 | Comprehensive analysis |
| **XX-Large** | 16384 | ~12000 | Strategic documents |
| **XXX-Large** | 32768 | ~24000 | Full business plans |

---

## 🚀 Rollout Commands

```bash
# Test with expanded limits
cd /media/newbu/3626C55326C514B1/Happier
source arche_env/bin/activate

# Run Project Janus with optimized token limits
python arche_cli.py "$(cat updated_keyholder_query.txt)" --model gemini-2.5-flash

# Monitor token usage in ThoughtTrail
tail -f thought_trail.jsonl | grep "token_count"
```

---

## ✅ Summary: Your Optimization Thinking is CORRECT

**Your Principle**: 
> "If the tier limit is 2500 (or 65K), we want max_tokens to match the tier capability"

**Refined Principle**:
> "Set max_tokens based on **task complexity needs**, not arbitrary conservative limits. Don't artificially truncate high-value outputs to save pennies."

**Key Insight**:
- All models support 65K tokens
- We pay per token **used**, not per token **allowed**
- Current limits (1500-2500) were probably set for expensive models
- **Strategic outputs should use 8K-16K limits** for quality
- **Simple tasks should use 500-1500 limits** for speed
- **The cost of truncating a strategic plan >> the cost of 10K extra tokens**

---

**Next Action**: Update workflow JSON files with optimized token limits.

**Expected Impact**:
- ✅ Eliminate truncation on strategic outputs
- ✅ More comprehensive analysis
- ✅ Better quality responses  
- ⚠️ Slightly higher costs (~2-3x on large outputs)
- ✅ Massively higher value (complete vs truncated)

**ROI**: If one truncated strategy causes a $1000 business mistake, but 10K extra tokens costs $0.003, the ROI is **333,000:1** 🚀

