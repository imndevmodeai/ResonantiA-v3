# SPR Definitions TV - Zepto Compressed Format

This file contains the Zepto-compressed version of spr_definitions_tv.json.

## Compression Info
- Format: Zepto SPR (Sparse Priming Representation)
- Requires: spr_definitions_tv.codex.md for decompression
- Lossless: Yes (with codex)

## Zepto Data

```zepto
Φ|Æ|Α|Μ|Σ
```

## Usage

To decompress, use the codex file (spr_definitions_tv.codex.md) with a Zepto decompressor.

```python
from Three_PointO_ArchE.zepto_spr_processor import decompress_from_zepto
import json

# Load codex
with open('spr_definitions_tv.codex.md', 'r') as f:
    codex_content = f.read()
    # Extract codex JSON from markdown
    codex = json.loads(codex_content.split('```json')[1].split('```')[0])

# Decompress
result = decompress_from_zepto(zepto_spr, codex)
original_json = json.loads(result.decompressed_text)
```
