#!/usr/bin/env python3
"""
Compress specification WITH code snippets to create comprehensive Zepto SPR
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.zepto_spr_processor import compress_to_zepto

def read_file_content(filepath):
    """Read file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def extract_class_code(filepath, class_name):
    """Extract a specific class from a Python file."""
    content = read_file_content(filepath)
    if not content:
        return None
    
    lines = content.split('\n')
    class_start = None
    class_end = None
    indent_level = None
    
    for i, line in enumerate(lines):
        if f"class {class_name}" in line:
            class_start = i
            indent_level = len(line) - len(line.lstrip())
            break
    
    if class_start is None:
        print(f"Class {class_name} not found in {filepath}")
        return None
    
    # Find the end of the class
    for i in range(class_start + 1, len(lines)):
        line = lines[i]
        if line.strip().startswith('class ') and len(line) - len(line.lstrip()) <= indent_level:
            class_end = i
            break
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if line.strip().startswith('def ') or line.strip().startswith('class '):
                class_end = i
                break
    
    if class_end is None:
        class_end = len(lines)
    
    return '\n'.join(lines[class_start:class_end])

def main():
    print("\n" + "=" * 80)
    print("  COMPRESSING SPECIFICATION + CODE TO ZEPTO SPR")
    print("=" * 80)
    
    # Read specification
    spec_file = "specifications/objective_generation_engine_crystallized.md"
    spec_content = read_file_content(spec_file)
    
    if not spec_content:
        print(f"❌ Could not read {spec_file}")
        return 1
    
    # Extract code
    code_file = "Three_PointO_ArchE/objective_generation_engine.py"
    code_class = extract_class_code(code_file, "CrystallizedObjectiveGenerator")
    
    if not code_class:
        print(f"❌ Could not extract CrystallizedObjectiveGenerator from {code_file}")
        return 1
    
    # Combine spec + code
    combined_content = f"""# Objective Generation Engine: Crystallized Implementation
## Specification + Implementation Code

{spec_content}

---

## Implementation Code: CrystallizedObjectiveGenerator

```python
{code_class}
```

---
END OF DOCUMENT
"""
    
    print(f"\n📄 Combined content:")
    print(f"   Specification: {len(spec_content):,} chars")
    print(f"   Code: {len(code_class):,} chars")
    print(f"   Total: {len(combined_content):,} chars")
    
    # Compress to Zepto
    print(f"\n⏳ Compressing to Zepto SPR...")
    result = compress_to_zepto(combined_content, target_stage="Zepto")
    
    if result.error:
        print(f"❌ Compression error: {result.error}")
        return 1
    
    print(f"\n✅ Compression successful!")
    print(f"   Original: {result.original_length:,} chars")
    print(f"   Zepto: {result.zepto_length:,} chars")
    print(f"   Compression ratio: {result.compression_ratio:.2f}:1")
    print(f"   Processing time: {result.processing_time_sec:.3f}s")
    print(f"   New codex entries: {len(result.new_codex_entries)}")
    
    # Save results
    import json
    output = {
        "zepto_spr": result.zepto_spr,
        "original_size": result.original_length,
        "compressed_size": result.zepto_length,
        "compression_ratio": result.compression_ratio,
        "codex_entries": result.new_codex_entries,
        "spec_size": len(spec_content),
        "code_size": len(code_class)
    }
    
    with open("zepto_spec_code_combined.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: zepto_spec_code_combined.json")
    print(f"\n📊 ZEPTO SPR:")
    print(f"   {result.zepto_spr}")
    
    # Generate prompt
    codex_str = json.dumps(result.new_codex_entries, indent=2)[:2000] if result.new_codex_entries else "{}"
    
    prompt = f"""You are an expert at deciphering compressed symbolic representations, technical documentation, and Python code.

I have a Zepto SPR (Sparse Priming Representation) - a hyper-compressed symbolic form of a technical specification document WITH its complete Python implementation code.
Your task is to decompress and decipher it, reconstructing BOTH the specification AND the complete Python code.

Zepto SPR (compressed specification + code):
{result.zepto_spr}

Symbol Codex Entries (for reference):
{codex_str}

Original content was approximately {result.original_length:,} characters (specification: {len(spec_content):,} chars + code: {len(code_class):,} chars).

Instructions:
1. Analyze the Zepto SPR structure and symbols carefully
2. Decompress it back to readable, comprehensive text
3. Reconstruct the COMPLETE Python implementation code for the CrystallizedObjectiveGenerator class
4. Explain what the original specification was about
5. Identify key concepts, architecture, components, stages, and technical details
6. Reconstruct the specification structure (sections, parts, stages, etc.)
7. Identify the 8-stage crystallization process
8. Extract ALL code examples, method implementations, and class structures
9. Provide a detailed summary of the decompressed content

CRITICAL: You must reconstruct the COMPLETE Python class implementation including:
- All method signatures
- All method implementations
- All data structures (FeatureVector, TemporalScope, ActivatedSPR, Mandate, etc.)
- All helper methods (_extract_features, _build_temporal_scope, _activate_sprs, etc.)
- All static data loading methods
- Complete class structure with proper indentation

Format your response as:
## Decompressed Specification Content
[Full decompressed specification text - reconstruct as much as possible]

## Complete Python Implementation Code
```python
# COMPLETE CrystallizedObjectiveGenerator class implementation
class CrystallizedObjectiveGenerator:
    # ... full implementation with all methods ...
```

## Analysis & Deciphering
[Your analysis of what the specification means, its purpose, and structure]

## Key Concepts Identified
[List of key concepts, components, stages, processes]

## Technical Details
[Technical architecture, implementation details, code structure, etc.]

## Specification Structure
[The structure of the original specification - sections, parts, stages]

## Code Structure Analysis
[Analysis of the Python implementation - classes, methods, data structures, etc.]

## Compression Analysis
[How effective was the compression? What information was preserved? What was lost?]

Begin decompression:"""
    
    # Save prompt
    with open("zepto_spec_code_prompt.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("ZEPTO SPR (Specification + Code)\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Zepto SPR: {result.zepto_spr}\n\n")
        f.write(f"Original Size: {result.original_length:,} characters\n")
        f.write(f"Compressed Size: {result.zepto_length:,} characters\n")
        f.write(f"Compression Ratio: {result.compression_ratio:.2f}:1\n\n")
        f.write("=" * 80 + "\n")
        f.write("LLM DECOMPRESSION PROMPT\n")
        f.write("=" * 80 + "\n\n")
        f.write(prompt)
    
    print(f"\n✅ Prompt saved to: zepto_spec_code_prompt.txt")
    
    return 0

if __name__ == "__main__":
    exit(main())


