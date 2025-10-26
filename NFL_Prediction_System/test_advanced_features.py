#!/usr/bin/env python3
"""
Test script for Advanced Three_PointO_ArchE Features
Tests the integrated NFL Prediction System with quantum analysis capabilities
"""

import json
import sys
import os
from datetime import datetime

# Import the integrated system
import ultimate_gambling_engine as uge

def test_cfp_framework():
    """Test the CFP Framework with NFL team data"""
    print("\n🔬 Testing CFP Framework with NFL Data")
    print("=" * 50)

    if not uge.CfpframeworK:
        print("❌ CFP Framework not available")
        return False

    try:
        # Create system configurations for two NFL teams
        system_a_config = {
            "quantum_state": [1.0, 0.0],  # Kansas City Chiefs
            "name": "Kansas City Chiefs",
            "type": "nfl_team",
            "offensive_efficiency": 0.85,
            "defensive_efficiency": 0.78,
            "special_teams": 0.82
        }

        system_b_config = {
            "quantum_state": [0.0, 1.0],  # Buffalo Bills
            "name": "Buffalo Bills",
            "type": "nfl_team",
            "offensive_efficiency": 0.88,
            "defensive_efficiency": 0.75,
            "special_teams": 0.79
        }

        # Initialize CFP Framework
        cfp_framework = uge.CfpframeworK(
            system_a_config=system_a_config,
            system_b_config=system_b_config,
            observable="position",
            time_horizon=10.0,
            integration_steps=100
        )

        print("✅ CFP Framework initialized successfully")
        print(f"   System A: {system_a_config['name']}")
        print(f"   System B: {system_b_config['name']}")
        print(f"   Observable: {cfp_framework.observable_name}")
        print(f"   Time Horizon: {cfp_framework.time_horizon}s")
        print(f"   Integration Steps: {cfp_framework.integration_steps}")

        # Run analysis
        print("\n🔄 Running CFP Analysis...")
        results = cfp_framework.run_analysis()

        print("✅ CFP Analysis completed!")
        print(f"   Quantum Flux Difference: {results.get('quantum_flux_difference', 'N/A')}")
        print(f"   Entanglement Correlation: {results.get('entanglement_correlation', 'N/A')}")
        print(f"   System Entropy A: {results.get('system_entropy_a', 'N/A')}")
        print(f"   System Entropy B: {results.get('system_entropy_b', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ CFP Framework test failed: {e}")
        return False

def test_adaptive_cognitive_orchestrator():
    """Test the Adaptive Cognitive Orchestrator"""
    print("\n🧠 Testing Adaptive Cognitive Orchestrator")
    print("=" * 50)

    if not uge.AdaptiveCognitiveOrchestrator:
        print("❌ Adaptive Cognitive Orchestrator not available")
        return False

    try:
        # Test with NFL-related query
        test_query = "Analyze NFL game strategy between Kansas City Chiefs and Buffalo Bills"

        orchestrator = uge.AdaptiveCognitiveOrchestrator(
            protocol_chunks=["NFL", "Football", "Strategy"],
            llm_provider=uge.enhanced_llm_provider
        )

        print(f"✅ Adaptive Cognitive Orchestrator initialized")
        print(f"   Query: {test_query}")

        # Process the query
        result, metadata = orchestrator.process_query_with_evolution(test_query)

        print("✅ Query processing completed!")
        print(f"   Result length: {len(result)} characters")
        print(f"   Active domain: {metadata.get('active_domain', 'unknown')}")
        print(f"   Processing time: {metadata.get('processing_time', 'unknown')}")

        return True

    except Exception as e:
        print(f"❌ Adaptive Cognitive Orchestrator test failed: {e}")
        return False

def test_knowledge_graph_manager():
    """Test the Knowledge Graph Manager"""
    print("\n📊 Testing Knowledge Graph Manager")
    print("=" * 50)

    if not uge.KnowledgeGraphManager:
        print("❌ Knowledge Graph Manager not available")
        return False

    try:
        kg_manager = uge.KnowledgeGraphManager(
            spr_definitions_path="Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json",
            knowledge_tapestry_path="Three_PointO_ArchE/knowledge_graph/knowledge_tapestry.json"
        )

        print("✅ Knowledge Graph Manager initialized")

        # Test listing specifications
        specs = kg_manager.list_specifications()
        print(f"   Available specifications: {len(specs)}")
        print(f"   Sample specs: {specs[:3]}")

        # Test searching for NFL-related content
        nfl_results = kg_manager.search_specifications("NFL")
        print(f"   NFL-related content found: {len(nfl_results)}")

        return True

    except Exception as e:
        print(f"❌ Knowledge Graph Manager test failed: {e}")
        return False

def test_spr_manager():
    """Test the SPR Manager"""
    print("\n⚡ Testing SPR Manager")
    print("=" * 40)

    if not uge.SPRManager:
        print("❌ SPR Manager not available")
        return False

    try:
        spr_manager = uge.SPRManager("Three_PointO_ArchE/knowledge_graph/spr_definitions_tv.json")

        print("✅ SPR Manager initialized")

        # Test SPR scanning and priming
        test_text = "NFL football strategy analysis quantum computing"
        spr_results = spr_manager.scan_and_prime(test_text)

        print(f"   Test text: {test_text}")
        print(f"   SPRs detected: {len(spr_results)}")

        if spr_results:
            for spr in spr_results[:3]:  # Show first 3 results
                print(f"   • {spr.get('spr_id', 'unknown')}: {spr.get('confidence', 0):.2f}")

        return True

    except Exception as e:
        print(f"❌ SPR Manager test failed: {e}")
        return False

def test_resonance_evaluator():
    """Test the Resonance Evaluator"""
    print("\n🎯 Testing Resonance Evaluator")
    print("=" * 40)

    if not uge.create_resonance_evaluator:
        print("❌ Resonance Evaluator not available")
        return False

    try:
        evaluator = uge.create_resonance_evaluator()

        # Test resonance evaluation
        test_data = {
            "data_sources": [{"name": "NFL Stats", "quality": 0.9}],
            "analysis_results": [{"accuracy": 0.85}],
            "strategic_objectives": ["Predict game outcomes"],
            "predicted_outcomes": [{"confidence": 0.8}],
            "temporal_scope": {"horizon": "weekly"},
            "iar_history": [{"confidence": 0.75}]
        }

        metrics = evaluator.evaluate_cognitive_resonance(test_data)

        print("✅ Resonance Evaluator working")
        print(f"   Data Alignment: {metrics.data_alignment:.2f}")
        print(f"   Analysis Coherence: {metrics.analysis_coherence:.2f}")
        print(f"   Objective Clarity: {metrics.objective_clarity:.2f}")
        print(f"   Overall Resonance: {metrics.overall_resonance:.2f}")
        print(f"   Confidence: {metrics.confidence:.2f}")

        return True

    except Exception as e:
        print(f"❌ Resonance Evaluator test failed: {e}")
        return False

def test_enhanced_llm_provider():
    """Test the Enhanced LLM Provider"""
    print("\n🤖 Testing Enhanced LLM Provider")
    print("=" * 40)

    if not uge.EnhancedLLMProvider:
        print("❌ Enhanced LLM Provider not available")
        return False

    try:
        if not uge.enhanced_llm_provider:
            print("❌ Enhanced LLM Provider not initialized")
            return False

        print("✅ Enhanced LLM Provider initialized")

        # Test capabilities
        capabilities = uge.enhanced_llm_provider.get_capabilities()
        print(f"   Available capabilities: {capabilities}")

        # Test a simple query
        test_query = "What are the key factors in NFL game prediction?"
        result = uge.enhanced_llm_provider.generate(test_query)

        print(f"   Test query: {test_query}")
        print(f"   Response length: {len(result)} characters")
        print(f"   Response preview: {result[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Enhanced LLM Provider test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Advanced Three_PointO_ArchE Features")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")

    tests = [
        test_cfp_framework,
        test_adaptive_cognitive_orchestrator,
        test_knowledge_graph_manager,
        test_spr_manager,
        test_resonance_evaluator,
        test_enhanced_llm_provider,
    ]

    results = {}
    for test in tests:
        try:
            results[test.__name__] = test()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results[test.__name__] = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for result in results.values() if result)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is fully operational.")
    else:
        print(f"\n⚠️  {total - passed} tests failed. System partially operational.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
