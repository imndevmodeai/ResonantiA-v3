# Querying Documents with ask_kg_cli.py

## Overview

The `ask_kg_cli.py` tool now supports querying specific documents (like `PRIME_ARCHE_PROTOCOL.md`) alongside the Knowledge Graph. This allows you to ask questions about concepts in documents and get answers that combine KG knowledge with document content.

## Usage

### Basic Document Query

```bash
python3 ask_kg_cli.py --document PRIME_ARCHE_PROTOCOL.md "What are the 14 Mandates?"
```

### Interactive Mode with Document

```bash
python3 ask_kg_cli.py --document PRIME_ARCHE_PROTOCOL.md
```

Then ask questions like:
- "What is Cognitive Resonance?"
- "What are the 14 Mandates?"
- "What is the Resonant Corrective Loop?"
- "What is the Knowledge network onenesS?"

### Combined with Comparison

```bash
python3 ask_kg_cli.py --document PRIME_ARCHE_PROTOCOL.md --compare "What is Cognitive Resonance?"
```

## How It Works

1. **Document Loading**: The specified document is loaded and parsed into sections (by markdown headers)
2. **Section Extraction**: Relevant sections are identified based on query keywords
3. **KG Query**: Knowledge Graph is queried for matching SPRs
4. **Confidence Boosting**: SPRs that appear in document sections get confidence boosts
5. **Response Synthesis**: KG response is enhanced with relevant document sections

## Features

- **Document Parsing**: Automatically splits documents by markdown headers (`#`, `##`, `###`, etc.)
- **Relevance Scoring**: Sections are scored by keyword overlap with query
- **Hybrid Responses**: Combines KG knowledge with document excerpts
- **Fallback**: If no KG match, returns document-only response
- **No LLM Calls**: Pure deterministic document search

## Example Output

```
📄 Document loaded: PRIME_ARCHE_PROTOCOL.md (29,625 characters)
✅ Knowledge Graph loaded: 3,589 total SPRs
   • Document mode: Querying from PRIME_ARCHE_PROTOCOL.md

Query: What are the 14 Mandates?

📖 Response:
--------------------------------------------------------------------------------
[KG Response about Mandates]

📄 **From Document**:

**⚡ THE 14 CRITICAL MANDATES**
MANDATE 1: The Crucible (Live Validation)
Validate against reality, not mocks...

MANDATE 2: The Archeologist (Proactive Truth Resonance)
Build Hypothetical Answer Models...
--------------------------------------------------------------------------------
```

## Supported Documents

Any markdown (`.md`) or text file can be queried:
- `PRIME_ARCHE_PROTOCOL.md`
- `README.md`
- `protocol/ResonantiA_Protocol_v3.0.md`
- Any other markdown document

## Tips

1. **Specific Queries**: More specific queries (e.g., "14 Mandates") work better than generic ones
2. **Section Headers**: Documents are split by markdown headers, so queries matching section titles work best
3. **Combined Mode**: Use `--document` with `--compare` to see how document knowledge compares to real-world understanding

## Limitations

- Document parsing is markdown-header-based (works best with well-structured markdown)
- Relevance scoring is keyword-based (not semantic)
- Large documents may take longer to parse
- Document-only responses don't use NLG (raw document excerpts)


