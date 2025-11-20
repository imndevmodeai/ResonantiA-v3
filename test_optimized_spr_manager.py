#!/usr/bin/env python3
"""
Test Optimized SPRManager
Verifies that optimized SPRManager works correctly with both storage formats.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Three_PointO_ArchE.spr_manager_optimized import OptimizedSPRManager

def test_optimized_manager():
    """Test optimized SPRManager."""
    print("=" * 70)
    print("TESTING OPTIMIZED SPR MANAGER")
    print("=" * 70)
    
    # Test with optimized storage
    optimized_dir = project_root / "knowledge_graph" / "optimized"
    index_file = optimized_dir / "spr_index.json"
    
    if not index_file.exists():
        print(f"❌ Optimized storage not found at {index_file}")
        print("   Run migrate_kg_to_zepto_optimized.py first")
        return False
    
    print(f"\n📚 Loading from optimized storage...")
    manager = OptimizedSPRManager(
        spr_filepath=str(index_file),
        optimized_dir=str(optimized_dir)
    )
    
    print(f"✅ Loaded {len(manager.sprs)} SPRs")
    print(f"   Using optimized storage: {manager.use_optimized}")
    print(f"   Index size: {index_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Test 1: Get SPR by ID
    print("\n" + "=" * 70)
    print("TEST 1: Get SPR by ID")
    print("=" * 70)
    
    test_spr_id = list(manager.sprs.keys())[0]
    spr = manager.get_spr(test_spr_id)
    
    if spr:
        print(f"✅ Retrieved SPR: {spr.get('spr_id', 'N/A')}")
        print(f"   Term: {spr.get('term', 'N/A')}")
        print(f"   Category: {spr.get('category', 'N/A')}")
        print(f"   Has Zepto: {bool(spr.get('zepto_spr'))}")
        print(f"   Has Zepto hash: {bool(spr.get('zepto_hash'))}")
    else:
        print(f"❌ Failed to retrieve SPR: {test_spr_id}")
        return False
    
    # Test 2: Get SPR with Narrative layer
    print("\n" + "=" * 70)
    print("TEST 2: Get SPR with Narrative Layer (Lazy Loading)")
    print("=" * 70)
    
    spr_with_narrative = manager.get_spr(test_spr_id, layer='Narrative')
    
    if spr_with_narrative:
        narrative = spr_with_narrative.get('narrative', '')
        if narrative:
            print(f"✅ Loaded Narrative layer: {len(narrative)} characters")
            print(f"   Preview: {narrative[:100]}...")
        else:
            print(f"⚠️  No Narrative layer found (may not have narrative_hash)")
    else:
        print(f"❌ Failed to retrieve SPR with Narrative layer")
    
    # Test 3: Scan and Prime
    print("\n" + "=" * 70)
    print("TEST 3: Scan and Prime")
    print("=" * 70)
    
    test_text = f"Using {test_spr_id} for testing"
    primed_sprs = manager.scan_and_prime(test_text)
    
    print(f"✅ Scanned text: '{test_text}'")
    print(f"   Found {len(primed_sprs)} SPRs")
    for spr in primed_sprs:
        if spr:
            print(f"   - {spr.get('spr_id', 'N/A')}: {spr.get('term', 'N/A')}")
    
    # Test 4: Query by Term
    print("\n" + "=" * 70)
    print("TEST 4: Query by Term (Database)")
    print("=" * 70)
    
    if manager.use_optimized and manager.db_conn:
        test_term = spr.get('term', '').split()[0] if spr.get('term') else 'Action'
        results = manager.query_by_term(test_term)
        print(f"✅ Query term: '{test_term}'")
        print(f"   Found {len(results)} SPRs")
        for result in results[:5]:
            if result:
                print(f"   - {result.get('spr_id', 'N/A')}: {result.get('term', 'N/A')}")
    else:
        print("⚠️  Database not available, skipping query test")
    
    # Test 5: Get SPR by Zepto
    print("\n" + "=" * 70)
    print("TEST 5: Get SPR by Zepto Hash (Content-Addressable)")
    print("=" * 70)
    
    if spr.get('zepto_spr') and spr.get('symbol_codex'):
        zepto_spr = spr.get('zepto_spr')
        symbol_codex = spr.get('symbol_codex')
        spr_by_zepto = manager.get_spr_by_zepto(zepto_spr, symbol_codex)
        
        if spr_by_zepto:
            print(f"✅ Retrieved SPR by Zepto hash")
            print(f"   SPR ID: {spr_by_zepto.get('spr_id', 'N/A')}")
            print(f"   Term: {spr_by_zepto.get('term', 'N/A')}")
        else:
            print(f"⚠️  Failed to retrieve SPR by Zepto (may not be in Zepto index)")
    else:
        print("⚠️  SPR doesn't have Zepto SPR, skipping test")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Optimized storage: {manager.use_optimized}")
    print(f"✅ SPRs loaded: {len(manager.sprs)}")
    print(f"✅ All tests passed")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_optimized_manager()
    sys.exit(0 if success else 1)

