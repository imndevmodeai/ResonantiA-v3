#!/usr/bin/env python3
"""
Compress specification + code WITH SPR definitions in Zepto form as context
This should improve decompression fidelity by providing semantic anchors
"""

import sys
import json
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
        return None
    
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

def extract_spr_definitions(spr_file):
    """Extract relevant SPR definitions from the SPR file."""
    try:
        with open(spr_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract SPRs mentioned in the specification
        relevant_sprs = [
            'HistoricalContextualizatioN',
            'TemporalDynamiX',
            'FutureStateAnalysiS',
            'CausalLagDetectioN',
            'EmergenceOverTimE',
            'TrajectoryComparisoN',
            'CognitiveresonancE',
            'FourdthinkinG',
            'CognitiveResonancE',  # Alternative spelling
            'FourDThinking'  # Alternative spelling
        ]
        
        spr_definitions = {}
        
        # Handle both list and dict formats
        if isinstance(data, list):
            # Convert list to dict by spr_id
            data_dict = {}
            for item in data:
                if isinstance(item, dict) and 'spr_id' in item:
                    data_dict[item['spr_id']] = item
            data = data_dict
        
        if isinstance(data, dict):
            for spr_id in relevant_sprs:
                # Direct match
                if spr_id in data:
                    spr_definitions[spr_id] = data[spr_id]
                    continue
                
                # Case-insensitive search
                for key in data.keys():
                    if spr_id.lower() == key.lower():
                        spr_definitions[spr_id] = data[key]
                        break
                    # Partial match (e.g., "TemporalDynamiX" matches "TemporalDynamiX" or "TemporalDynamics")
                    if spr_id.lower().replace('x', '').replace('n', '') in key.lower().replace('x', '').replace('n', ''):
                        spr_definitions[spr_id] = data[key]
                        break
        
        return spr_definitions
    except Exception as e:
        print(f"Warning: Could not load SPR definitions: {e}")
        return {}

def compress_spr_definitions(spr_definitions):
    """Compress SPR definitions to Zepto form."""
    spr_zepto_context = {}
    
    for spr_id, spr_data in spr_definitions.items():
        # Convert SPR definition to text
        spr_text = f"SPR: {spr_id}\n"
        if isinstance(spr_data, dict):
            spr_text += f"Name: {spr_data.get('name', spr_id)}\n"
            spr_text += f"Definition: {spr_data.get('definition', spr_data.get('description', ''))}\n"
            spr_text += f"Context: {spr_data.get('context', '')}\n"
            spr_text += f"Keywords: {', '.join(spr_data.get('keywords', []))}\n"
            spr_text += f"Usage: {spr_data.get('usage', '')}\n"
        else:
            spr_text += str(spr_data)
        
        # Compress to Zepto
        result = compress_to_zepto(spr_text, target_stage="Zepto")
        if not result.error:
            spr_zepto_context[spr_id] = {
                'zepto_spr': result.zepto_spr,
                'compression_ratio': result.compression_ratio,
                'original_size': result.original_length,
                'compressed_size': result.zepto_length
            }
    
    return spr_zepto_context

def main():
    print("\n" + "=" * 80)
    print("  COMPRESSING SPECIFICATION + CODE WITH SPR CONTEXT (ZEPTO FORM)")
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
        print(f"❌ Could not extract CrystallizedObjectiveGenerator")
        return 1
    
    # Load and compress SPR definitions
    print("\n📚 Loading and compressing SPR definitions...")
    spr_file = "knowledge_graph/spr_definitions_tv.json"
    spr_definitions = extract_spr_definitions(spr_file)
    
    print(f"   Found {len(spr_definitions)} relevant SPR definitions")
    
    spr_zepto_context = compress_spr_definitions(spr_definitions)
    print(f"   Compressed {len(spr_zepto_context)} SPRs to Zepto form")
    
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
    
    # Save results
    output = {
        "zepto_spr": result.zepto_spr,
        "original_size": result.original_length,
        "compressed_size": result.zepto_length,
        "compression_ratio": result.compression_ratio,
        "codex_entries": result.new_codex_entries,
        "spec_size": len(spec_content),
        "code_size": len(code_class),
        "spr_context_zepto": spr_zepto_context,
        "spr_context_summary": {
            "total_sprs": len(spr_zepto_context),
            "total_compressed_size": sum(s['compressed_size'] for s in spr_zepto_context.values()),
            "total_original_size": sum(s['original_size'] for s in spr_zepto_context.values())
        }
    }
    
    with open("zepto_with_spr_context.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: zepto_with_spr_context.json")
    print(f"\n📊 ZEPTO SPR:")
    print(f"   {result.zepto_spr}")
    
    # Generate enhanced prompt with SPR context
    spr_context_text = "\n\n## SPR Definitions (Zepto Compressed Context)\n\n"
    spr_context_text += "The following SPR definitions are provided in Zepto form to provide semantic context:\n\n"
    
    for spr_id, spr_info in spr_zepto_context.items():
        spr_context_text += f"**{spr_id}**:\n"
        spr_context_text += f"  Zepto SPR: `{spr_info['zepto_spr']}`\n"
        spr_context_text += f"  Compression: {spr_info['original_size']} → {spr_info['compressed_size']} chars ({spr_info['compression_ratio']:.1f}:1)\n\n"
    
    codex_str = json.dumps(result.new_codex_entries, indent=2)[:2000] if result.new_codex_entries else "{}"
    
    prompt = f"""You are an expert at deciphering compressed symbolic representations, technical documentation, and Python code.

I have a Zepto SPR (Sparse Priming Representation) - a hyper-compressed symbolic form of a technical specification document WITH its complete Python implementation code.
Your task is to decompress and decipher it, reconstructing BOTH the specification AND the complete Python code.

Zepto SPR (compressed specification + code):
{result.zepto_spr}

Symbol Codex Entries (for reference):
{codex_str}
{spr_context_text}

Original content was approximately {result.original_length:,} characters (specification: {len(spec_content):,} chars + code: {len(code_class):,} chars).

CRITICAL: The SPR definitions above are provided in Zepto form. You should decompress them first to understand what each SPR means, then use that context to better understand the specification and code.

Instructions:
1. First, decompress the SPR definitions in Zepto form to understand their meanings
2. Analyze the main Zepto SPR structure and symbols carefully
3. Decompress it back to readable, comprehensive text
4. Reconstruct the COMPLETE Python implementation code for the CrystallizedObjectiveGenerator class
5. Use the SPR definitions as semantic anchors to understand the domain and purpose
6. Explain what the original specification was about
7. Identify key concepts, architecture, components, stages, and technical details
8. Reconstruct the specification structure (sections, parts, stages, etc.)
9. Identify the 8-stage crystallization process
10. Extract ALL code examples, method implementations, and class structures
11. Provide a detailed summary of the decompressed content

CRITICAL: You must reconstruct the COMPLETE Python class implementation including:
- All method signatures
- All method implementations
- All data structures (FeatureVector, TemporalScope, ActivatedSPR, Mandate, etc.)
- All helper methods (_extract_features, _build_temporal_scope, _activate_sprs, etc.)
- All static data loading methods
- Complete class structure with proper indentation
- Use the SPR definitions to understand what SPRs like HistoricalContextualizatioN, TemporalDynamiX, etc. actually mean

Format your response as:
## Decompressed SPR Definitions
[Decompress each SPR from Zepto form and explain what it means]

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
    with open("zepto_with_spr_context_prompt.txt", "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("ZEPTO SPR (Specification + Code) WITH SPR CONTEXT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Zepto SPR: {result.zepto_spr}\n\n")
        f.write(f"Original Size: {result.original_length:,} characters\n")
        f.write(f"Compressed Size: {result.zepto_length:,} characters\n")
        f.write(f"Compression Ratio: {result.compression_ratio:.2f}:1\n\n")
        f.write(f"SPR Context: {len(spr_zepto_context)} SPRs in Zepto form\n")
        f.write(f"SPR Context Size: {sum(s['compressed_size'] for s in spr_zepto_context.values()):,} chars\n\n")
        f.write("=" * 80 + "\n")
        f.write("LLM DECOMPRESSION PROMPT (WITH SPR CONTEXT)\n")
        f.write("=" * 80 + "\n\n")
        f.write(prompt)
    
    print(f"\n✅ Enhanced prompt with SPR context saved to: zepto_with_spr_context_prompt.txt")
    print(f"\n📊 SPR Context Summary:")
    print(f"   SPRs in Zepto form: {len(spr_zepto_context)}")
    if spr_zepto_context:
        print(f"   Total SPR context size: {sum(s['compressed_size'] for s in spr_zepto_context.values()):,} chars")
        print(f"   Average SPR compression: {sum(s['compression_ratio'] for s in spr_zepto_context.values()) / len(spr_zepto_context):.1f}:1")
    else:
        print(f"   ⚠️  No SPR definitions found - using specification text as context instead")
    
    return 0

if __name__ == "__main__":
    exit(main())

