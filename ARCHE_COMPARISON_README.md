# ArchE vs LLM Comparison Framework

## Purpose

This framework runs novel queries through ArchE's best cognitive flows and directly compares the results with standard LLM calls. This enables quantitative and qualitative analysis of ArchE's cognitive architecture advantages.

## Features

- **Direct LLM Comparison**: Runs queries through standard LLM API calls
- **ArchE RISE Comparison**: Runs queries through ArchE's full RISE orchestrator (4-phase cognitive architecture)
- **ArchE Workflow Comparison**: Runs queries through specific workflows (knowledge scaffolding, strategy fusion, etc.)
- **Comprehensive Metrics**: Time, response quality, error rates, response length
- **Batch Processing**: Run multiple queries and generate summary statistics

## Usage

### Single Query Comparison

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py --query "Your novel query here" --arche-method rise
```

### Batch Comparison

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py --queries-file test_queries.json --arche-method rise
```

### Specific Workflow Comparison

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py --query "Your query" --arche-method workflow:knowledge_scaffolding.json
```

### Interactive Mode

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py
```

## ArchE Methods

### RISE (Recommended)
Full 4-phase RISE orchestrator:
- Phase A: Knowledge Scaffolding
- Phase B: Strategy Fusion (CFP, ABM, Causal Inference)
- Phase C: High-Stakes Vetting
- Phase D: Utopian Refinement

```bash
--arche-method rise
```

### Specific Workflows
Run through individual workflows:
- `knowledge_scaffolding.json` - Domain knowledge acquisition
- `strategy_fusion.json` - Multi-perspective strategy synthesis
- `high_stakes_vetting.json` - Adversarial validation

```bash
--arche-method workflow:knowledge_scaffolding.json
```

## Output

Results are saved to `outputs/comparisons/` with:
- Individual comparison JSON files
- Batch summary files
- Full results including:
  - Direct LLM response
  - ArchE response
  - Timing metrics
  - Error information
  - Response length comparisons

## Sample Queries

The framework includes `test_queries.json` with 10 novel, complex queries designed to test:
- Multi-domain reasoning
- Ethical considerations
- Strategic planning
- Complex system analysis
- Long-term thinking

## Metrics Collected

1. **Performance Metrics**:
   - Execution time (ms)
   - Time ratio (ArchE / Direct LLM)
   - Response length

2. **Quality Metrics**:
   - Success/failure status
   - Error messages
   - Response completeness

3. **ArchE-Specific Metrics**:
   - Phases completed (for RISE)
   - Session ID
   - Workflow execution details

## Example Output

```json
{
  "comparison": {
    "query": "How would you design a sustainable city...",
    "direct_llm": {
      "status": "success",
      "time_ms": 1250.5,
      "response_length": 2847
    },
    "arche": {
      "status": "success",
      "time_ms": 8543.2,
      "response_length": 12456,
      "method": "arche_rise"
    },
    "metrics": {
      "time_difference_ms": 7292.7,
      "time_ratio": 6.84,
      "response_length_ratio": 4.37
    }
  }
}
```

## Requirements

- Python 3.8+
- ArchE system initialized
- GEMINI_API_KEY or GOOGLE_API_KEY environment variable
- All ArchE dependencies installed

## Analysis

After running comparisons, analyze:
1. **Time Trade-offs**: ArchE takes longer but provides deeper analysis
2. **Response Quality**: Compare depth, structure, and comprehensiveness
3. **Error Rates**: Which method is more reliable?
4. **Use Case Fit**: When is ArchE's extra processing worth it?

## Next Steps

1. Run batch comparisons with test queries
2. Analyze results for patterns
3. Identify ArchE's strengths (complex reasoning, multi-perspective analysis)
4. Identify areas for optimization (speed, efficiency)
5. Create visualizations of comparison metrics

