#!/usr/bin/env python3
"""
Fix Pseudo-Compressed Zepto SPRs
Compresses SPRs that have pseudo-compressed (long text) Zepto SPRs into real Zepto format.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.zepto_spr_processor import ZeptoSPRProcessorAdapter


def is_pseudo_compressed(zepto_spr: str) -> bool:
    """Check if a Zepto SPR is pseudo-compressed (long text) rather than real compressed."""
    if not zepto_spr or not zepto_spr.strip() or zepto_spr == 'Ξ':
        return False
    
    # Real Zepto SPRs are short
    if len(zepto_spr) > 50:
        return True
    
    # Real Zepto SPRs contain symbolic characters
    zepto_symbols = ['|', 'Γ', 'Σ', 'Δ', 'Θ', 'Λ', 'Ξ', 'Π', 'Φ', 'Ψ', 'Ω', 
                    'Α', 'Β', 'Ε', 'Η', 'Ι', 'Κ', 'Μ', 'Ν', 'Ο', 'Ρ', 'Τ', 'Υ', 'Χ']
    has_symbols = any(symbol in zepto_spr for symbol in zepto_symbols)
    
    # If it's long and doesn't have symbols, it's pseudo-compressed
    if len(zepto_spr) > 20 and not has_symbols:
        return True
    
    return False


def _is_real_zepto_spr(zepto_spr: str) -> bool:
    """
    Check if a Zepto SPR is actually compressed (short, symbolic) 
    or just pseudo-compressed text (long, readable).
    """
    if not zepto_spr or not zepto_spr.strip() or zepto_spr == 'Ξ':
        return False
    
    if len(zepto_spr) > 50:
        return False
    
    zepto_symbols = ['|', 'Γ', 'Σ', 'Δ', 'Θ', 'Λ', 'Ξ', 'Π', 'Φ', 'Ψ', 'Ω', 
                    'Α', 'Β', 'Ε', 'Η', 'Ι', 'Κ', 'Μ', 'Ν', 'Ο', 'Ρ', 'Τ', 'Υ', 'Χ', 'Æ']
    has_symbols = any(symbol in zepto_spr for symbol in zepto_symbols)
    
    is_readable = ' ' in zepto_spr or (len([c for c in zepto_spr if c.isalpha() and c.islower()]) > len(zepto_spr) * 0.5)
    
    return has_symbols and not is_readable


def fix_zepto_sprs(spr_file: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Fix pseudo-compressed Zepto SPRs by compressing them properly.
    
    Args:
        spr_file: Path to SPR definitions file
        dry_run: If True, don't save changes, just report
        
    Returns:
        Dictionary with statistics about fixes
    """
    print(f"📚 Loading SPR definitions from {spr_file}...")
    
    # Load SPR definitions
    with open(spr_file, 'r', encoding='utf-8') as f:
        spr_data = json.load(f)
    
    # Handle both dict and list formats
    if isinstance(spr_data, dict):
        sprs = spr_data
    elif isinstance(spr_data, list):
        sprs = {spr['spr_id']: spr for spr in spr_data if isinstance(spr, dict) and 'spr_id' in spr}
    else:
        print("❌ ERROR: Invalid SPR data format")
        return {}
    
    print(f"✅ Loaded {len(sprs)} SPRs")
    
    # Initialize Zepto processor
    try:
        zepto_processor = ZeptoSPRProcessorAdapter()
        print("✅ Zepto SPR processor initialized")
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Zepto processor: {e}")
        print("   This may require PatternCrystallizationEngine to be available")
        return {}
    
    # Find ALL SPRs that need Zepto compression:
    # 1. Missing zepto_spr
    # 2. Empty zepto_spr or just "Ξ"
    # 3. Pseudo-compressed (long readable text)
    spr_to_compress = []
    for spr_id, spr in sprs.items():
        zepto_spr = spr.get('zepto_spr', '')
        
        # Check if needs compression
        needs_compression = False
        reason = ""
        
        if not zepto_spr or zepto_spr.strip() == '':
            needs_compression = True
            reason = "missing"
        elif zepto_spr == "Ξ":
            needs_compression = True
            reason = "default_symbol"
        elif is_pseudo_compressed(zepto_spr):
            needs_compression = True
            reason = "pseudo_compressed"
        elif not _is_real_zepto_spr(zepto_spr):
            # Check if it's actually symbolic (might be readable text)
            needs_compression = True
            reason = "not_symbolic"
        
        if needs_compression:
            spr_to_compress.append((spr_id, spr, zepto_spr, reason))
    
    print(f"\n🔍 Found {len(spr_to_compress)} SPRs that need Zepto compression")
    if spr_to_compress:
        reasons = {}
        for _, _, _, reason in spr_to_compress:
            reasons[reason] = reasons.get(reason, 0) + 1
        print("   Breakdown:")
        for reason, count in reasons.items():
            print(f"     • {reason}: {count}")
    
    if not spr_to_compress:
        print("✅ All SPRs already have proper Zepto SPRs!")
        return {"fixed": 0, "failed": 0, "skipped": 0}
    
    # Statistics
    stats = {"fixed": 0, "failed": 0, "skipped": 0, "errors": []}
    
    # Compress each SPR
    for i, (spr_id, spr, old_zepto, reason) in enumerate(spr_to_compress, 1):
        print(f"\n[{i}/{len(spr_to_compress)}] Processing: {spr_id} (reason: {reason})")
        if old_zepto:
            print(f"   Old Zepto SPR length: {len(old_zepto)} chars")
            if len(old_zepto) > 100:
                print(f"   Preview: {old_zepto[:100]}...")
            else:
                print(f"   Old Zepto SPR: '{old_zepto}'")
        else:
            print(f"   Old Zepto SPR: (missing/empty)")
        
        # Get the narrative to compress
        # Priority: definition > term > old_zepto (if readable)
        definition = spr.get('definition', '')
        term = spr.get('term', spr_id)
        
        # Build narrative from available sources
        narrative_parts = []
        if term:
            narrative_parts.append(term)
        if definition and len(definition) > 10:
            narrative_parts.append(definition)
        
        narrative = " ".join(narrative_parts).strip()
        
        # If narrative is too short and old_zepto is readable, use it
        if len(narrative) < 50 and old_zepto and len(old_zepto) > 50 and not _is_real_zepto_spr(old_zepto):
            narrative = old_zepto
        
        if not narrative or len(narrative) < 10:
            print(f"   ⚠️  Insufficient narrative for compression (term/definition too short)")
            stats["skipped"] += 1
            continue
        
        # Compress to Zepto
        try:
            result = zepto_processor.compress_to_zepto(
                narrative=narrative,
                target_stage="Zepto"
            )
            
            if result.error:
                print(f"   ❌ Compression error: {result.error}")
                stats["failed"] += 1
                stats["errors"].append(f"{spr_id}: {result.error}")
                continue
            
            if not result.zepto_spr or len(result.zepto_spr) == 0:
                print(f"   ⚠️  Compression produced empty result")
                stats["skipped"] += 1
                continue
            
            new_zepto = result.zepto_spr
            compression_ratio = result.compression_ratio
            
            # Verify result is actually symbolic (the fixed _finalize_crystal should ensure this)
            zepto_symbols = ['|', 'Γ', 'Σ', 'Δ', 'Θ', 'Λ', 'Ξ', 'Π', 'Φ', 'Ψ', 'Ω', 
                            'Α', 'Β', 'Ε', 'Η', 'Ι', 'Κ', 'Μ', 'Ν', 'Ο', 'Ρ', 'Τ', 'Υ', 'Χ', 'Æ']
            has_symbols = any(symbol in new_zepto for symbol in zepto_symbols)
            is_short = len(new_zepto) <= 50
            is_readable = ' ' in new_zepto or (len([c for c in new_zepto if c.isalpha() and c.islower()]) > len(new_zepto) * 0.5)
            
            is_actually_symbolic = has_symbols and is_short and not is_readable
            
            if is_actually_symbolic:
                print(f"   ✅ Compressed to {len(new_zepto)} chars (ratio: {compression_ratio:.2f}x) - SYMBOLIC")
                print(f"   New Zepto SPR: '{new_zepto}'")
            else:
                print(f"   ⚠️  Compressed to {len(new_zepto)} chars (ratio: {compression_ratio:.2f}x)")
                print(f"   New Zepto SPR: '{new_zepto}'")
                print(f"   ⚠️  WARNING: Result may not be fully symbolic - compression system may need LLM")
                # Still update it - the _finalize_crystal fix should have made it more symbolic
                # If it's still not perfect, it's better than the pseudo-compressed version
            
            # Update the SPR
            if not dry_run:
                spr['zepto_spr'] = new_zepto
                
                # Update symbol_codex if new entries were created
                if result.new_codex_entries:
                    existing_codex = spr.get('symbol_codex', {})
                    existing_codex.update(result.new_codex_entries)
                    spr['symbol_codex'] = existing_codex
                    print(f"   📝 Updated symbol_codex with {len(result.new_codex_entries)} new entries")
            
            stats["fixed"] += 1
            
        except Exception as e:
            print(f"   ❌ Exception during compression: {e}")
            stats["failed"] += 1
            stats["errors"].append(f"{spr_id}: {str(e)}")
            continue
    
    # Save updated SPR definitions
    if not dry_run and stats["fixed"] > 0:
        print(f"\n💾 Saving updated SPR definitions...")
        
        # Preserve original format (dict or list)
        if isinstance(spr_data, dict):
            updated_data = sprs
        else:
            # Convert back to list format
            updated_data = list(sprs.values())
        
        # Create backup
        backup_file = spr_file.with_suffix('.json.backup')
        print(f"   Creating backup: {backup_file}")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(spr_data, f, indent=2, ensure_ascii=False)
        
        # Save updated data
        with open(spr_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Saved {spr_file}")
    
    return stats


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix pseudo-compressed Zepto SPRs')
    parser.add_argument('--spr-file', type=str, 
                       default='knowledge_graph/spr_definitions_tv.json',
                       help='Path to SPR definitions file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Dry run mode (don\'t save changes)')
    
    args = parser.parse_args()
    
    spr_file = Path(args.spr_file)
    if not spr_file.exists():
        print(f"❌ ERROR: SPR file not found: {spr_file}")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be saved\n")
    
    stats = fix_zepto_sprs(spr_file, dry_run=args.dry_run)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"✅ Fixed: {stats.get('fixed', 0)}")
    print(f"❌ Failed: {stats.get('failed', 0)}")
    print(f"⏭️  Skipped: {stats.get('skipped', 0)}")
    
    if stats.get('errors'):
        print(f"\n⚠️  Errors encountered:")
        for error in stats['errors'][:10]:  # Show first 10 errors
            print(f"   • {error}")
        if len(stats['errors']) > 10:
            print(f"   ... and {len(stats['errors']) - 10} more")
    
    if args.dry_run:
        print("\n💡 Run without --dry-run to apply changes")


if __name__ == '__main__':
    main()

