# Quick Start: ArchE vs LLM Comparison

## Run Your First Comparison

### 1. Single Query Test

```bash
cd /mnt/3626C55326C514B1/Happier
python ARCHE_LLM_COMPARISON_FRAMEWORK.py --query "How would you design a sustainable city for 10 million people?"
```

### 2. Batch Comparison (10 Novel Queries)

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py --queries-file test_queries.json --arche-method rise
```

### 3. Interactive Mode

```bash
python ARCHE_LLM_COMPARISON_FRAMEWORK.py
```

## What Gets Compared

### Direct LLM
- Simple prompt → LLM API → Response
- Fast, straightforward
- Single-pass reasoning

### ArchE RISE
- Query → Knowledge Scaffolding → Strategy Fusion → Vetting → Refinement
- Slower but deeper
- Multi-phase cognitive architecture
- CFP, ABM, Causal Inference integration

## Expected Results

**Direct LLM:**
- Time: ~1-3 seconds
- Response: Direct answer
- Depth: Single perspective

**ArchE RISE:**
- Time: ~5-15 seconds
- Response: Comprehensive strategic dossier
- Depth: Multi-perspective, validated, refined

## Output Location

Results saved to: `outputs/comparisons/`

Each comparison includes:
- Full responses from both methods
- Timing metrics
- Error information
- Response quality metrics

## Next Steps

1. Run batch comparison: `python ARCHE_LLM_COMPARISON_FRAMEWORK.py --queries-file test_queries.json`
2. Review results in `outputs/comparisons/`
3. Analyze patterns:
   - When is ArchE's extra processing worth it?
   - What types of queries benefit most from ArchE?
   - What are the time/quality trade-offs?

## Requirements

- `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable set
- ArchE system initialized
- All dependencies installed

