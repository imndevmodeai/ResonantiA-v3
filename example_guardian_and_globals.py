#!/usr/bin/env python3
"""
Example Script: Guardian Review + Global Namespace Usage

This script demonstrates:
1. Initializing ArchE with global namespace storage
2. Using objects from global namespace
3. Checking and reviewing Guardian queue
4. Approving/rejecting wisdom items

Usage:
    python3 example_guardian_and_globals.py
"""

from arche_unified_init import prime_arche_system

def main():
    print("=" * 80)
    print("GUARDIAN REVIEW + GLOBAL NAMESPACE EXAMPLE")
    print("=" * 80)
    
    # ========================================================================
    # STEP 1: Initialize with Global Namespace Storage
    # ========================================================================
    print("\n[STEP 1] Initializing ArchE systems with global namespace storage...")
    results = prime_arche_system(store_globals=True, save_results=True)
    
    # Verify initialization
    if not results["initialized_objects"]["references"]["learning_loop"]:
        print("❌ Learning Loop not initialized - cannot demonstrate Guardian Review")
        return
    
    print("\n✅ Initialization complete!")
    print(f"   Systems stored in global namespace: {len(results['initialized_objects'])}")
    
    # ========================================================================
    # STEP 2: Access Objects from Global Namespace
    # ========================================================================
    print("\n[STEP 2] Accessing objects from global namespace...")
    
    # Check what's available
    available_objects = []
    for obj_name in ['spr_manager', 'learning_loop', 'session_capture', 
                     'thought_trail', 'crystallization_engine', 'ingest_file_with_zepto']:
        if obj_name in globals():
            available_objects.append(obj_name)
            print(f"   ✅ {obj_name} available")
    
    print(f"\n   Total objects available: {len(available_objects)}")
    
    # ========================================================================
    # STEP 3: Use Objects from Global Namespace
    # ========================================================================
    print("\n[STEP 3] Using objects from global namespace...")
    
    # Use SPR Manager
    if 'spr_manager' in globals():
        test_text = "This text contains Cognitive resonancE and Metacognitive shifT concepts"
        primed_sprs = spr_manager.scan_and_prime(test_text)
        print(f"   ✅ SPR Manager: Primed {len(primed_sprs)} SPRs from test text")
    
    # Use Session Capture
    if 'session_capture' in globals():
        session_capture.capture_message(
            "system",
            "Guardian Review + Global Namespace example session",
            {"example": True, "step": "demonstration"}
        )
        print(f"   ✅ Session Capture: Message captured")
    
    # Use Learning Loop
    if 'learning_loop' in globals():
        print(f"   ✅ Learning Loop: Active")
        print(f"      - Guardian Review Enabled: {learning_loop.guardian_review_enabled}")
        print(f"      - Auto-Crystallization: {learning_loop.auto_crystallization}")
        print(f"      - Stardust Captured: {learning_loop.metrics.get('stardust_captured', 0)}")
    
    # ========================================================================
    # STEP 4: Check Guardian Queue
    # ========================================================================
    print("\n[STEP 4] Checking Guardian queue...")
    
    if 'learning_loop' in globals():
        queue_size = len(learning_loop.guardian_queue)
        print(f"   Guardian Queue Size: {queue_size}")
        
        if queue_size > 0:
            print(f"\n   📋 {queue_size} wisdom item(s) awaiting Guardian review:")
            
            for idx, pattern in enumerate(learning_loop.guardian_queue, 1):
                print(f"\n   [{idx}] Pattern: {pattern.pattern_signature[:50]}...")
                print(f"       Occurrences: {pattern.occurrences}")
                print(f"       Success Rate: {pattern.success_rate:.1%}")
                
                # Find associated wisdom
                wisdom_id = None
                wisdom = None
                for wid, w in learning_loop.ignited_wisdom.items():
                    if w.source_pattern.pattern_id == pattern.pattern_id:
                        wisdom_id = wid
                        wisdom = w
                        break
                
                if wisdom:
                    print(f"       Wisdom ID: {wisdom_id}")
                    print(f"       Hypothesis: {wisdom.hypothesis[:80]}...")
                    print(f"       Guardian Approval: {wisdom.guardian_approval}")
                    
                    # Example: Auto-approve if success rate > 80%
                    if pattern.success_rate > 0.8:
                        print(f"       ⚡ Auto-approving (success rate > 80%)...")
                        learning_loop.guardian_approve(
                            wisdom_id,
                            approved=True,
                            notes="Auto-approved: High success rate (>80%)"
                        )
                        print(f"       ✅ Approved")
                    else:
                        print(f"       ⏸️  Requires manual review (success rate ≤ 80%)")
        else:
            print("   ✅ No items in Guardian queue - all clear!")
    
    # ========================================================================
    # STEP 5: Demonstrate Guardian Review Interface
    # ========================================================================
    print("\n[STEP 5] Guardian Review Interface Example...")
    
    if 'learning_loop' in globals() and len(learning_loop.guardian_queue) > 0:
        print("\n   Example: Manual Guardian Review Process")
        print("   " + "-" * 60)
        
        for pattern in learning_loop.guardian_queue:
            # Find wisdom
            wisdom_id = None
            wisdom = None
            for wid, w in learning_loop.ignited_wisdom.items():
                if w.source_pattern.pattern_id == pattern.pattern_id:
                    wisdom_id = wid
                    wisdom = w
                    break
            
            if wisdom and not wisdom.guardian_approval:
                print(f"\n   📋 Reviewing Wisdom: {wisdom_id}")
                print(f"   Pattern: {pattern.pattern_signature[:60]}...")
                print(f"   Occurrences: {pattern.occurrences}")
                print(f"   Success Rate: {pattern.success_rate:.1%}")
                print(f"   Hypothesis: {wisdom.hypothesis}")
                
                # In a real scenario, you would:
                # decision = input("\n   Approve? (y/n): ")
                # notes = input("   Notes: ")
                # learning_loop.guardian_approve(wisdom_id, decision == 'y', notes)
                
                print(f"\n   💡 In interactive mode, you would:")
                print(f"      decision = input('Approve? (y/n): ')")
                print(f"      notes = input('Notes: ')")
                print(f"      learning_loop.guardian_approve(wisdom_id, decision == 'y', notes)")
    
    # ========================================================================
    # STEP 6: Check Metrics
    # ========================================================================
    print("\n[STEP 6] Learning Loop Metrics...")
    
    if 'learning_loop' in globals():
        metrics = learning_loop.metrics
        print(f"   Stardust Captured: {metrics.get('stardust_captured', 0)}")
        print(f"   Nebulae Detected: {metrics.get('nebulae_detected', 0)}")
        print(f"   Wisdom Ignited: {metrics.get('wisdom_ignited', 0)}")
        print(f"   Guardian Approvals: {metrics.get('guardian_approvals', 0)}")
        print(f"   Guardian Rejections: {metrics.get('guardian_rejections', 0)}")
        print(f"   Knowledge Crystallized: {metrics.get('knowledge_crystallized', 0)}")
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("\n✅ Demonstrated:")
    print("   1. Initialization with global namespace storage")
    print("   2. Accessing objects from global namespace")
    print("   3. Using objects directly (SPR Manager, Session Capture, etc.)")
    print("   4. Checking Guardian queue")
    print("   5. Reviewing wisdom items")
    print("   6. Approving/rejecting wisdom (example)")
    print("\n💡 Key Points:")
    print("   - Global namespace makes objects accessible everywhere")
    print("   - Guardian review prevents unsafe self-modification")
    print("   - Check Guardian queue regularly for pending wisdom")
    print("   - Always review before approving wisdom")
    print("=" * 80)


if __name__ == "__main__":
    main()






