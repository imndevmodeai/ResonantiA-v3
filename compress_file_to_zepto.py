#!/usr/bin/env python3
"""
Zepto File Compression Utility
Compresses any text file to Zepto SPR format with full metadata preservation.

Usage:
    python compress_file_to_zepto.py <input_file> [output_dir] [target_stage]

Examples:
    python compress_file_to_zepto.py document.txt
    python compress_file_to_zepto.py document.txt outputs Zepto
    python compress_file_to_zepto.py large_file.txt compressed/ Atto
"""

import json
import sys
import time
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.zepto_spr_processor import compress_to_zepto, decompress_from_zepto
    ZEPTO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Could not import Zepto compression module: {e}")
    print("   Attempting to use workflow method instead...")
    ZEPTO_AVAILABLE = False


def compress_file_workflow(input_path: str, output_dir: str = "outputs", target_stage: str = "Zepto"):
    """
    Compress file using workflow method (fallback if direct import fails).
    """
    from Three_PointO_ArchE.main import main as workflow_main
    
    # Read file
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create initial context
    initial_context = {
        "narrative": content,
        "target_stage": target_stage,
        "file_path": str(input_path)
    }
    
    # Execute workflow
    context_json = json.dumps(initial_context)
    workflow_main(
        workflow_name="workflows/zepto_spr_compression.json",
        initial_context=initial_context
    )


def compress_file_direct(input_path: str, output_dir: str = "outputs", target_stage: str = "Zepto"):
    """
    Compress a file to Zepto SPR format using direct function call.
    
    Args:
        input_path: Path to the file to compress
        output_dir: Directory to save compressed artifacts
        target_stage: Compression stage target (default: "Zepto")
    
    Returns:
        Dictionary with compression results and file paths
    """
    # Read input file
    input_file = Path(input_path)
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    print(f"📄 Reading file: {input_path}")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    print(f"   Original size: {original_size:,} characters")
    
    # Compress to Zepto
    print(f"\n⏳ Compressing to {target_stage} SPR...")
    start_time = time.time()
    result = compress_to_zepto(content, target_stage=target_stage)
    compression_time = time.time() - start_time
    
    if result.error:
        raise RuntimeError(f"Compression failed: {result.error}")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate output filenames
    base_name = input_file.stem
    timestamp = int(time.time())
    zepto_file = output_path / f"{base_name}_zepto_{timestamp}.txt"
    codex_file = output_path / f"{base_name}_codex_{timestamp}.json"
    stages_file = output_path / f"{base_name}_stages_{timestamp}.json"
    metadata_file = output_path / f"{base_name}_metadata_{timestamp}.json"
    
    # Save Zepto SPR
    print(f"\n💾 Saving compressed artifacts...")
    with open(zepto_file, 'w', encoding='utf-8') as f:
        f.write(result.zepto_spr)
    print(f"   ✓ Zepto SPR: {zepto_file}")
    
    # Save codex entries (CRITICAL for decompression)
    with open(codex_file, 'w', encoding='utf-8') as f:
        json.dump(result.new_codex_entries, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Codex: {codex_file}")
    
    # Save compression stages
    with open(stages_file, 'w', encoding='utf-8') as f:
        json.dump(result.compression_stages, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Stages: {stages_file}")
    
    # Save metadata
    metadata = {
        "original_file": str(input_path),
        "original_length": result.original_length,
        "zepto_length": result.zepto_length,
        "compression_ratio": result.compression_ratio,
        "target_stage": target_stage,
        "processing_time_sec": result.processing_time_sec,
        "compression_time_sec": compression_time,
        "stages_completed": len(result.compression_stages),
        "new_codex_entries_count": len(result.new_codex_entries),
        "zepto_file": str(zepto_file),
        "codex_file": str(codex_file),
        "stages_file": str(stages_file)
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    print(f"   ✓ Metadata: {metadata_file}")
    
    # Print summary
    print(f"\n✅ Compression Complete!")
    print(f"   Original: {result.original_length:,} chars")
    print(f"   Zepto: {result.zepto_length:,} chars")
    print(f"   Compression Ratio: {result.compression_ratio:.2f}:1")
    print(f"   Processing Time: {result.processing_time_sec:.3f}s")
    print(f"   New Symbols: {len(result.new_codex_entries)}")
    
    # Verify round-trip decompression
    print(f"\n🔄 Verifying decompression...")
    decomp_start = time.time()
    decomp_result = decompress_from_zepto(
        zepto_spr=result.zepto_spr,
        codex=result.new_codex_entries,
        compression_stages=result.compression_stages
    )
    decomp_time = time.time() - decomp_start
    
    if decomp_result.error:
        print(f"   ⚠️  Decompression warning: {decomp_result.error}")
    else:
        decompressed_size = len(decomp_result.decompressed_text)
        match = (decompressed_size == original_size)
        print(f"   Decompressed: {decompressed_size:,} chars")
        print(f"   Round-trip match: {'✓' if match else '✗'}")
        print(f"   Decompression time: {decomp_time:.3f}s")
        
        if not match:
            print(f"   ⚠️  Size mismatch: Original={original_size}, Decompressed={decompressed_size}")
    
    return {
        "zepto_file": str(zepto_file),
        "codex_file": str(codex_file),
        "stages_file": str(stages_file),
        "metadata_file": str(metadata_file),
        "compression_result": {
            "zepto_spr": result.zepto_spr,
            "compression_ratio": result.compression_ratio,
            "original_length": result.original_length,
            "zepto_length": result.zepto_length,
            "processing_time_sec": result.processing_time_sec
        },
        "decompression_result": {
            "decompressed_text": decomp_result.decompressed_text if not decomp_result.error else None,
            "error": decomp_result.error,
            "decompression_time_sec": decomp_time
        }
    }


def main():
    """Main entry point for the compression script."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nError: Input file path required.")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "outputs"
    target_stage = sys.argv[3] if len(sys.argv) > 3 else "Zepto"
    
    # Validate target stage
    valid_stages = ["Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto"]
    if target_stage not in valid_stages:
        print(f"⚠️  Warning: Invalid target_stage '{target_stage}'")
        print(f"   Valid stages: {', '.join(valid_stages)}")
        print(f"   Using 'Zepto' as default.")
        target_stage = "Zepto"
    
    try:
        if ZEPTO_AVAILABLE:
            result = compress_file_direct(input_file, output_dir, target_stage)
            print(f"\n🎉 All artifacts saved to: {output_dir}/")
            print(f"\n📋 Summary:")
            print(f"   Zepto SPR file: {result['zepto_file']}")
            print(f"   Codex file: {result['codex_file']}")
            print(f"   Stages file: {result['stages_file']}")
            print(f"   Metadata file: {result['metadata_file']}")
        else:
            print("Using workflow method...")
            compress_file_workflow(input_file, output_dir, target_stage)
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"\n❌ Compression Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

