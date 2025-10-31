#!/usr/bin/env python3
"""
Test Script for Qiskit-CFP Integration
Validates the enhanced CFP framework with authentic quantum operations via Qiskit.

This script tests:
1. Qiskit state preparation
2. Quantum evolution using PauliEvolutionGate
3. Entanglement detection using Qiskit partial_trace and entropy
4. Full CFP workflow with Qiskit backend
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import numpy as np
import logging
from Three_PointO_ArchE.cfp_framework import CfpframeworK
from Three_PointO_ArchE.quantum_utils import (
    prepare_quantum_state_qiskit, 
    evolve_flux_qiskit,
    detect_entanglement_qiskit,
    integrate_confluence_qiskit,
    measure_insight_qiskit,
    QISKIT_AVAILABLE
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

def test_qiskit_state_preparation():
    """Test Phase 1: State Preparation with Qiskit"""
    logger.info("=" * 60)
    logger.info("PHASE 1: Testing Qiskit State Preparation")
    logger.info("=" * 60)
    
    if not QISKIT_AVAILABLE:
        logger.error("Qiskit is not available. Cannot test state preparation.")
        return False
    
    try:
        # Create initial metrics
        initial_metrics = np.array([0.5, 0.3, 0.2])
        
        # Create statevector using Qiskit
        statevector = prepare_quantum_state_qiskit(initial_metrics, num_qubits=2)
        
        logger.info(f"✓ Successfully prepared Qiskit Statevector")
        logger.info(f"  - Statevector type: {type(statevector)}")
        logger.info(f"  - Number of qubits: {statevector.num_qubits}")
        logger.info(f"  - State dimensions: {statevector.dim}")
        
        # Verify normalization
        probabilities = np.abs(statevector.data)**2
        total_prob = np.sum(probabilities)
        logger.info(f"  - Total probability: {total_prob:.6f}")
        
        assert np.isclose(total_prob, 1.0, atol=1e-6), f"State not normalized: {total_prob}"
        logger.info("✓ State is properly normalized")
        
        return True
    except Exception as e:
        logger.error(f"✗ State preparation failed: {e}", exc_info=True)
        return False

def test_qiskit_evolution():
    """Test Phase 2: Evolution using Qiskit PauliEvolutionGate"""
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 2: Testing Qiskit Evolution")
    logger.info("=" * 60)
    
    if not QISKIT_AVAILABLE:
        logger.error("Qiskit is not available. Cannot test evolution.")
        return False
    
    try:
        from qiskit.quantum_info import Statevector
        from qiskit import QuantumCircuit
        
        # Create initial state
        initial_metrics = np.array([0.6, 0.4])
        statevector = prepare_quantum_state_qiskit(initial_metrics, num_qubits=1)
        
        # Create evolution
        time_steps = np.array([0.1, 0.2, 0.3])
        hamiltonian_coeffs = np.array([1.0])
        
        evolved_states = evolve_flux_qiskit(statevector, time_steps, hamiltonian_coeffs, observable="Z")
        
        logger.info(f"✓ Successfully evolved state with Qiskit")
        logger.info(f"  - Number of time steps: {len(time_steps)}")
        logger.info(f"  - Evolved states: {len(evolved_states)}")
        
        # Check that states evolved
        for i, evolved in enumerate(evolved_states):
            logger.info(f"  - Step {i}: State norm = {np.linalg.norm(evolved.data):.6f}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Evolution failed: {e}", exc_info=True)
        return False

def test_entanglement_detection():
    """Test Phase 3: Entanglement Detection"""
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 3: Testing Entanglement Detection")
    logger.info("=" * 60)
    
    if not QISKIT_AVAILABLE:
        logger.error("Qiskit is not available. Cannot test entanglement detection.")
        return False
    
    try:
        from qiskit.quantum_info import Statevector
        from qiskit import QuantumCircuit
        
        # Create a Bell state (maximally entangled)
        qc = QuantumCircuit(2)
        qc.h(0)  # Hadamard gate
        qc.cx(0, 1)  # CNOT gate
        bell_state = Statevector.from_instruction(qc)
        
        # Detect entanglement
        entropy = detect_entanglement_qiskit(bell_state, subsystem_a_qubits=[0])
        
        logger.info(f"✓ Successfully detected entanglement")
        logger.info(f"  - Bell state prepared: {bell_state}")
        logger.info(f"  - Subsystem entropy (measure of entanglement): {entropy:.6f}")
        
        # For a Bell state, entropy should be ln(2) ≈ 0.693 (maximum for a 2-qubit system)
        assert entropy > 0.6, f"Bell state should have high entropy, got {entropy}"
        logger.info("✓ Entanglement properly detected (high entropy)")
        
        return True
    except Exception as e:
        logger.error(f"✗ Entanglement detection failed: {e}", exc_info=True)
        return False

def test_confluence_integration():
    """Test Phase 4: Confluence Integration"""
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 4: Testing Confluence Integration")
    logger.info("=" * 60)
    
    if not QISKIT_AVAILABLE:
        logger.error("Qiskit is not available. Cannot test confluence integration.")
        return False
    
    try:
        from qiskit.quantum_info import Statevector
        
        # Create two flux states
        flux_a_metrics = np.array([0.5, 0.5])
        flux_b_metrics = np.array([0.3, 0.7])
        
        flux_a = prepare_quantum_state_qiskit(flux_a_metrics, num_qubits=1)
        flux_b = prepare_quantum_state_qiskit(flux_b_metrics, num_qubits=1)
        
        # Integrate confluence
        interaction_coeffs = [0.5]
        combined = integrate_confluence_qiskit(flux_a, flux_b, interaction_coeffs)
        
        logger.info(f"✓ Successfully integrated confluence")
        logger.info(f"  - Combined state dimensions: {combined.dim}")
        logger.info(f"  - Number of qubits: {combined.num_qubits}")
        
        # Verify normalization
        probabilities = np.abs(combined.data)**2
        total_prob = np.sum(probabilities)
        logger.info(f"  - Total probability: {total_prob:.6f}")
        
        assert np.isclose(total_prob, 1.0, atol=1e-6), f"Combined state not normalized: {total_prob}"
        logger.info("✓ Confluence integration successful")
        
        return True
    except Exception as e:
        logger.error(f"✗ Confluence integration failed: {e}", exc_info=True)
        return False

def test_cfp_full_integration():
    """Test Phase 5: Full CFP Integration with Qiskit"""
    logger.info("\n" + "=" * 60)
    logger.info("PHASE 5: Testing Full CFP Integration")
    logger.info("=" * 60)
    
    try:
        # Create system configurations
        system_a_config = {
            'quantum_state': [0.6, 0.4],
            'label': 'System Alpha'
        }
        
        system_b_config = {
            'quantum_state': [0.3, 0.7],
            'label': 'System Beta'
        }
        
        # Initialize CFP with Qiskit evolution
        cfp = CfpframeworK(
            system_a_config=system_a_config,
            system_b_config=system_b_config,
            observable="position",
            time_horizon=5.0,
            integration_steps=50,
            evolution_model_type="qiskit"
        )
        
        logger.info("✓ CFP framework initialized with Qiskit evolution model")
        
        # Run analysis
        results = cfp.run_analysis()
        
        logger.info("✓ CFP analysis completed")
        logger.info(f"  - Status: {results.get('reflection', {}).get('status', 'Unknown')}")
        logger.info(f"  - Confidence: {results.get('reflection', {}).get('confidence', 0.0)}")
        
        if 'quantum_flux_difference' in results:
            logger.info(f"  - Quantum Flux Difference: {results['quantum_flux_difference']:.6f}")
        
        if 'entanglement_correlation_MI' in results:
            logger.info(f"  - Entanglement Correlation (MI): {results['entanglement_correlation_MI']:.6f}")
        
        if 'entropy_system_a' in results:
            logger.info(f"  - Entropy System A: {results['entropy_system_a']:.6f}")
        
        if 'entropy_system_b' in results:
            logger.info(f"  - Entropy System B: {results['entropy_system_b']:.6f}")
        
        return True
    except Exception as e:
        logger.error(f"✗ Full CFP integration failed: {e}", exc_info=True)
        return False

def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("QISKIT-CFP INTEGRATION TEST SUITE")
    logger.info("=" * 60)
    
    if not QISKIT_AVAILABLE:
        logger.warning("Qiskit is not available. Some tests will be skipped.")
    
    # Run all tests
    tests = [
        ("Qiskit State Preparation", test_qiskit_state_preparation),
        ("Qiskit Evolution", test_qiskit_evolution),
        ("Entanglement Detection", test_entanglement_detection),
        ("Confluence Integration", test_confluence_integration),
        ("Full CFP Integration", test_cfp_full_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    logger.info(f"\nTotal: {total}, Passed: {passed}, Failed: {total - passed}")
    
    if passed == total:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

