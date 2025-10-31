import unittest
import numpy as np
from scipy.linalg import expm
import pytest
from Three_PointO_ArchE.quantum_utils import (
    superposition_state,
    entangled_state,
    calculate_shannon_entropy,
    von_neumann_entropy,
    hamiltonian_pulsed,
    run_quantum_simulation,
    partial_trace
)

class TestQuantumSimulation:
    @pytest.fixture
    def simple_hamiltonian(self):
        """Create a simple 2x2 Hamiltonian matrix for testing"""
        return np.array([[1.0, 0.5], [0.5, 1.0]], dtype=complex)

    @pytest.fixture
    def initial_state(self):
        """Create a normalized initial state vector"""
        return np.array([1.0, 0.0], dtype=complex)

    def test_hamiltonian_pulsed(self, simple_hamiltonian):
        """Test the time-dependent Hamiltonian with Gaussian pulse"""
        time = 0.0
        pulse_period = 1.0
        H = hamiltonian_pulsed(time, pulse_period)
        
        # Check shape and type
        assert H.shape == (2, 2)
        assert H.dtype == np.complex128
        
        # Check Hermiticity
        assert np.allclose(H, H.conj().T)
        
        # Test at different times
        times = [0.0, 0.5, 1.0]
        for t in times:
            H_t = hamiltonian_pulsed(t, pulse_period)
            assert np.allclose(H_t, H_t.conj().T)  # Hermiticity
            assert not np.allclose(H_t, simple_hamiltonian)  # Should be modified by pulse

    def test_quantum_simulation_basic(self, simple_hamiltonian, initial_state):
        """Test basic quantum simulation with constant Hamiltonian"""
        time_horizon = 1.0
        pulse_amplitude = 1.0
        pulse_width = 0.5
        pulse_periods = np.linspace(0.5, 10.0, 5)
        
        results = run_quantum_simulation(
            time_horizon=time_horizon,
            pulse_amplitude=pulse_amplitude,
            pulse_width=pulse_width,
            pulse_periods=pulse_periods
        )
        
        # Check results structure
        assert 'state_evolution' in results
        assert 'entropy_evolution' in results
        assert 'final_state' in results
        
        # Check dimensions
        assert len(results['state_evolution']) == len(pulse_periods)
        assert len(results['entropy_evolution']) == len(pulse_periods)
        
        # Check state normalization
        for state in results['state_evolution']:
            assert np.isclose(np.linalg.norm(state), 1.0)
        
        # Check entropy bounds
        for entropy in results['entropy_evolution']:
            assert 0.0 <= entropy <= 1.0

    def test_quantum_simulation_entanglement(self):
        """Test quantum simulation with entangled states"""
        # Create Bell state
        state_a = np.array([1.0, 0.0], dtype=complex)
        state_b = np.array([0.0, 1.0], dtype=complex)
        bell_state = entangled_state(state_a, state_b)
        
        time_horizon = 2.0
        pulse_amplitude = 2.0
        pulse_width = 0.5
        pulse_periods = np.linspace(0.5, 5.0, 10)
        
        results = run_quantum_simulation(
            time_horizon=time_horizon,
            pulse_amplitude=pulse_amplitude,
            pulse_width=pulse_width,
            pulse_periods=pulse_periods,
            initial_state=bell_state
        )
        
        # Check entanglement preservation
        for state in results['state_evolution']:
            # Calculate reduced density matrix
            rho = np.outer(state, state.conj())
            # Trace out the second qubit to get the reduced density matrix for the first qubit
            reduced_rho = partial_trace(rho, keep_subsystem=0, dims=[2, 2])
            # Check that entropy is non-zero (indicating entanglement)
            entropy = von_neumann_entropy(reduced_rho)
            assert entropy > 0.0, "Entanglement was lost during evolution."

    def test_quantum_simulation_4d_entanglement(self):
        """Real-world 4D test for entanglement preservation using the entangling Hamiltonian."""
        state_a = np.array([1.0, 0.0], dtype=complex)
        state_b = np.array([0.0, 1.0], dtype=complex)
        bell_state = entangled_state(state_a, state_b)
        time_horizon = 2.0
        pulse_amplitude = 2.0
        pulse_width = 0.5
        pulse_periods = np.linspace(0.5, 5.0, 10)
        J = 1.0  # Coupling strength
        K = 0.5  # Local field strength
        results = run_quantum_simulation(
            time_horizon=time_horizon,
            pulse_amplitude=pulse_amplitude,
            pulse_width=pulse_width,
            pulse_periods=pulse_periods,
            initial_state=bell_state,
            J=J,
            K=K
        )
        for state in results['state_evolution']:
            rho = np.outer(state, state.conj())
            # Trace out the second qubit to get the reduced density matrix for the first qubit
            reduced_rho = partial_trace(rho, keep_subsystem=0, dims=[2, 2])
            entropy = von_neumann_entropy(reduced_rho)
            assert entropy > 0.0, "Entanglement was lost during evolution under the entangling Hamiltonian."

    def test_quantum_simulation_conservation(self, simple_hamiltonian, initial_state):
        """Test conservation of probability and energy"""
        time_horizon = 1.0
        pulse_amplitude = 1.0
        pulse_width = 0.5
        pulse_periods = np.linspace(0.5, 10.0, 5)
        
        results = run_quantum_simulation(
            time_horizon=time_horizon,
            pulse_amplitude=pulse_amplitude,
            pulse_width=pulse_width,
            pulse_periods=pulse_periods,
            initial_state=initial_state
        )
        
        # Check probability conservation
        for state in results['state_evolution']:
            prob = np.sum(np.abs(state)**2)
            assert np.isclose(prob, 1.0, atol=1e-10)
        
        # Check energy conservation (expectation value of Hamiltonian)
        initial_energy = np.real(np.vdot(initial_state, simple_hamiltonian @ initial_state))
        for state in results['state_evolution']:
            energy = np.real(np.vdot(state, simple_hamiltonian @ state))
            assert np.isclose(energy, initial_energy, atol=1e-10)

    def test_quantum_simulation_error_handling(self):
        """Test error handling in quantum simulation"""
        pulse_periods = np.linspace(0.5, 10.0, 5)
        # Test invalid time horizon
        with pytest.raises(ValueError):
            run_quantum_simulation(time_horizon=-1.0, pulse_amplitude=1.0, pulse_width=0.5, pulse_periods=pulse_periods)
        # Test invalid pulse parameters
        with pytest.raises(ValueError):
            run_quantum_simulation(time_horizon=1.0, pulse_amplitude=-1.0, pulse_width=0.5, pulse_periods=pulse_periods)
        # Test invalid initial state
        with pytest.raises(ValueError):
            run_quantum_simulation(time_horizon=1.0, pulse_amplitude=1.0, pulse_width=0.5, pulse_periods=pulse_periods, initial_state=np.array([0.0, 0.0]))

    def test_quantum_simulation_visualization(self, simple_hamiltonian, initial_state):
        """Test visualization capabilities of quantum simulation"""
        time_horizon = 1.0
        pulse_amplitude = 1.0
        pulse_width = 0.5
        pulse_periods = np.linspace(0.5, 10.0, 5)
        
        results = run_quantum_simulation(
            time_horizon=time_horizon,
            pulse_amplitude=pulse_amplitude,
            pulse_width=pulse_width,
            pulse_periods=pulse_periods,
            initial_state=initial_state,
            visualize=True
        )
        
        # Check visualization data
        assert 'visualization_data' in results
        assert 'state_plot' in results['visualization_data']
        assert 'entropy_plot' in results['visualization_data']
        
        # Check plot data structure
        state_plot = results['visualization_data']['state_plot']
        assert 'times' in state_plot
        assert 'states' in state_plot
        assert len(state_plot['times']) == len(state_plot['states']) 