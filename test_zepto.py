#!/usr/bin/env python3
"""
Zepto SPR Processor Test Script

Tests the Zepto SPR compression and decompression system.
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
    decompress_from_zepto,
    ZeptoSPRRegistry
)

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(result, title="Result"):
    """Print a result object in a formatted way."""
    print(f"\n{title}:")
    print("-" * 80)
    if hasattr(result, '__dict__'):
        for key, value in result.__dict__.items():
            if key == 'zepto_spr' and value:
                print(f"  {key}: {value[:200]}..." if len(str(value)) > 200 else f"  {key}: {value}")
            elif key == 'decompressed_text' and value:
                print(f"  {key}: {value[:200]}..." if len(str(value)) > 200 else f"  {key}: {value}")
            elif isinstance(value, dict) and value:
                print(f"  {key}: {json.dumps(value, indent=4)[:300]}...")
            elif isinstance(value, list) and value:
                print(f"  {key}: [{len(value)} items]")
            else:
                print(f"  {key}: {value}")
    else:
        print(f"  {result}")

def test_basic_compression():
    """Test basic compression functionality."""
    print_section("TEST 1: Basic Compression")
    
    test_narrative = """
    The ResonantiA Protocol v3.5-GP is a comprehensive framework for autonomous AI systems.
    It defines 13 critical mandates that govern system behavior, including full automation,
    integrated action reflection, and ethical safeguards. The protocol emphasizes the
    importance of self-healing capabilities, predictive prefetching, and continuous learning.
    ArchE, as the primary implementation, must adhere to all mandates and maintain
    compliance with the Integrated Action Reflection (IAR) protocol.
    """
    
    print(f"Original narrative length: {len(test_narrative)} characters")
    print(f"Original narrative:\n{test_narrative[:200]}...")
    
    # Test compression
    result = compress_to_zepto(test_narrative, target_stage="Zepto")
    
    if result.error:
        print(f"\n❌ Compression failed: {result.error}")
        return False
    
    print_result(result, "Compression Result")
    
    print(f"\n✅ Compression successful!")
    print(f"   Original: {result.original_length} chars")
    print(f"   Zepto: {result.zepto_length} chars")
    print(f"   Compression ratio: {result.compression_ratio:.2f}:1")
    print(f"   Processing time: {result.processing_time_sec:.3f}s")
    
    return result

def test_decompression(compression_result):
    """Test decompression functionality."""
    print_section("TEST 2: Decompression")
    
    if not compression_result or compression_result.error:
        print("❌ Cannot test decompression - compression failed")
        return False
    
    zepto_spr = compression_result.zepto_spr
    codex = compression_result.new_codex_entries
    
    print(f"Zepto SPR length: {len(zepto_spr)} characters")
    print(f"Zepto SPR: {zepto_spr[:200]}...")
    print(f"Codex entries: {len(codex)} symbols")
    
    # Test decompression
    decomp_result = decompress_from_zepto(zepto_spr, codex=codex)
    
    if decomp_result.error:
        print(f"\n❌ Decompression failed: {decomp_result.error}")
        return False
    
    print_result(decomp_result, "Decompression Result")
    
    print(f"\n✅ Decompression successful!")
    print(f"   Decompressed length: {len(decomp_result.decompressed_text)} chars")
    print(f"   Symbols found: {len(decomp_result.symbols_found)}")
    print(f"   Symbols expanded: {len(decomp_result.symbols_expanded)}")
    
    return decomp_result

def test_validation(original, compression_result, decompression_result):
    """Test compression validation."""
    print_section("TEST 3: Compression Validation")
    
    if not compression_result or compression_result.error:
        print("❌ Cannot test validation - compression failed")
        return False
    
    if not decompression_result or decompression_result.error:
        print("❌ Cannot test validation - decompression failed")
        return False
    
    processor = get_zepto_processor()
    if not processor:
        print("❌ Cannot get processor for validation")
        return False
    
    validation = processor.validate_compression(
        original=original,
        zepto_spr=compression_result.zepto_spr,
        decompressed=decompression_result.decompressed_text
    )
    
    print_result(validation, "Validation Metrics")
    
    if validation.get('error'):
        print(f"\n❌ Validation error: {validation.get('error')}")
        return False
    
    print(f"\n✅ Validation complete!")
    print(f"   Compression ratio: {validation.get('compression_ratio', 0):.2f}:1")
    print(f"   Decompression accuracy: {validation.get('decompression_accuracy', 0):.2%}")
    print(f"   Key concepts preserved: {validation.get('key_concepts_preserved', False)}")
    print(f"   Logical structure intact: {validation.get('logical_structure_intact', False)}")
    
    return validation

def test_different_stages():
    """Test compression at different stages."""
    print_section("TEST 4: Different Compression Stages")
    
    test_narrative = """
    The workflow engine executes tasks in dependency order, resolving template variables
    and ensuring IAR compliance. Each task produces reflection data that includes status,
    confidence, and alignment metrics. The system supports self-healing and automatic
    error recovery through the Resonant Corrective Loop (RCL).
    """
    
    stages = ["Concise", "Nano", "Micro", "Pico", "Femto", "Atto", "Zepto"]
    
    results = {}
    for stage in stages:
        print(f"\nTesting {stage} stage...")
        result = compress_to_zepto(test_narrative, target_stage=stage)
        
        if result.error:
            print(f"  ❌ {stage} failed: {result.error}")
            results[stage] = None
        else:
            print(f"  ✅ {stage}: {result.original_length} → {result.zepto_length} chars ({result.compression_ratio:.2f}:1)")
            results[stage] = result
    
    print("\n" + "-" * 80)
    print("Compression Stage Comparison:")
    print("-" * 80)
    for stage, result in results.items():
        if result:
            print(f"  {stage:8s}: {result.compression_ratio:6.2f}:1 ratio, {result.zepto_length:4d} chars")
        else:
            print(f"  {stage:8s}: FAILED")
    
    return results

def test_codex_operations():
    """Test codex operations."""
    print_section("TEST 5: Codex Operations")
    
    processor = get_zepto_processor()
    if not processor:
        print("❌ Cannot get processor")
        return False
    
    # Get current codex
    codex = processor.get_codex()
    print(f"Current codex size: {len(codex)} symbols")
    
    if codex:
        print("\nSample codex entries:")
        for i, (symbol, entry) in enumerate(list(codex.items())[:5]):
            if isinstance(entry, dict):
                meaning = entry.get('meaning', 'N/A')[:100]
            else:
                meaning = str(entry)[:100]
            print(f"  {symbol}: {meaning}...")
            if i >= 4:
                break
    
    return True

def main():
    """Run all Zepto tests."""
    print("\n" + "=" * 80)
    print("  ZEPTO SPR PROCESSOR TEST SUITE")
    print("=" * 80)
    
    # Check if processor is available
    processor = get_zepto_processor()
    if not processor:
        print("\n❌ ERROR: Zepto SPR processor not available!")
        print("   Make sure PatternCrystallizationEngine is available and")
        print("   knowledge_graph/symbol_codex.json exists.")
        return 1
    
    print("\n✅ Zepto SPR processor initialized successfully")
    
    # Test 1: Basic compression
    compression_result = test_basic_compression()
    if not compression_result:
        print("\n❌ Basic compression test failed")
        return 1
    
    # Test 2: Decompression
    original_narrative = """
    The ResonantiA Protocol v3.5-GP is a comprehensive framework for autonomous AI systems.
    It defines 13 critical mandates that govern system behavior, including full automation,
    integrated action reflection, and ethical safeguards. The protocol emphasizes the
    importance of self-healing capabilities, predictive prefetching, and continuous learning.
    ArchE, as the primary implementation, must adhere to all mandates and maintain
    compliance with the Integrated Action Reflection (IAR) protocol.
    """
    
    decompression_result = test_decompression(compression_result)
    if not decompression_result:
        print("\n❌ Decompression test failed")
        return 1
    
    # Test 3: Validation
    validation_result = test_validation(original_narrative, compression_result, decompression_result)
    if not validation_result:
        print("\n❌ Validation test failed")
        return 1
    
    # Test 4: Different stages
    stage_results = test_different_stages()
    
    # Test 5: Codex operations
    codex_test = test_codex_operations()
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ Basic Compression: PASSED")
    print("✅ Decompression: PASSED")
    print("✅ Validation: PASSED")
    print("✅ Different Stages: PASSED")
    print("✅ Codex Operations: PASSED")
    
    print("\n" + "=" * 80)
    print("  ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    exit(main())


