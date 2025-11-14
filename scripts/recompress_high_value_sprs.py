#!/usr/bin/env python3
"""
PATH B: Recompress top 52 high-value SPRs to proper symbols.
Cost: ~$6.24, Time: ~2 minutes (rate-limited by Groq)
"""

import json
import sys
from pathlib import Path
import time

def recompress_high_value_sprs():
    """Recompress high-value SPRs to symbols."""
    
    # Load the high-value list
    hv_path = Path("knowledge_graph/high_value_80_sprs.json")
    with open(hv_path, 'r') as f:
        hv_data = json.load(f)
    
    high_value_ids = [s['spr_id'] for s in hv_data['sprs']]
    
    # Load SPR definitions
    spr_path = Path("knowledge_graph/spr_definitions_tv.json")
    with open(spr_path, 'r') as f:
        sprs = json.load(f)
    
    # Filter to high-value SPRs only
    high_value_sprs = [s for s in sprs if s.get('spr_id') in high_value_ids]
    
    print(f"🎯 Recompressing {len(high_value_sprs)} High-Value SPRs")
    print("=" * 90)
    
    # Try to import pattern crystallization engine
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    try:
        from Three_PointO_ArchE.pattern_crystallization_engine import PatternCrystallizationEngine
        engine = PatternCrystallizationEngine()
        print("✅ Pattern Crystallization Engine loaded\n")
    except Exception as e:
        print(f"⚠️  Engine load failed: {e}")
        print("    Attempting direct import from current path...\n")
        try:
            # Try alternative import
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "pattern_crystallization_engine",
                Path(__file__).parent.parent / "Three_PointO_ArchE" / "pattern_crystallization_engine.py"
            )
            pce_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pce_module)
            engine = pce_module.PatternCrystallizationEngine()
            print("✅ Pattern Crystallization Engine loaded (alternative method)\n")
        except Exception as e2:
            print(f"❌ Failed to load engine via any method: {e2}")
            print("    Using placeholder compression\n")
            engine = None
    
    recompressed_count = 0
    skipped_count = 0
    error_count = 0
    
    for i, spr in enumerate(high_value_sprs, 1):
        spr_id = spr.get('spr_id', '')
        term = spr.get('term', '')
        definition = spr.get('definition', '')
        
        # Check if already has good symbols
        existing_zepto = spr.get('zepto_spr', '')
        symbol_chars = ['Ω', 'Δ', 'Φ', 'Θ', 'Λ', 'Σ', 'Π', 'Æ']
        has_symbols = any(sym in existing_zepto for sym in symbol_chars)
        
        if has_symbols:
            print(f"{i:2d}. [SKIP] {term:40s} - Already has symbols")
            skipped_count += 1
            continue
        
        try:
            # Attempt recompression
            if engine:
                # Full compression with engine
                narrative = f"{term}: {definition}"
                result = engine.compress_to_zepto(
                    narrative=narrative,
                    target_stage="Zepto",
                    force_symbols=True
                )
                
                new_zepto = result.get('zepto_spr', '')
                new_codex = result.get('symbol_codex', {})
                new_stages = result.get('compression_stages', [])
                
                # Update the SPR
                spr['zepto_spr'] = new_zepto
                spr['symbol_codex'] = new_codex
                spr['compression_stages'] = new_stages
                
                # Calculate compression ratio
                if new_zepto:
                    ratio = len(narrative) / len(new_zepto)
                    spr['compression_ratio'] = f"{ratio:.1f}:1"
                
                has_new_symbols = any(sym in new_zepto for sym in symbol_chars)
                status = "RECOMP✓" if has_new_symbols else "PARTIAL"
            else:
                status = "SKIPPED"
                continue
            
            print(f"{i:2d}. [{status:6s}] {term:40s} - Ratio: {spr.get('compression_ratio', 'N/A')}")
            recompressed_count += 1
            
            # Rate limiting (be nice to Groq)
            if i % 5 == 0:
                time.sleep(1)
        
        except Exception as e:
            print(f"{i:2d}. [ERROR ] {term:40s} - {str(e)[:30]}")
            error_count += 1
    
    # Save updated SPRs back
    print("\n" + "=" * 90)
    print(f"💾 Saving {recompressed_count} recompressed SPRs back to KG...")
    
    with open(spr_path, 'w') as f:
        json.dump(sprs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved: {spr_path}")
    
    # Statistics
    print(f"\n📊 Recompression Results:")
    print(f"  ✅ Recompressed:   {recompressed_count}")
    print(f"  ⏭️  Skipped:        {skipped_count}")
    print(f"  ❌ Errors:         {error_count}")
    print(f"  💰 Cost:           ~${recompressed_count * 0.12:.2f}")
    print(f"  📈 Annual savings: ~${recompressed_count * 12:.2f}")

if __name__ == '__main__':
    recompress_high_value_sprs()
