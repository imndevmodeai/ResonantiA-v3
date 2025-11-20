# SPR Definitions TV - Symbol Codex

This file contains the symbol codex required for lossless decompression of spr_definitions_tv.zepto.md.

## Codex Info
- Purpose: Decompression key for Zepto format
- Required: Yes (for lossless decompression)
- Format: JSON

## Codex Data

```json
{}
```

## Usage

This codex is required to decompress the Zepto file back to the original JSON format.

```python
from Three_PointO_ArchE.zepto_spr_processor import decompress_from_zepto
import json

# Load codex
with open('spr_definitions_tv.codex.md', 'r') as f:
    codex_content = f.read()
    codex = json.loads(codex_content.split('```json')[1].split('```')[0])

# Load Zepto
with open('spr_definitions_tv.zepto.md', 'r') as f:
    zepto_content = f.read()
    zepto_spr = zepto_content.split('```zepto')[1].split('```')[0].strip()

# Decompress
result = decompress_from_zepto(zepto_spr, codex)
original_json = json.loads(result.decompressed_text)
```
