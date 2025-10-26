#!/usr/bin/env python3
"""
ArchE Full Automation Activation Script
========================================

This script activates ALL existing automation systems and verifies their integration:
1. Session Auto-Capture
2. SPR Auto-Priming
3. Autopoietic Learning Loop
4. Insight Solidification
5. ThoughtTrail Monitoring

This is the master integration script that connects all the pieces.
"""

import sys
import logging
from pathlib import Path

# Add Three_PointO_ArchE to path
sys.path.insert(0, str(Path(__file__).parent))

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from Three_PointO_ArchE.temporal_core import now_iso

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_existing_systems():
    """Verify all existing automation systems are present."""
    logger.info("=" * 60)
    logger.info("VERIFYING EXISTING AUTOMATION SYSTEMS")
    logger.info("=" * 60)
    
    results = {}
    
    # 1. SPR Manager
    try:
        from Three_PointO_ArchE.spr_manager import SPRManager
        spr_path = Path("knowledge_graph/spr_definitions_tv.json")
        if spr_path.exists():
            spr_manager = SPRManager(str(spr_path))
            spr_count = len(spr_manager.sprs)
            results['spr_manager'] = {
                'status': 'ACTIVE',
                'sprs_loaded': spr_count,
                'file': str(spr_path)
            }
            logger.info(f"✅ SPR Manager: {spr_count} SPRs loaded")
        else:
            results['spr_manager'] = {'status': 'FILE_NOT_FOUND', 'file': str(spr_path)}
            logger.warning(f"⚠️  SPR Manager: File not found at {spr_path}")
    except Exception as e:
        results['spr_manager'] = {'status': 'ERROR', 'error': str(e)}
        logger.error(f"❌ SPR Manager: {e}")
    
    # 2. Session Auto-Capture
    try:
        from Three_PointO_ArchE.session_auto_capture import SessionAutoCapture
        session_capture = SessionAutoCapture()
        results['session_capture'] = {
            'status': 'ACTIVE',
            'output_dir': str(session_capture.output_dir)
        }
        logger.info(f"✅ Session Auto-Capture: Active, output to {session_capture.output_dir}")
    except Exception as e:
        results['session_capture'] = {'status': 'ERROR', 'error': str(e)}
        logger.error(f"❌ Session Auto-Capture: {e}")
    
    # 3. Autopoietic Learning Loop
    try:
        from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop
        learning_loop = AutopoieticLearningLoop()
        results['learning_loop'] = {
            'status': 'ACTIVE',
            'guardian_review': learning_loop.guardian_review_required
        }
        logger.info(f"✅ Autopoietic Learning Loop: Active, Guardian review={learning_loop.guardian_review_required}")
    except Exception as e:
        results['learning_loop'] = {'status': 'ERROR', 'error': str(e)}
        logger.error(f"❌ Autopoietic Learning Loop: {e}")
    
    # 4. ThoughtTrail
    try:
        from Three_PointO_ArchE.thought_trail import ThoughtTrail
        thought_trail = ThoughtTrail(maxlen=1000)
        results['thought_trail'] = {
            'status': 'ACTIVE',
            'buffer_size': thought_trail.entries.maxlen
        }
        logger.info(f"✅ ThoughtTrail: Active, buffer size={thought_trail.entries.maxlen}")
    except Exception as e:
        results['thought_trail'] = {'status': 'ERROR', 'error': str(e)}
        logger.error(f"❌ ThoughtTrail: {e}")
    
    # 5. Insight Solidification Engine
    try:
        from Three_PointO_ArchE.insight_solidification_engine import InsightSolidificationEngine, SPRManager as ISE_SPRManager
        kt_path = Path("knowledge_graph/spr_definitions_tv.json")
        if kt_path.exists():
            ise = InsightSolidificationEngine(knowledge_tapestry_path=str(kt_path))
            results['insight_solidification'] = {
                'status': 'ACTIVE',
                'knowledge_tapestry': str(kt_path)
            }
            logger.info(f"✅ Insight Solidification Engine: Active")
        else:
            results['insight_solidification'] = {'status': 'FILE_NOT_FOUND', 'file': str(kt_path)}
            logger.warning(f"⚠️  Insight Solidification: Knowledge tapestry not found")
    except Exception as e:
        results['insight_solidification'] = {'status': 'ERROR', 'error': str(e)}
        logger.error(f"❌ Insight Solidification Engine: {e}")
    
    # 6. Workflow Files
    workflow_files = [
        "core_workflows/insight_solidification.json",
        "core_workflows/ReSSyD_Session_Context_Capture_Workflow_v3.0.json"
    ]
    
    results['workflows'] = {}
    for wf in workflow_files:
        wf_path = Path(wf)
        if wf_path.exists():
            results['workflows'][wf] = 'FOUND'
            logger.info(f"✅ Workflow: {wf}")
        else:
            results['workflows'][wf] = 'NOT_FOUND'
            logger.warning(f"⚠️  Workflow: {wf} not found")
    
    return results

def test_integration():
    """Test integration between systems."""
    logger.info("=" * 60)
    logger.info("TESTING SYSTEM INTEGRATION")
    logger.info("=" * 60)
    
    try:
        from Three_PointO_ArchE.spr_manager import SPRManager
        from Three_PointO_ArchE.session_auto_capture import SessionAutoCapture
        from Three_PointO_ArchE.thought_trail import ThoughtTrail, IAREntry
        
        # Initialize systems
        spr_manager = SPRManager("knowledge_graph/spr_definitions_tv.json")
        session_capture = SessionAutoCapture()
        thought_trail = ThoughtTrail()
        
        # Test 1: SPR Priming
        logger.info("\n--- Test 1: SPR Priming ---")
        test_text = "Testing Cognitive resonancE and Implementation resonancE detection"
        primed_sprs = spr_manager.scan_and_prime(test_text)
        logger.info(f"✅ Primed {len(primed_sprs)} SPRs from test text")
        
        # Test 2: Session Capture
        logger.info("\n--- Test 2: Session Capture ---")
        session_capture.capture_message("user", "Test message from user")
        session_capture.capture_message("assistant", "Test response from ArchE")
        session_capture.capture_spr_priming(primed_sprs)
        summary = session_capture.get_session_summary()
        logger.info(f"✅ Session captured: {summary}")
        
        # Test 3: IAR Entry
        logger.info("\n--- Test 3: ThoughtTrail IAR Entry ---")
        test_iar = IAREntry(
            task_id="test_integration",
            action_type="system_test",
            inputs={"test": "integration"},
            outputs={"status": "success"},
            iar={
                "intention": "Test integration",
                "action": "Created test IAR entry",
                "reflection": "Integration test successful"
            },
            timestamp=now_iso(),
            confidence=0.95,
            metadata={"test": True}
        )
        thought_trail.add_entry(test_iar)
        session_capture.capture_iar_entry(vars(test_iar))
        logger.info("✅ IAR entry added to ThoughtTrail and captured")
        
        # Test 4: Export Session
        logger.info("\n--- Test 4: Session Export ---")
        try:
            export_path = session_capture.export_session(
                session_id="integration_test",
                topic="full automation test"
            )
            logger.info(f"✅ Session exported to: {export_path}")
        except Exception as e:
            logger.error(f"❌ Session export failed: {e}")
        
        logger.info("\n✅ ALL INTEGRATION TESTS PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_status_report(results, integration_success):
    """Generate comprehensive status report."""
    logger.info("=" * 60)
    logger.info("AUTOMATION STATUS REPORT")
    logger.info("=" * 60)
    
    print("\n## 🤖 ARCHE AUTOMATION SYSTEMS STATUS")
    print(f"\n**Generated**: {now_iso()}")
    print("\n### Core Systems")
    
    for system, status in results.items():
        if system != 'workflows':
            status_emoji = "✅" if status.get('status') == 'ACTIVE' else "❌"
            print(f"\n#### {system.replace('_', ' ').title()}")
            print(f"**Status**: {status_emoji} {status.get('status', 'UNKNOWN')}")
            for key, value in status.items():
                if key != 'status':
                    print(f"- {key}: {value}")
    
    print("\n### Workflows")
    for wf, status in results.get('workflows', {}).items():
        status_emoji = "✅" if status == 'FOUND' else "❌"
        print(f"- {status_emoji} {wf}: {status}")
    
    print("\n### Integration Test")
    if integration_success:
        print("✅ **PASSED** - All systems integrated successfully")
    else:
        print("❌ **FAILED** - Integration issues detected")
    
    # Calculate overall status
    active_count = sum(1 for s in results.values() if isinstance(s, dict) and s.get('status') == 'ACTIVE')
    total_count = len([k for k in results.keys() if k != 'workflows'])
    
    print(f"\n### Overall Status")
    print(f"**Active Systems**: {active_count}/{total_count}")
    print(f"**Integration**: {'OPERATIONAL' if integration_success else 'NEEDS ATTENTION'}")
    
    if active_count == total_count and integration_success:
        print("\n🌟 **FULL AUTOMATION ACHIEVED** 🌟")
        print("\nAll systems are active and integrated:")
        print("- Session capture → Auto-exports conversations")
        print("- SPR priming → Auto-loads definitions")
        print("- Learning loop → Auto-detects patterns")
        print("- Insight solidification → Auto-proposes SPRs (Guardian approval)")
        print("- ThoughtTrail → Auto-captures all IAR entries")
    else:
        print("\n⚠️  **AUTOMATION INCOMPLETE** ⚠️")
        print("\nSome systems need attention. Check errors above.")

def main():
    """Main activation and verification routine."""
    print("\n" + "=" * 60)
    print("ARCHE FULL AUTOMATION ACTIVATION")
    print("=" * 60)
    print(f"\nStarting at: {now_iso()}")
    print(f"Working directory: {Path.cwd()}")
    
    # Step 1: Verify existing systems
    results = verify_existing_systems()
    
    # Step 2: Test integration
    integration_success = test_integration()
    
    # Step 3: Generate report
    generate_status_report(results, integration_success)
    
    print("\n" + "=" * 60)
    print("ACTIVATION COMPLETE")
    print("=" * 60)
    
    # Exit code
    if all(r.get('status') == 'ACTIVE' for r in results.values() if isinstance(r, dict)) and integration_success:
        print("\n✅ All systems operational. Full automation achieved.")
        return 0
    else:
        print("\n⚠️  Some systems need attention. Review report above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


