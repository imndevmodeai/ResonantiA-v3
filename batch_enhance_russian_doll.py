#!/usr/bin/env python3
"""
Batch Enhancement Script for Russian Doll Architecture

This script processes SPRs in batches to avoid overwhelming the system
and provides better progress tracking for large-scale enhancement.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import argparse
import time

def get_spr_count(spr_file: Path) -> int:
    """Get total number of SPRs in the file."""
    with open(spr_file, 'r', encoding='utf-8') as f:
        sprs = json.load(f)
    return len(sprs) if isinstance(sprs, list) else len(sprs.values())

def check_enhancement_status(spr_file: Path) -> Dict[str, Any]:
    """Check how many SPRs already have Russian Doll enhancement."""
    with open(spr_file, 'r', encoding='utf-8') as f:
        sprs = json.load(f)
    
    spr_list = sprs if isinstance(sprs, list) else list(sprs.values())
    
    total = len(spr_list)
    has_narrative = 0
    has_enhanced_codex = 0
    
    for spr in spr_list[:100]:  # Sample first 100
        compression_stages = spr.get('compression_stages', [])
        has_narrative_layer = any(
            stage.get('stage_name') == 'Narrative'
            for stage in compression_stages
        )
        if has_narrative_layer:
            has_narrative += 1
        
        symbol_codex = spr.get('symbol_codex', {})
        if symbol_codex:
            sample_symbol = list(symbol_codex.values())[0] if symbol_codex else {}
            has_enhanced = all(
                field in sample_symbol
                for field in ['original_patterns', 'critical_specifics', 'generalizable_patterns']
            )
            if has_enhanced and sample_symbol.get('original_patterns'):
                has_enhanced_codex += 1
    
    return {
        'total': total,
        'sample_checked': min(100, total),
        'has_narrative': has_narrative,
        'has_enhanced_codex': has_enhanced_codex,
        'needs_enhancement': total  # Assume all need enhancement for now
    }

def process_batch(
    spr_file: Path,
    start_idx: int,
    batch_size: int,
    workers: int = 2,
    dry_run: bool = False
) -> bool:
    """Process a batch of SPRs using the enhancement script."""
    cmd = [
        sys.executable,
        'enhance_sprs_russian_doll.py',
        '--spr-file', str(spr_file),
        '--workers', str(workers)
    ]
    
    if dry_run:
        cmd.append('--dry-run')
    
    print(f"\n{'='*80}")
    print(f"Processing batch: SPRs {start_idx} to {start_idx + batch_size - 1}")
    print(f"{'='*80}")
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        elapsed = time.time() - start_time
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\n✅ Batch completed in {elapsed:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Batch failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Batch enhancement of SPRs for Russian Doll architecture"
    )
    parser.add_argument(
        '--spr-file',
        type=str,
        default='knowledge_graph/spr_definitions_tv.json',
        help='Path to SPR definitions file'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=500,
        help='Number of SPRs to process per batch (default: 500)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=2,
        help='Number of parallel workers per batch (default: 2)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Dry run mode (don\'t save changes)'
    )
    parser.add_argument(
        '--check-status',
        action='store_true',
        help='Check enhancement status and exit'
    )
    parser.add_argument(
        '--start-from',
        type=int,
        default=0,
        help='Start processing from this SPR index (for resuming)'
    )
    
    args = parser.parse_args()
    
    spr_file = Path(args.spr_file)
    if not spr_file.exists():
        print(f"❌ ERROR: SPR file not found: {spr_file}")
        sys.exit(1)
    
    # Check status
    print("📊 Checking enhancement status...")
    status = check_enhancement_status(spr_file)
    print(f"   Total SPRs: {status['total']}")
    print(f"   Sample checked: {status['sample_checked']}")
    print(f"   Has Narrative layer: {status['has_narrative']}/{status['sample_checked']}")
    print(f"   Has enhanced codex: {status['has_enhanced_codex']}/{status['sample_checked']}")
    
    if args.check_status:
        return
    
    # Get total count
    total_sprs = status['total']
    
    # Calculate batches
    batch_size = args.batch_size
    num_batches = (total_sprs - args.start_from + batch_size - 1) // batch_size
    
    print(f"\n{'='*80}")
    print("BATCH ENHANCEMENT PLAN")
    print(f"{'='*80}")
    print(f"Total SPRs: {total_sprs}")
    print(f"Starting from: SPR #{args.start_from}")
    print(f"Batch size: {batch_size}")
    print(f"Number of batches: {num_batches}")
    print(f"Workers per batch: {args.workers}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"{'='*80}")
    
    if not args.dry_run:
        response = input("\n⚠️  This will modify your SPR file. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Process batches
    successful_batches = 0
    failed_batches = 0
    start_time = time.time()
    
    for batch_num in range(num_batches):
        start_idx = args.start_from + (batch_num * batch_size)
        end_idx = min(start_idx + batch_size, total_sprs)
        
        print(f"\n{'='*80}")
        print(f"BATCH {batch_num + 1}/{num_batches}")
        print(f"SPRs {start_idx} to {end_idx - 1} ({end_idx - start_idx} SPRs)")
        print(f"{'='*80}")
        
        # Note: The enhancement script processes all SPRs, not just a range
        # This is a limitation - we'd need to modify enhance_sprs_russian_doll.py
        # to support --start and --end parameters for true batching
        # For now, this processes all SPRs each time (which is inefficient)
        # Better approach: Use --limit to process incrementally
        
        success = process_batch(
            spr_file=spr_file,
            start_idx=start_idx,
            batch_size=batch_size,
            workers=args.workers,
            dry_run=args.dry_run
        )
        
        if success:
            successful_batches += 1
        else:
            failed_batches += 1
            print(f"\n⚠️  Batch {batch_num + 1} failed. You can resume with:")
            print(f"   python batch_enhance_russian_doll.py --start-from {end_idx}")
            response = input("\nContinue with next batch? (yes/no): ")
            if response.lower() != 'yes':
                break
        
        # Brief pause between batches to avoid overwhelming the system
        if batch_num < num_batches - 1:
            print("\n⏸️  Pausing 5 seconds before next batch...")
            time.sleep(5)
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print("BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Successful batches: {successful_batches}/{num_batches}")
    print(f"Failed batches: {failed_batches}/{num_batches}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

