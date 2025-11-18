# ArchE Knowledge Graph CLI

## Overview

The `ask_kg_cli.py` tool allows you to query ArchE's internal Knowledge Graph directly, without making LLM API calls. It can also optionally compare KG answers with real-world understanding.

## Features

✅ **Zero LLM Calls (Default)**: All answers come from ArchE's internal Knowledge Graph  
✅ **Real-World Comparison (Optional)**: Use `--compare` flag to compare with LLM/web search  
✅ **Side-by-Side Analysis**: Highlights differences and similarities between KG and real-world answers  
✅ **Fast**: <1ms latency for KG queries  
✅ **Autonomous**: Uses compressed Zepto SPR knowledge from agi.txt

## Usage

### Basic Usage (No LLM Calls)

```bash
cd /mnt/3626C55326C514B1/Happier
source arche_env/bin/activate
python3 ask_kg_cli.py
```

Then ask questions like:
- "What is System Architecture?"
- "What is Machine Learning?"
- "What is Natural Language Processing?"

### With Real-World Comparison

```bash
python3 ask_kg_cli.py --compare
```

Or query directly:
```bash
python3 ask_kg_cli.py --compare "What is Machine Learning?"
```

## What It Answers

The CLI can answer questions about:
- **1,070 SPRs from agi.txt** (Mastermind_AI legacy knowledge)
- **2,519 SPRs from other sources** (ResonantiA Protocol, codebase, etc.)
- **Total: 3,589 SPRs** covering:
  - System Architecture
  - Machine Learning
  - Natural Language Processing
  - Cognitive Architecture
  - Security
  - Data Processing
  - And many more domains

## Comparison Feature

When using `--compare`:
1. **KG Answer**: Retrieved from internal Knowledge Graph (instant, zero cost)
2. **Real-World Answer**: Fetched via LLM (Gemini) or web search (fallback)
3. **Comparison Analysis**:
   - Similarity score (%)
   - Common concepts
   - KG-only concepts
   - Real-world-only concepts

## Example Output

### Without Comparison
```
📚 KNOWLEDGE GRAPH RESPONSE
Query: What is System Architecture?

✅ KG HIT: System Architecture (ArchitecturE)
   Confidence: 0.79
   Execution Time: 141.27ms
   Source: knowledge_graph (NO LLM CALL)

🔤 Zepto SPR: 'Σ|Α'

📖 Response:
System Architecture: Node 2: System Architecture
[From Codebase]: - Next.js (React 18, TS) client...
```

### With Comparison
```
📊 KNOWLEDGE COMPARISON: KG vs Real-World

🔵 KNOWLEDGE GRAPH ANSWER:
System Architecture: Node 2: System Architecture...

🌐 REAL-WORLD ANSWER:
System architecture refers to the fundamental structure...

📊 COMPARISON ANALYSIS:
   Similarity Score: 45.2%
   ✅ Common Concepts: architecture, system, design...
   🔵 KG-Only Concepts: node, agi.txt, codebase...
   🌐 Real-World-Only Concepts: components, patterns...
```

## Requirements

- Python 3.8+
- ArchE virtual environment activated
- Knowledge Graph file: `knowledge_graph/spr_definitions_tv.json`

For comparison feature:
- LLM API key (for LLM comparison) OR
- Web search tool configured (for web search fallback)

## Commands

- `help` - Show example queries
- `exit` or `quit` - Exit the CLI

## Notes

- **Default mode**: Zero LLM calls, pure KG queries
- **Comparison mode**: Only calls LLM/web search when `--compare` flag is used
- **KG answers**: Come from Zepto-compressed SPRs (100:1 to 1000:1 compression)
- **Autonomy**: As KG grows, more queries can be answered without LLM


