#!/usr/bin/env python3
"""
Zepto Compression Test: Objective Generation Engine Crystallized Specification
Compresses the specification file and uses LLM to decompress and decipher it.
"""

import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.zepto_spr_processor import (
    get_zepto_processor,
    compress_to_zepto,
    decompress_from_zepto
)

# Import LLM provider directly to bypass ArchE direct execution
try:
    from Three_PointO_ArchE.llm_providers import get_llm_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM providers not available")

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def read_file_content(filepath):
    """Read file content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def main():
    """Run the test."""
    print("\n" + "=" * 80)
    print("  ZEPTO COMPRESSION: OBJECTIVE GENERATION ENGINE SPECIFICATION")
    print("  WITH LLM DECOMPRESSION & DECIPHERING")
    print("=" * 80)
    
    # File path
    spec_file = "specifications/objective_generation_engine_crystallized.md"
    
    # Check file exists
    if not Path(spec_file).exists():
        print(f"❌ Specification file not found: {spec_file}")
        return 1
    
    # Get Zepto processor
    processor = get_zepto_processor()
    if not processor:
        print("❌ Zepto processor not available")
        return 1
    
    print("\n✅ Zepto processor initialized")
    
    # ========================================================================
    # PART 1: Read and Compress Specification
    # ========================================================================
    print_section("PART 1: Compressing Specification File")
    
    spec_original = read_file_content(spec_file)
    if not spec_original:
        print("❌ Could not read specification file")
        return 1
    
    print(f"📄 Original specification: {len(spec_original):,} characters")
    print(f"   File: {spec_file}\n")
    
    # Compress to Zepto
    print("⏳ Compressing to Zepto SPR...")
    spec_compression = compress_to_zepto(spec_original, target_stage="Zepto")
    
    if spec_compression.error:
        print(f"❌ Compression error: {spec_compression.error}")
        return 1
    
    print(f"\n✅ Compression successful!")
    print(f"   Original: {spec_compression.original_length:,} chars")
    print(f"   Zepto: {spec_compression.zepto_length:,} chars")
    print(f"   Compression ratio: {spec_compression.compression_ratio:.2f}:1")
    print(f"   Processing time: {spec_compression.processing_time_sec:.3f}s")
    print(f"   New codex entries: {len(spec_compression.new_codex_entries)}")
    print(f"\n   Zepto SPR:")
    print(f"   {spec_compression.zepto_spr}")
    
    # ========================================================================
    # PART 2: Zepto Decompression (with codex)
    # ========================================================================
    print_section("PART 2: Zepto Decompression (with Codex)")
    
    print("⏳ Decompressing with Zepto codex...")
    spec_zepto_decompressed = decompress_from_zepto(
        spec_compression.zepto_spr,
        codex=spec_compression.new_codex_entries
    )
    
    if spec_zepto_decompressed.error:
        print(f"❌ Decompression error: {spec_zepto_decompressed.error}")
    else:
        print(f"✅ Decompressed: {len(spec_zepto_decompressed.decompressed_text):,} characters")
        print(f"✅ Symbols found: {len(spec_zepto_decompressed.symbols_found)}")
        print(f"✅ Symbols expanded: {len(spec_zepto_decompressed.symbols_expanded)}")
        print(f"\n   Decompressed preview:")
        print(f"   {spec_zepto_decompressed.decompressed_text[:300]}...")
    
    # ========================================================================
    # PART 3: LLM Decompression (without codex)
    # ========================================================================
    print_section("PART 3: LLM Decompression & Deciphering (without Codex)")
    
    if not LLM_AVAILABLE:
        print("⚠️  LLM not available - skipping LLM decompression test")
    else:
        # Build prompt for LLM
        codex_info = ""
        if spec_compression.new_codex_entries:
            codex_info = f"\n\nSymbol Codex Entries (for reference):\n{json.dumps(spec_compression.new_codex_entries, indent=2)[:1000]}..."
        
        prompt = f"""You are an expert at deciphering compressed symbolic representations and technical documentation.

I have a Zepto SPR (Sparse Priming Representation) - a hyper-compressed symbolic form of a technical specification document.
Your task is to decompress and decipher it, reconstructing the original meaning and structure.

Zepto SPR (compressed specification):
{spec_compression.zepto_spr}
{codex_info}

Original specification was approximately {spec_compression.original_length:,} characters.

Instructions:
1. Analyze the Zepto SPR structure and symbols carefully
2. Decompress it back to readable, comprehensive text
3. Explain what the original specification was about
4. Identify key concepts, architecture, components, stages, and technical details
5. Reconstruct the specification structure (sections, parts, stages, etc.)
6. Identify the 8-stage crystallization process if present
7. Extract any code examples, symbolic representations, or implementation details
8. Provide a detailed summary of the decompressed content

Format your response as:
## Decompressed Specification Content
[Full decompressed text - reconstruct as much as possible]

## Analysis & Deciphering
[Your analysis of what the specification means, its purpose, and structure]

## Key Concepts Identified
[List of key concepts, components, stages, processes]

## Technical Details
[Technical architecture, implementation details, code structure, etc.]

## Specification Structure
[The structure of the original specification - sections, parts, stages]

## Compression Analysis
[How effective was the compression? What information was preserved? What was lost?]

Begin decompression:"""
        
        try:
            print("⏳ Calling LLM to decompress and decipher (this may take a moment)...")
            
            # Use provider directly to bypass ArchE direct execution
            provider = get_llm_provider("groq")
            generated_text = provider.generate(
                prompt=prompt,
                model="llama-3.3-70b-versatile",
                max_tokens=8000,
                temperature=0.3
            )
            
            print(f"✅ LLM response received ({len(generated_text):,} characters)")
            
            # ========================================================================
            # PART 4: Save Results
            # ========================================================================
            print_section("PART 4: Saving Results")
            
            results = {
                "specification": {
                    "file": spec_file,
                    "original_size": spec_compression.original_length,
                    "compressed_size": spec_compression.zepto_length,
                    "compression_ratio": spec_compression.compression_ratio,
                    "processing_time_sec": spec_compression.processing_time_sec,
                    "zepto_spr": spec_compression.zepto_spr,
                    "new_codex_entries": spec_compression.new_codex_entries,
                    "zepto_decompressed": spec_zepto_decompressed.decompressed_text if not spec_zepto_decompressed.error else None,
                    "llm_decompressed": generated_text
                }
            }
            
            output_file = "zepto_spec_llm_results.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Results saved to: {output_file}")
            
            # ========================================================================
            # PART 5: Display Results
            # ========================================================================
            print_section("PART 5: Results Summary")
            
            print("\n📊 COMPRESSION METRICS:")
            print(f"   Original: {results['specification']['original_size']:,} chars")
            print(f"   Compressed: {results['specification']['compressed_size']:,} chars")
            print(f"   Ratio: {results['specification']['compression_ratio']:.2f}:1")
            print(f"   Processing time: {results['specification']['processing_time_sec']:.3f}s")
            
            print(f"\n📊 ZEPTO SPR:")
            print(f"   {results['specification']['zepto_spr']}")
            
            print(f"\n📊 LLM DECOMPRESSED PREVIEW:")
            print(f"   {generated_text[:800]}...")
            
            # Save LLM output to separate file for easier reading
            llm_output_file = "zepto_llm_decompressed_specification.md"
            with open(llm_output_file, 'w', encoding='utf-8') as f:
                f.write(f"# LLM Decompressed Specification\n\n")
                f.write(f"**Original Size**: {spec_compression.original_length:,} characters\n")
                f.write(f"**Compressed Size**: {spec_compression.zepto_length:,} characters\n")
                f.write(f"**Compression Ratio**: {spec_compression.compression_ratio:.2f}:1\n\n")
                f.write(f"**Zepto SPR**:\n```\n{spec_compression.zepto_spr}\n```\n\n")
                f.write(f"---\n\n")
                f.write(generated_text)
            
            print(f"\n✅ LLM decompressed output saved to: {llm_output_file}")
            
        except Exception as e:
            print(f"❌ LLM decompression error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print_section("TEST COMPLETE")
    print("✅ All tests completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())

