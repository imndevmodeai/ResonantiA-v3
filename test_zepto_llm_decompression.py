#!/usr/bin/env python3
"""
Zepto Compression + LLM Decompression Test

Tests Zepto compression on specification and code files, then uses an LLM
to decompress and decipher the compressed content without access to the codex.
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

# Import LLM tool for decompression
try:
    from Three_PointO_ArchE.llm_tool import generate_text_llm
    from Three_PointO_ArchE.llm_providers import get_llm_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM tools not available")

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

def compress_file(filepath, file_type="specification"):
    """Compress a file using Zepto."""
    print(f"\n📄 Compressing {file_type}: {filepath}")
    
    content = read_file_content(filepath)
    if not content:
        return None
    
    print(f"   Original size: {len(content):,} characters")
    
    # Compress to Zepto
    result = compress_to_zepto(content, target_stage="Zepto")
    
    if result.error:
        print(f"   ❌ Compression error: {result.error}")
        return None
    
    print(f"   ✅ Compressed size: {result.zepto_length:,} characters")
    print(f"   ✅ Compression ratio: {result.compression_ratio:.2f}:1")
    print(f"   ✅ Processing time: {result.processing_time_sec:.3f}s")
    print(f"   ✅ New codex entries: {len(result.new_codex_entries)}")
    
    return result

def llm_decompress_and_decipher(zepto_spr, codex_entries=None, file_type="content"):
    """Use LLM to decompress and decipher Zepto SPR without codex."""
    if not LLM_AVAILABLE:
        print("❌ LLM not available for decompression")
        return None
    
    print(f"\n🤖 LLM Decompression & Deciphering ({file_type})...")
    
    # Build prompt for LLM
    codex_info = ""
    if codex_entries:
        codex_info = f"\n\nSymbol Codex Entries (for reference):\n{json.dumps(codex_entries, indent=2)[:500]}..."
    
    prompt = f"""You are an expert at deciphering compressed symbolic representations.

I have a Zepto SPR (Sparse Priming Representation) - a hyper-compressed symbolic form of technical content.
Your task is to decompress and decipher it, reconstructing the original meaning.

Zepto SPR (compressed content):
{zepto_spr}
{codex_info}

Instructions:
1. Analyze the Zepto SPR structure and symbols
2. Decompress it back to readable, comprehensive text
3. Explain what the original content was about
4. Identify key concepts, architecture, and technical details
5. Provide a detailed summary of the decompressed content

Format your response as:
## Decompressed Content
[Full decompressed text]

## Analysis & Deciphering
[Your analysis of what the content means]

## Key Concepts Identified
[List of key concepts]

## Technical Details
[Technical architecture, components, etc.]

Begin decompression:"""
    
    try:
        # Use Groq for fast response
        provider = get_llm_provider("groq")
        if not provider:
            print("   ❌ Could not get LLM provider")
            return None
        
        print("   ⏳ Calling LLM (this may take a moment)...")
        
        response = generate_text_llm(
            inputs={
                "prompt": prompt,
                "provider": "groq",
                "model": "llama-3.3-70b-versatile",
                "max_tokens": 4000,
                "temperature": 0.3
            }
        )
        
        if isinstance(response, dict):
            generated_text = response.get('generated_text', response.get('text', str(response)))
        else:
            generated_text = str(response)
        
        print(f"   ✅ LLM response received ({len(generated_text):,} characters)")
        
        return generated_text
        
    except Exception as e:
        print(f"   ❌ LLM decompression error: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_decompressions(original, zepto_decompressed, llm_decompressed):
    """Compare Zepto decompression vs LLM decompression."""
    print_section("COMPARISON: Zepto vs LLM Decompression")
    
    print(f"\nOriginal content length: {len(original):,} characters")
    print(f"Zepto decompressed length: {len(zepto_decompressed) if zepto_decompressed else 0:,} characters")
    print(f"LLM decompressed length: {len(llm_decompressed) if llm_decompressed else 0:,} characters")
    
    # Simple similarity check (word overlap)
    if original and zepto_decompressed and llm_decompressed:
        original_words = set(original.lower().split())
        zepto_words = set(zepto_decompressed.lower().split())
        llm_words = set(llm_decompressed.lower().split())
        
        zepto_overlap = len(original_words & zepto_words) / len(original_words) if original_words else 0
        llm_overlap = len(original_words & llm_words) / len(original_words) if original_words else 0
        
        print(f"\nWord overlap with original:")
        print(f"  Zepto decompression: {zepto_overlap:.1%}")
        print(f"  LLM decompression: {llm_overlap:.1%}")

def main():
    """Run the complete test."""
    print("\n" + "=" * 80)
    print("  ZEPTO COMPRESSION + LLM DECOMPRESSION TEST")
    print("=" * 80)
    
    # File paths
    spec_file = "specifications/zepto_spr_processor_abstraction.md"
    code_file = "Three_PointO_ArchE/zepto_spr_processor.py"
    
    # Check files exist
    if not Path(spec_file).exists():
        print(f"❌ Specification file not found: {spec_file}")
        return 1
    
    if not Path(code_file).exists():
        print(f"❌ Code file not found: {code_file}")
        return 1
    
    # Get Zepto processor
    processor = get_zepto_processor()
    if not processor:
        print("❌ Zepto processor not available")
        return 1
    
    print("\n✅ Zepto processor initialized")
    
    # ========================================================================
    # PART 1: Compress Specification File
    # ========================================================================
    print_section("PART 1: Compressing Specification File")
    
    spec_original = read_file_content(spec_file)
    spec_compression = compress_file(spec_file, "specification")
    
    if not spec_compression:
        print("❌ Specification compression failed")
        return 1
    
    # ========================================================================
    # PART 2: Compress Code File
    # ========================================================================
    print_section("PART 2: Compressing Code File")
    
    code_original = read_file_content(code_file)
    code_compression = compress_file(code_file, "code")
    
    if not code_compression:
        print("❌ Code compression failed")
        return 1
    
    # ========================================================================
    # PART 3: Zepto Decompression (with codex)
    # ========================================================================
    print_section("PART 3: Zepto Decompression (with Codex)")
    
    print("\n📄 Decompressing specification...")
    spec_zepto_decompressed = decompress_from_zepto(
        spec_compression.zepto_spr,
        codex=spec_compression.new_codex_entries
    )
    
    if spec_zepto_decompressed.error:
        print(f"   ❌ Decompression error: {spec_zepto_decompressed.error}")
    else:
        print(f"   ✅ Decompressed: {len(spec_zepto_decompressed.decompressed_text):,} characters")
        print(f"   ✅ Symbols found: {len(spec_zepto_decompressed.symbols_found)}")
    
    print("\n📄 Decompressing code...")
    code_zepto_decompressed = decompress_from_zepto(
        code_compression.zepto_spr,
        codex=code_compression.new_codex_entries
    )
    
    if code_zepto_decompressed.error:
        print(f"   ❌ Decompression error: {code_zepto_decompressed.error}")
    else:
        print(f"   ✅ Decompressed: {len(code_zepto_decompressed.decompressed_text):,} characters")
        print(f"   ✅ Symbols found: {len(code_zepto_decompressed.symbols_found)}")
    
    # ========================================================================
    # PART 4: LLM Decompression (without codex)
    # ========================================================================
    print_section("PART 4: LLM Decompression & Deciphering (without Codex)")
    
    if not LLM_AVAILABLE:
        print("⚠️  LLM not available - skipping LLM decompression test")
    else:
        # LLM decompress specification
        spec_llm_decompressed = llm_decompress_and_decipher(
            spec_compression.zepto_spr,
            codex_entries=spec_compression.new_codex_entries,
            file_type="specification"
        )
        
        # LLM decompress code
        code_llm_decompressed = llm_decompress_and_decipher(
            code_compression.zepto_spr,
            codex_entries=code_compression.new_codex_entries,
            file_type="code"
        )
        
        # ========================================================================
        # PART 5: Save Results
        # ========================================================================
        print_section("PART 5: Saving Results")
        
        results = {
            "specification": {
                "original_size": len(spec_original),
                "compressed_size": spec_compression.zepto_length,
                "compression_ratio": spec_compression.compression_ratio,
                "zepto_spr": spec_compression.zepto_spr,
                "zepto_decompressed": spec_zepto_decompressed.decompressed_text if not spec_zepto_decompressed.error else None,
                "llm_decompressed": spec_llm_decompressed
            },
            "code": {
                "original_size": len(code_original),
                "compressed_size": code_compression.zepto_length,
                "compression_ratio": code_compression.compression_ratio,
                "zepto_spr": code_compression.zepto_spr,
                "zepto_decompressed": code_zepto_decompressed.decompressed_text if not code_zepto_decompressed.error else None,
                "llm_decompressed": code_llm_decompressed
            }
        }
        
        output_file = "zepto_llm_decompression_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")
        
        # ========================================================================
        # PART 6: Display Results
        # ========================================================================
        print_section("PART 6: Results Summary")
        
        print("\n📊 SPECIFICATION FILE:")
        print(f"   Original: {results['specification']['original_size']:,} chars")
        print(f"   Compressed: {results['specification']['compressed_size']:,} chars")
        print(f"   Ratio: {results['specification']['compression_ratio']:.2f}:1")
        print(f"   Zepto SPR: {results['specification']['zepto_spr'][:200]}...")
        
        if spec_llm_decompressed:
            print(f"\n   🤖 LLM Decompressed Preview:")
            print(f"   {spec_llm_decompressed[:500]}...")
        
        print("\n📊 CODE FILE:")
        print(f"   Original: {results['code']['original_size']:,} chars")
        print(f"   Compressed: {results['code']['compressed_size']:,} chars")
        print(f"   Ratio: {results['code']['compression_ratio']:.2f}:1")
        print(f"   Zepto SPR: {results['code']['zepto_spr'][:200]}...")
        
        if code_llm_decompressed:
            print(f"\n   🤖 LLM Decompressed Preview:")
            print(f"   {code_llm_decompressed[:500]}...")
        
        # Compare decompressions
        if spec_original and spec_zepto_decompressed and spec_llm_decompressed:
            compare_decompressions(
                spec_original,
                spec_zepto_decompressed.decompressed_text if not spec_zepto_decompressed.error else "",
                spec_llm_decompressed
            )
    
    print_section("TEST COMPLETE")
    print("✅ All tests completed successfully!")
    
    return 0

if __name__ == "__main__":
    exit(main())

