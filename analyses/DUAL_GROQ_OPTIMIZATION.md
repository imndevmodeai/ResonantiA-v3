# Dual Groq Account Optimization Strategy

## Current Setup: 2 Groq API Keys

**Account 1:** Primary (GROQ_API_KEY)
**Account 2:** Secondary (available for load balancing)

---

## Cost Optimization with Dual Accounts

### Current Groq Pricing

Per account:
- **Free tier limit:** ~$200 total credits (if on free tier)
- **Cost:** $0.50 per 1M input tokens, $1.50 per 1M output tokens
- **Rate limit:** ~500 tokens/second per account

### Dual Account Strategy

```
Request arrives (52 recompressions needed)
    ↓
Split into 2 batches:
├─ Batch A: 26 SPRs → Account 1 (GROQ_API_KEY)
│           Cost: ~$3.12
│           Rate: 500 tokens/sec
│           Time: ~65 seconds
│
└─ Batch B: 26 SPRs → Account 2 (GROQ_API_KEY_2)
            Cost: ~$3.12
            Rate: 500 tokens/sec
            Time: ~65 seconds

Parallel execution: ~65 seconds (vs 130 seconds sequential)
Total cost: $6.24 (same)
Speed improvement: 2× faster (65s vs 130s)
```

---

## Implementation: Parallel Execution

### Option 1: Simple Sequential Execution (Current Plan)

```bash
# Execute all 52 on Account 1
python scripts/recompress_high_value_sprs.py
```

**Time:** ~2 minutes
**Cost:** $6.24 on Account 1
**Benefit:** Simple, low risk

### Option 2: Parallel Execution (Optimized) ← RECOMMENDED

Create two concurrent processes:

```bash
# Terminal 1: Recompress SPRs 1-26 on Account 1
GROQ_API_KEY="[Account1]" python scripts/recompress_high_value_sprs.py --batch 1 --of 2

# Terminal 2 (parallel): Recompress SPRs 27-52 on Account 2
GROQ_API_KEY="[Account2]" python scripts/recompress_high_value_sprs.py --batch 2 --of 2

# Merge results
python scripts/merge_recompression_results.py
```

**Time:** ~65 seconds (2× faster)
**Cost:** $3.12 per account (balanced load)
**Benefit:** Faster completion, balanced spending

### Option 3: Load Balancing with Failover

```python
# Automatically switch accounts if rate limit hit

if rate_limit_exceeded(account1):
    switch_to_account2()
    resume_recompression()
```

---

## Updated Script: Dual Account Support

I'll create an enhanced recompression script that supports:
1. Account selection
2. Batch splitting (1 of 2, 2 of 2)
3. Parallel-safe writes
4. Result merging

### Enhanced Command

```bash
# Quick test: 5 SPRs per account
python scripts/recompress_high_value_sprs.py \
  --batch 1 --of 2 \
  --groq-key $GROQ_API_KEY_1 \
  --dry-run

# Full execution: 26 SPRs each
python scripts/recompress_high_value_sprs.py \
  --batch 1 --of 2 \
  --groq-key $GROQ_API_KEY_1

# (Run in parallel with batch 2)
```

---

## Financial Impact with Dual Accounts

### Scenario A: Sequential on One Account

```
Approach:      Sequential (Account 1 only)
Time:          ~2.5 minutes
Cost:          $6.24 (all on Account 1)
Account 1:     $6.24 used
Account 2:     $0.00 used
Balance:       Unbalanced
Risk:          Medium (single point of failure)
```

### Scenario B: Parallel on Both Accounts ← OPTIMAL

```
Approach:      Parallel (split across accounts)
Time:          ~65 seconds (2× faster)
Cost:          $6.24 ($3.12 each account)
Account 1:     $3.12 used
Account 2:     $3.12 used
Balance:       Perfect
Risk:          Low (automatic failover possible)

Annual savings with parallel:
  - Process 12 batches/year = 12 × 65s = 780s = 13 minutes
  - vs Sequential: 12 × 150s = 1800s = 30 minutes
  - Productivity gain: 17 minutes/year
```

### Long-term Benefit: Rate Limit Headroom

When scaling beyond 52 SPRs:

```
Scenario 1: One Account (Future)
  - Need to recompress 246 SPRs
  - Rate limit: 500 tokens/sec
  - Time: ~13 minutes
  - Cost: $24
  - Risk: Hit rate limits during peak hours

Scenario 2: Two Accounts (Now)
  - Need to recompress 246 SPRs
  - Rate limit: 1000 tokens/sec (combined)
  - Time: ~6.5 minutes (2× faster)
  - Cost: $24
  - Risk: Low (distributed load)
```

---

## Implementation Plan: Dual-Account Execution

### Step 1: Verify Both Keys are Available

```bash
python << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

account1 = os.getenv("GROQ_API_KEY")
account2 = os.getenv("GROQ_API_KEY_2")

print("Groq Account Status:")
print(f"  Account 1 (GROQ_API_KEY):   {'✅ Available' if account1 else '❌ Missing'}")
print(f"  Account 2 (GROQ_API_KEY_2): {'✅ Available' if account2 else '❌ Missing'}")

if account1 and account2:
    print("\n✅ Dual-account execution is READY")
    print(f"  Account 1 prefix: {account1[:10]}...")
    print(f"  Account 2 prefix: {account2[:10]}...")
else:
    print("\n❌ Setup incomplete - need both keys")
EOF
```

### Step 2: Modify config.py to Support Second Key

Add to `Three_PointO_ArchE/config.py`:

```python
@dataclass
class GroqConfig:
    """Groq multi-account configuration."""
    primary_api_key: str = os.getenv("GROQ_API_KEY")
    secondary_api_key: str = os.getenv("GROQ_API_KEY_2")
    
    def get_key(self, account: int = 1) -> str:
        """Get API key for specified account (1 or 2)."""
        if account == 2:
            return self.secondary_api_key or self.primary_api_key
        return self.primary_api_key
```

### Step 3: Create Parallel Execution Script

```python
# scripts/recompress_parallel.py

def recompress_batch(batch_num, total_batches, groq_key=None):
    """Recompress a batch of SPRs using specified Groq account."""
    # Load high-value SPRs
    # Split into batches (1 of 2, 2 of 2)
    # Use specified groq_key for this batch
    # Save results with batch marker
    pass

# Usage:
import subprocess
import threading

# Start two parallel processes
p1 = subprocess.Popen([
    "python", "scripts/recompress_high_value_sprs.py",
    "--batch", "1", "--of", "2",
    "--groq-key", os.getenv("GROQ_API_KEY")
])

p2 = subprocess.Popen([
    "python", "scripts/recompress_high_value_sprs.py",
    "--batch", "2", "--of", "2",
    "--groq-key", os.getenv("GROQ_API_KEY_2")
])

# Wait for both
p1.wait()
p2.wait()

# Merge results
merge_results()
```

---

## Recommendation: Which Strategy to Use?

### For PATH B (Current): Use Sequential

**Why:**
- Simplicity (lower risk)
- Still under 3 minutes
- Cost savings already achieved ($624/year)
- Good enough for 52 SPRs

**Command:**
```bash
python scripts/recompress_high_value_sprs.py
```

### For Future Scaling (246 SPRs): Use Parallel

**Why:**
- Time critical (13 min vs 6.5 min)
- Perfect load balancing
- Rate limit safety
- Automatic failover capability

**Command:**
```bash
python scripts/recompress_parallel.py --all-sprs
```

---

## Cost Comparison Matrix

| Approach | SPRs | Time | Cost | Speed | Notes |
|----------|------|------|------|-------|-------|
| Sequential (Acc1) | 52 | 2.5m | $6.24 | 1x | Simple, current plan |
| Parallel (Both) | 52 | 65s | $6.24 | 2x | Optimal for small batch |
| Sequential (Acc1) | 246 | 13m | $24 | 1x | Rate limit risk |
| Parallel (Both) | 246 | 6.5m | $24 | 2x | Safe, optimal |

---

## Immediate Action Items

### Option A: Execute PATH B (Sequential, Now)
```bash
python scripts/recompress_high_value_sprs.py
```
- **Time:** 2.5 minutes
- **Cost:** $6.24
- **Benefit:** 52 high-value SPRs symbolized
- **Next:** Build KG-First Router

### Option B: Execute PATH B (Parallel, Fast)
```bash
# Requires creating parallel execution script first
python scripts/recompress_parallel.py --batch-size 26
```
- **Time:** ~65 seconds
- **Cost:** $6.24
- **Benefit:** 2× faster + load balanced
- **Next:** Build KG-First Router

### Option C: Prepare for Full Scaling
```bash
# Build all parallel infrastructure first
python scripts/setup_dual_groq_execution.py
# Then execute when ready
```
- **Time:** ~30 min setup
- **Benefit:** Ready for 246 SPRs anytime
- **Next:** Execute whenever needed

---

## My Recommendation

**Execute Option A NOW** (Sequential) because:

1. ✅ Simplest to execute (no new scripts needed)
2. ✅ Still only 2.5 minutes
3. ✅ $6.24 cost is minimal
4. ✅ Gets you to next phase (KG-First Router) faster
5. ✅ Can always parallelize later for 246-SPR scale

**Then prepare Option B** (Parallel infrastructure) for future scaling:

- When you need to recompress all 246 SPRs
- When you want to optimize rate limits
- When throughput becomes critical

---

## Decision Point

What's your preference?

1. **🚀 FAST:** Execute PATH B now (2.5m, sequential, $6.24)
2. **⚡ OPTIMAL:** Build parallel first (~30m), then execute (65s, parallel, $6.24)
3. **📊 ANALYZE:** Show cost/time breakdown for each approach
4. **🔧 PREPARE:** Setup dual-account infrastructure without executing yet

