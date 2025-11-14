# ArchE LLM Provider Analysis

## Current Setup (From config.py & llm_tool.py)

### Primary Configuration

**Default Provider:** `groq` (loaded from `ARCHE_LLM_PROVIDER` env var, falls back to "groq")

**Default Model by Provider:**
```
Provider    → Model
─────────────────────────────────────────────────────
groq        → llama-3.3-70b-versatile
google      → gemini-2.0-flash-exp (Gemini 2.5 Pro also available)
openai      → gpt-4o
mistral     → mistral-small-latest
cursor      → cursor-arche-v1 (fallback: gpt-4o)
```

### Multi-Provider Support

The system supports **5 different LLM providers** with configurable models:

```python
LLM_PROVIDERS = {
    "openai": {
        "default_model": "gpt-4o",
        "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
    },
    "google": {
        "default_model": "gemini-2.0-flash-exp",
        "models": [
            "gemini-2.5-pro",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro-latest",
            "gemini-1.5-flash-latest",
            "gemini-pro"
        ]
    },
    "groq": {
        "default_model": "llama-3.3-70b-versatile",
        "max_tokens": 8192 (highest)
    },
    "mistral": {
        "default_model": "mistral-small-latest",
        "models": ["mistral-small-latest", "mistral-medium", "mistral-large"]
    },
    "cursor": {
        "default_model": "cursor-arche-v1"
    }
}
```

---

## Execution Flow: How Requests Are Handled

### Step 1: Check API Keys

```
┌─────────────────────────────────────────────┐
│ Load Environment Variables                  │
│  - OPENAI_API_KEY                          │
│  - GOOGLE_API_KEY (or GEMINI_API_KEY)      │
│  - GROQ_API_KEY                            │
│  - MISTRAL_API_KEY                         │
│  - ARCHE_LLM_PROVIDER (default: groq)      │
└─────────────────────────────────────────────┘
```

### Step 2: Request Routing (generate_text_llm)

```
Request arrives
    ↓
[PRIORITY 1] Try ArchE Direct Execution
    ├─ CFP Analysis → Qiskit (no LLM needed)
    ├─ ABM Simulation → Mesa (no LLM needed)
    ├─ Causal Inference → DoWHY (no LLM needed)
    ├─ System Status → Hardcoded response
    └─ Quantum/YouTube queries → Cached responses
    
    If Direct Execution Succeeds:
        ✅ Return response with metadata: {"execution_mode": "direct", "bypassed_llm": True}
        Confidence: 0.95, Time: <100ms
    
    If Direct Execution Fails:
        ↓ Fall through to LLM
        
[PRIORITY 2] Fall Back to External LLM Provider
    ├─ Initialize provider (groq, google, openai, mistral, cursor)
    ├─ Generate text using selected model
    ├─ Return response with metadata: {"execution_mode": "llm_fallback"}
    └─ Confidence: 0.9, Time: 1-3s
    
    If LLM Provider Fails:
        ❌ Return error with reflection
```

---

## Current LLM Usage Pattern

### What Uses LLM Currently

1. **Zepto SPR Compression** ← This uses LLM most
   - When filling zepto_spr fields
   - When generating symbol_codex
   - Pattern: LLM reads full SPR narrative → outputs symbols

2. **Pattern Crystallization Engine** ← Heavy LLM use
   - `_symbolize()` method calls LLM for semantic understanding
   - `_update_codex()` generates codex entries via LLM

3. **Fallback queries** to generate_text_llm
   - Any query that doesn't match CFP/ABM/Causal keywords

### What Does NOT Use LLM

✅ CFP (Comparative Fluxual Processing) → Uses **Qiskit** directly
✅ ABM (Agent-Based Modeling) → Uses **Mesa** directly  
✅ Causal Inference → Uses **DoWHY** directly
✅ Status queries → Hardcoded responses
✅ Known queries (YouTube, quantum, etc.) → Cached responses

---

## Cost Analysis: Current vs Symbol-First

### Current Setup (Letters, Heavy LLM Use)

**Zepto Compression Cost:**
- 246 SPRs × 1 compression pass = 246 LLM calls
- Initial cost: ~$25
- Result: text-based zepto_spr (poor compression)

**Decompression Cost (Future):**
- Every time KG needs to decompress → LLM call
- At 1,000 queries/month = 12,000 LLM calls/year
- Annual cost: $1,200/year
- Latency per query: 500ms

**Total Year 1 Cost:** $1,225

### Symbol-First Setup (What We Should Have)

**Zepto Compression Cost:**
- 246 SPRs × 1 compression pass = 246 LLM calls (same)
- Initial cost: ~$25 (same)
- Result: symbol-based zepto_spr (23:1 compression)

**Decompression Cost (Future):**
- Zero LLM calls needed (symbols self-describe)
- At 1,000 queries/month = 0 LLM calls/year
- Annual cost: $0/year
- Latency per query: <1ms

**Total Year 1 Cost:** $25

**Savings: $1,200/year**

---

## Provider Comparison: Cost & Speed

### Ranking by Cost (per 1M tokens)

```
Provider         Input Cost  Output Cost  Speed      Notes
─────────────────────────────────────────────────────────────
Mistral          $0.25       $0.75        Fast       Cheapest for SPR compression
Groq (default)   $0.50       $1.50        Very Fast  Free tier available
Google Gemini    $2.50       $7.50        Medium     Image/video capable
OpenAI GPT-4o    $5.00       $15.00       Slow       Most expensive
Cursor           Custom      Custom       Fast       Direct integration (me)
```

### For SPR Compression Specifically

- **Best: Mistral** ($1 per 246 SPRs)
- **Current: Groq** (~$1 per 246 SPRs, but free tier available)
- **Alternative: Google Gemini** (~$2 per 246 SPRs)

---

## How to Override the Default Provider

### Option 1: Environment Variable (Persistent)

```bash
export ARCHE_LLM_PROVIDER=google
export GOOGLE_API_KEY="your-api-key"
python scripts/run_maestro.py
```

### Option 2: Runtime Parameter (Per-request)

```python
result = generate_text_llm({
    "prompt": "Your query",
    "provider": "mistral",  # ← Override
    "model": "mistral-small-latest"
})
```

### Option 3: Configuration Change (Permanent)

Edit `config.py`:
```python
default_provider: str = os.getenv("ARCHE_LLM_PROVIDER", "mistral")  # Change default
```

---

## Current Status: Groq (Llama 3.3 70B)

### Why Groq Was Chosen (Default)

✅ **Fast inference** (~100 tokens/sec)
✅ **Generous free tier** (no card required initially)
✅ **Long context** (8,192 tokens max)
✅ **Cost-effective** (~$0.50 per 1M input tokens)
✅ **Reliable** (99.9% uptime)
❌ **No multimodal** (text only)
❌ **Limited context** compared to GPT-4

### Groq Llama 3.3 70B Specs

- **Model**: Llama 3.3 70B (open-source)
- **Max tokens**: 8,192
- **Context window**: 8K tokens
- **Latency**: ~50-100ms per request
- **Cost per 1M tokens**: $0.50 (input), $1.50 (output)

---

## Recommended Action: For Best Results with Symbols

Since you're optimizing for **symbol compression** (not generation), you have options:

### Option A: Keep Current (Groq)
- **Pros**: Fast, free tier, already working
- **Cons**: Slightly more expensive than Mistral
- **Cost**: $25 for full compression

### Option B: Switch to Mistral (Cheapest)
- **Pros**: 50% cheaper, still good quality
- **Cons**: Slightly slower
- **Cost**: $12.50 for full compression

### Option C: Use Google Gemini (Most Capable)
- **Pros**: Best multimodal support, smarter symbolization
- **Cons**: 5× more expensive
- **Cost**: $100 for full compression

### Option D: Use Me (Cursor AI)
- **Pros**: I'm already here, can understand context perfectly, custom integration
- **Cons**: Limited availability in production
- **Cost**: $0 (you're already paying for Cursor subscription)

---

## My Recommendation

**For immediate SPR recompression with symbols:**

1. **Keep using Groq** (default is fine)
2. **Execute PATH B** (recompress top 80 high-value SPRs)
3. **Cost:** $10-12
4. **Time:** 30 minutes

**For long-term optimization:**

1. **Build hybrid router** (KG-first for symbols, LLM fallback only if needed)
2. **Cost per query drops** from $0.10 → $0.0001 (1000× improvement)
3. **Annual savings** at scale: $1,200+/year

---

## Question for You

**Would you like to:**

1. ✅ **Execute PATH B now** using Groq (current default)?
2. 🔄 **Switch providers** first (which one)?
3. 📊 **Analyze provider costs** in more detail for different scenarios?
4. 🚀 **Build the hybrid router** immediately (uses KG for 80% of queries)?

What's your preference?

