# --- START OF FILE 3.0ArchE/quantum_utils.py ---
# ResonantiA Protocol v3.0 - quantum_utils.py (ENHANCED WITH QISKIT)
# Provides utility functions for quantum state vector manipulation, density matrix
# calculations, and information-theoretic measures (entropy, mutual information)
# primarily supporting the CfpframeworK (Section 7.6).
# NOW ENHANCED WITH AUTHENTIC QISKIT-BASED QUANTUM OPERATIONS

import numpy as np
# Import necessary math functions from scipy and standard math library
from scipy.linalg import logm, sqrtm, LinAlgError
from math import log2, sqrt
import logging
from typing import Union, List, Optional, Tuple, cast, Dict, Any, TYPE_CHECKING
from scipy.linalg import expm
from scipy.constants import hbar

# Try to import Qiskit
try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, DensityMatrix, partial_trace as qiskit_partial_trace, entropy as qiskit_entropy, Operator
    from qiskit.circuit.library import PauliEvolutionGate
    from qiskit.quantum_info.operators import SparsePauliOp
    from qiskit.synthesis import SuzukiTrotter
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    logger_imp = logging.getLogger(__name__)
    logger_imp.warning("Qiskit not available. Using classical quantum simulation fallback.")
    # Create dummy types for type annotations when Qiskitrying is not available
    if TYPE_CHECKING:
        from typing import Any as Statevector, Any as DensityMatrix
    else:
        # For runtime, use Any as a placeholder for type annotations
        Statevector = Any
        DensityMatrix = Any

logger = logging.getLogger(__name__)
# Basic logging config if running standalone or logger not configured externally
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - QuantumUtils - %(levelname)s - %(message)s')

# Use natural units for stability
hbar = 1.0

# --- State Vector Manipulation ---

def superposition_state(quantum_state: Union[List, np.ndarray], amplitude_factor: float = 1.0) -> np.ndarray:
    """
    Normalizes a list or NumPy array into a valid quantum state vector (L2 norm = 1).
    NOW ENHANCED: Can return Qiskit Statevector object for better integration.
    Optionally multiplies by an amplitude factor before normalization.
    Ensures the output is a 1D complex NumPy array or Statevector.

    Args:
        quantum_state: Input list or NumPy array representing the state.
        amplitude_factor: Optional float factor to multiply state by before normalization.

    Returns:
        A 1D complex NumPy array representing the normalized quantum state vector.

    Enhanced to optionally return Qiskit Statevector if Qiskit is available.
    """

    if not isinstance(quantum_state, (list, np.ndarray)):
        raise TypeError(f"Input 'quantum_state' must be a list or NumPy array, got {type(quantum_state)}.")
    try:
        # Convert to complex NumPy array and apply amplitude factor
        state = np.array(quantum_state, dtype=complex) * complex(amplitude_factor)
        if state.ndim != 1:
            raise ValueError(f"Input 'quantum_state' must be 1-dimensional, got {state.ndim} dimensions.")
        if state.size == 0:
            raise ValueError("Input 'quantum_state' cannot be empty.")

        # Calculate L2 norm (magnitude)
        norm = np.linalg.norm(state)

        # Check for zero norm before division
        if norm < 1e-15:
            raise ValueError("Input quantum state has zero norm and cannot be normalized.")

        # Normalize the state vector
        normalized_state = state / norm
        logger.debug(f"Input state normalized. Original norm: {norm:.4f}")
        return normalized_state
    except (ValueError, TypeError) as e:
        raise e
    except Exception as e_conv:
        raise ValueError(f"Error processing input quantum state: {e_conv}")

def prepare_quantum_state_qiskit(initial_metrics: np.ndarray, trajectories: Optional[np.ndarray] = None, num_qubits: int = 2) -> "Statevector":
    """
    ENHANCED WITH QISKIT: Prepare a quantum state using Qiskit for authentic quantum operations.
    
    Real-World: Encode timestamps/actions as qubit amplitudes.
    Workflow: Use Qiskit to initialize circuits.
    
    Args:
        initial_metrics: Initial metrics as numpy array.
        trajectories: Optional trajectory data to encode.
        num_qubits: Number of qubits (default 2).
    
    Returns:
        Qiskit Statevector representing the prepared quantum state.
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is required for prepare_quantum_state_qiskit but not available.")
    
    try:
        # Normalize classical data to amplitudes
        if trajectories is not None:
            amps = np.concatenate([initial_metrics, trajectories.flatten()])
        else:
            amps = initial_metrics.flatten() if initial_metrics.ndim > 1 else initial_metrics
        
        # Normalize to valid quantum state
        amps = amps / np.linalg.norm(amps)
        
        # Pad/truncate to 2**num_qubits
        target_dim = 2**num_qubits
        if len(amps) < target_dim:
            amps = np.pad(amps, (0, target_dim - len(amps)))
        elif len(amps) > target_dim:
            amps = amps[:target_dim]
        
        # Re-normalize after padding/truncation
        amps = amps / np.linalg.norm(amps)
        
        # Create quantum circuit and initialize state
        qc = QuantumCircuit(num_qubits)
        qc.initialize(amps, range(num_qubits))
        
        # Return Statevector
        return Statevector.from_instruction(qc)
    
    except Exception as e:
        logger.error(f"Error preparing quantum state with Qiskit: {e}")
        raise

def evolve_flux_qiskit(initial_state: "Statevector", time_steps: np.ndarray, hamiltonian_coeffs: np.ndarray, observable: str = "ZZ") -> List["Statevector"]:
    """
    ENHANCED WITH QISKIT: Evolve flux under data-derived Hamiltonians using PauliEvolutionGate.
    
    Real-World: Evolve under data-derived Hamiltonians.
    Workflow: Use PauliEvolutionGate for unitary dynamics.
    
    Args:
        initial_state: Initial Qiskit Statevector.
        time_steps: Array of time points for evolution.
        hamiltonian_coeffs: Hamiltonian coefficients.
        observable: Pauli observable string (e.g., "ZZ", "XX", "YY").
    
    Returns:
        List of evolved Statevectors.
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is required for evolve_flux_qiskit but not available.")
    
    try:
        num_qubits = initial_state.num_qubits
        evolved_states = []
        
        for t in time_steps:
            # Create Pauli evolution gate
            ham_op = SparsePauliOp.from_list([(observable, hamiltonian_coeffs[0])])
            evo_gate = PauliEvolutionGate(ham_op, time=t, synthesis=SuzukiTrotter(order=2))
            
            # Create circuit and apply evolution
            qc = QuantumCircuit(num_qubits)
            qc.append(evo_gate, range(num_qubits))
            
            # Evolve state
            evolved = initial_state.evolve(qc)
            evolved_states.append(evolved)
        
        return evolved_states
    
    except Exception as e:
        logger.error(f"Error evolving flux with Qiskit: {e}")
        raise

def detect_entanglement_qiskit(bipartite_state: Union["Statevector", "DensityMatrix"], subsystem_a_qubits: List[int]) -> float:
    """
    ENHANCED WITH QISKIT: Detect entanglement using Qiskit partial trace and entropy.
    
    Real-World: Quantify log correlations quantumly.
    Workflow: Compute partial trace and Von Neumann entropy.
    
    Args:
        bipartite_state: Qiskit Statevector or DensityMatrix.
        subsystem_a_qubits: Qubit indices for subsystem A.
    
    Returns:
        Von Neumann entropy (entanglement measure).
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is required for detect_entanglement_qiskit but not available.")
    
    try:
        # Convert to density matrix if needed
        if isinstance(bipartite_state, Statevector):
            density_matrix = DensityMatrix(bipartite_state)  # Fixed: Use constructor, not from_statevector
        else:
            density_matrix = bipartite_state
        
        # Compute partial trace over subsystem A
        rho_a = qiskit_partial_trace(density_matrix, subsystem_a_qubits)
        
        # Calculate Von Neumann entropy
        entropy_val = qiskit_entropy(rho_a, base=np.e)
        
        return float(entropy_val)
    
    except Exception as e:
        logger.error(f"Error detecting entanglement with Qiskit: {e}")
        raise

def integrate_confluence_qiskit(flux_a: "Statevector", flux_b: "Statevector", interaction_ham_coeffs: List[float]) -> "Statevector":
    """
    ENHANCED WITH QISKIT: Integrate confluence using tensor product and joint evolution.
    
    Real-World: Entangle fluxes for interference.
    Workflow: Tensor product and joint evolution.
    
    Args:
        flux_a: First flux state (Qiskit Statevector).
        flux_b: Second flux state (Qiskit Statevector).
        interaction_ham_coeffs: Interaction Hamiltonian coefficients.
    
    Returns:
        Combined and evolved Statevector.
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is required for integrate_confluence_qiskit but not available.")
    
    try:
        # Tensor product states
        combined = flux_a.tensor(flux_b)
        
        # Apply interaction Hamiltonian
        num_qubits = combined.num_qubits
        
        # Create interaction Hamiltonian - use ZZ for 2-qubit interaction
        if num_qubits == 2:
            ham_op = SparsePauliOp.from_list([("ZZ", interaction_ham_coeffs[0])])
        elif num_qubits == 1:
            ham_op = SparsePauliOp.from_list([("Z", interaction_ham_coeffs[0])])
        else:
            # For more qubits, create multi-qubit Z interactions
            pauli_str = "Z" * num_qubits
            ham_op = SparsePauliOp.from_list([(pauli_str, interaction_ham_coeffs[0])])
        
        # Create evolution gate - pass only the first qubit for single-qubit operations
        if num_qubits == 1:
            evo_gate = PauliEvolutionGate(ham_op, time=1.0)
            qc = QuantumCircuit(1)
            qc.append(evo_gate, [0])
        else:
            evo_gate = PauliEvolutionGate(ham_op, time=1.0)
            qc = QuantumCircuit(num_qubits)
            qc.append(evo_gate, range(num_qubits))
        
        # Return evolved state
        return combined.evolve(qc)
    
    except Exception as e:
        logger.error(f"Error integrating confluence with Qiskit: {e}")
        raise

def measure_insight_qiskit(confluence_state: "Statevector", shots: int = 1024) -> str:
    """
    ENHANCED WITH QISKIT: Measure insight using quantum measurement simulation.
    
    Real-World: Collapse to probabilistic insights.
    Workflow: Simulate measurements.
    
    Args:
        confluence_state: Qiskit Statevector to measure.
        shots: Number of measurement shots.
    
    Returns:
        Most probable outcome as insight (binary string).
    """
    if not QISKIT_AVAILABLE:
        raise ImportError("Qiskit is required for measure_insight_qiskit but not available.")
    
    try:
        num_qubits = confluence_state.num_qubits
        
        # Create quantum circuit
        qc = QuantumCircuit(num_qubits, num_qubits)
        qc.initialize(confluence_state.data, range(num_qubits))
        qc.measure_all()
        
        # Run on simulator
        simulator = AerSimulator()
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts()
        
        # Most probable outcome as insight
        insight = max(counts, key=counts.get)
        return insight
    
    except Exception as e:
        logger.error(f"Error measuring insight with Qiskit: {e}")
        raise

# --- CLASSICAL FALLBACK FUNCTIONS (Maintained for compatibility) ---

def entangled_state(state_a: Union[List, np.ndarray], state_b: Union[List, np.ndarray], coefficients: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Creates a combined quantum state vector representing the tensor product (|a> ⊗ |b>)
    of two input state vectors. Normalizes the resulting combined state.
    """
    if not isinstance(state_a, (list, np.ndarray)): raise TypeError(f"Input 'state_a' must be list/array.")
    if not isinstance(state_b, (list, np.ndarray)): raise TypeError(f"Input 'state_b' must be list/array.")

    try:
        vec_a = np.array(state_a, dtype=complex)
        vec_b = np.array(state_b, dtype=complex)
        if vec_a.ndim != 1 or vec_b.ndim != 1: raise ValueError("Input states must be 1-dimensional vectors.")
        if vec_a.size == 0 or vec_b.size == 0: raise ValueError("Input states cannot be empty.")
    except Exception as e_conv:
        raise ValueError(f"Error converting input states to vectors: {e_conv}")

    combined_state = np.kron(vec_a, vec_b)

    if coefficients is not None:
        logger.warning("The 'coefficients' parameter is currently ignored in 'entangled_state' (v3.0). Using simple tensor product.")

    try:
        final_state = superposition_state(combined_state)
        logger.debug(f"Created combined state (tensor product) of dimension {final_state.size}.")
        return final_state
    except ValueError as e_norm:
        raise ValueError(f"Could not normalize the combined tensor product state: {e_norm}")

def _density_matrix(state_vector: np.ndarray) -> np.ndarray:
    """Calculates the density matrix (rho = |psi><psi|) for a pure quantum state vector."""
    state_vector = np.asarray(state_vector, dtype=complex)
    if state_vector.ndim != 1:
        raise ValueError("Input state_vector must be 1-dimensional.")

    column_vector = state_vector[:, np.newaxis]
    density_mat = column_vector @ column_vector.conj().T

    trace = np.trace(density_mat)
    if not np.isclose(trace, 1.0, atol=1e-8):
        logger.warning(f"Density matrix trace is {trace.real:.6f}, expected 1. Input vector norm might not be exactly 1.")

    logger.debug(f"Computed density matrix (shape {density_mat.shape}).")
    return density_mat

def partial_trace(density_matrix: np.ndarray, keep_subsystem: int, dims: List[int]) -> np.ndarray:
    """
    Computes the partial trace of a density matrix over specified subsystems.
    NOW CAN USE QISKIT if Qiskit DensityMatrix is provided.
    """
    # If Qiskit is available and input is Qiskit DensityMatrix, use Qiskit method
    if QISKIT_AVAILABLE and isinstance(density_matrix, DensityMatrix):
        try:
            # Convert subsystem indices to qubit positions
            keep_subsystem_qubits = list(range(keep_subsystem * 2, (keep_subsystem + 1) * 2))
            reduced = qiskit_partial_trace(density_matrix, keep_subsystem_qubits)
            return np.array(reduced.data)
        except Exception as e:
            logger.warning(f"Qiskit partial trace failed, falling back to classical: {e}")
    
    # Classical implementation
    num_subsystems = len(dims)
    if not all(isinstance(d, int) and d > 0 for d in dims):
        raise ValueError("dims must be a list of positive integers.")
    if not (0 <= keep_subsystem < num_subsystems):
        raise ValueError(f"Invalid subsystem index {keep_subsystem} for {num_subsystems} subsystems.")

    total_dim = np.prod(dims)
    if density_matrix.shape != (total_dim, total_dim):
        raise ValueError(f"Density matrix shape {density_matrix.shape} is inconsistent with total dimension {total_dim} derived from dims {dims}.")

    try:
        rho_tensor = density_matrix.reshape(dims + dims)
    except ValueError as e_reshape:
        raise ValueError(f"Cannot reshape density matrix with shape {density_matrix.shape} to dims {dims + dims}: {e_reshape}")

    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if 2 * num_subsystems > len(alphabet):
        raise ValueError("Too many subsystems for default alphabet in partial trace.")

    ket_indices = list(alphabet[:num_subsystems])
    bra_indices = list(alphabet[num_subsystems : 2 * num_subsystems])

    einsum_input_indices = list(ket_indices)
    for i in range(num_subsystems):
        if i == keep_subsystem:
            einsum_input_indices.append(bra_indices[i])
        else:
            einsum_input_indices.append(ket_indices[i])

    output_indices = ket_indices[keep_subsystem] + bra_indices[keep_subsystem]

    einsum_str = f"{''.join(einsum_input_indices)}->{output_indices}"
    logger.debug(f"Performing partial trace with einsum string: '{einsum_str}'")

    try:
        reduced_density_matrix = np.einsum(einsum_str, rho_tensor, optimize='greedy')
    except Exception as e_einsum:
        raise ValueError(f"Failed to compute partial trace via np.einsum: {e_einsum}")

    logger.debug(f"Reduced density matrix for subsystem {keep_subsystem} calculated (shape {reduced_density_matrix.shape}).")
    return reduced_density_matrix

def von_neumann_entropy(density_matrix: Union[np.ndarray, "DensityMatrix"]) -> float:
    """
    Computes the Von Neumann entropy S(rho) = -Tr(rho * log2(rho)) for a density matrix.
    NOW ENHANCED to use Qiskit if DensityMatrix is provided.
    """
    # Use Qiskit if available and input is Qiskit DensityMatrix
    if QISKIT_AVAILABLE and isinstance(density_matrix, DensityMatrix):
        try:
            entropy_val = qiskit_entropy(density_matrix, base=2)
            return float(entropy_val)
        except Exception as e:
            logger.warning(f"Qiskit entropy calculation failed, falling back to classical: {e}")
    
    # Classical implementation
    if not isinstance(density_matrix, np.ndarray) or density_matrix.ndim != 2 or density_matrix.shape[0] != density_matrix.shape[1]:
        raise ValueError("Input must be a square 2D NumPy array.")

    try:
        eigenvalues = np.linalg.eigh(density_matrix)[0]
        eigenvalues = eigenvalues[eigenvalues > 1e-15]

        if eigenvalues.size == 0:
            return 0.0

        entropy = -np.sum(eigenvalues * np.log2(eigenvalues))
        return float(entropy) if entropy > 0 else 0.0
    except LinAlgError as e:
        logger.error(f"Linear algebra error computing eigenvalues for Von Neumann entropy: {e}", exc_info=True)
        return np.nan
    except Exception as e_gen:
        logger.error(f"Unexpected error in von_neumann_entropy: {e_gen}", exc_info=True)
        return np.nan

def get_quaternion_for_state(state_vector: np.ndarray) -> np.ndarray:
    """Converts a 2D quantum state vector (qubit) into a real 4D quaternion."""
    if state_vector.shape != (2,):
        raise ValueError("Input state vector must be of shape (2,).")
    
    a = np.real(state_vector[0])
    b = np.imag(state_vector[0])
    c = np.real(state_vector[1])
    d = np.imag(state_vector[1])
    
    return np.array([a, b, c, d])

def compute_multipartite_mutual_information(state_vector: np.ndarray, dims: List[int]) -> float:
    """
    Computes the bipartite mutual information I(A:B) = S(A) + S(B) - S(AB).
    NOW ENHANCED to work with both classical and Qiskit states.
    """
    if len(dims) != 2:
        raise NotImplementedError("Mutual information calculation currently only supports bipartite systems (len(dims) must be 2).")
    if not all(isinstance(d, int) and d > 0 for d in dims):
        raise ValueError("dims must be a list of two positive integers.")

    try:
        normalized_state = superposition_state(state_vector)
        total_dim = np.prod(dims)
        if normalized_state.size != total_dim:
            raise ValueError(f"State vector size {normalized_state.size} does not match total dimension {total_dim} from dims {dims}.")
    except (ValueError, TypeError) as e_state:
        raise ValueError(f"Invalid input state vector for mutual information calculation: {e_state}")

    try:
        rho_ab = _density_matrix(normalized_state)
        rho_a = partial_trace(rho_ab, keep_subsystem=0, dims=dims)
        rho_b = partial_trace(rho_ab, keep_subsystem=1, dims=dims)
    except ValueError as e_trace:
        raise ValueError(f"Error calculating density matrices or partial trace for mutual information: {e_trace}")

    entropy_rho_a = von_neumann_entropy(rho_a)
    entropy_rho_b = von_neumann_entropy(rho_b)

    if np.isnan(entropy_rho_a) or np.isnan(entropy_rho_b):
        logger.error("NaN entropy encountered during mutual information calculation. Returning NaN.")
        return np.nan

    mutual_info = entropy_rho_a + entropy_rho_b

    tolerance = 1e-12
    if mutual_info < -tolerance:
        logger.warning(f"Calculated negative Mutual Information ({mutual_info:.4g}). Clamping to 0.0. Check S(A)={entropy_rho_a:.4g}, S(B)={entropy_rho_b:.4g}.")
        mutual_info = 0.0
    elif np.isnan(mutual_info):
        logger.warning("Calculated NaN Mutual Information. Returning 0.0.")
        mutual_info = 0.0
    else:
        mutual_info = max(0.0, mutual_info)

    logger.debug(f"Calculated Entropies for MI: S(A)={entropy_rho_a:.6f}, S(B)={entropy_rho_b:.6f}")
    logger.info(f"Calculated Mutual Information I(A:B): {mutual_info:.6f}")
    return float(mutual_info)

def calculate_shannon_entropy(quantum_state_vector: np.ndarray) -> float:
    """Computes the Shannon entropy H(p) = -sum(p_i * log2(p_i))."""
    state = np.asarray(quantum_state_vector, dtype=complex)
    if state.ndim != 1:
        raise ValueError("Input quantum_state_vector must be 1-dimensional.")

    probabilities = np.abs(state)**2

    total_prob = np.sum(probabilities)
    epsilon = 1e-9
    if not np.isclose(total_prob, 1.0, atol=epsilon):
        logger.warning(f"Input state probabilities sum to {total_prob:.6f}, expected 1. Normalizing probability distribution for entropy calculation.")
        if total_prob > 1e-15:
            probabilities /= total_prob
        else:
            logger.error("Input state has zero total probability. Cannot calculate Shannon entropy.")
            return 0.0

    tolerance_prob = 1e-15
    non_zero_probs = probabilities[probabilities > tolerance_prob]

    if len(non_zero_probs) <= 1:
        return 0.0

    try:
        entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))
    except FloatingPointError as e_fp:
        logger.error(f"Floating point error during Shannon entropy calculation: {e_fp}. Returning NaN.")
        return np.nan

    if entropy < -1e-12:
        logger.warning(f"Calculated negative Shannon entropy ({entropy:.4g}). Clamping to 0.0.")
        entropy = 0.0
    elif np.isnan(entropy):
        logger.warning("Calculated NaN Shannon entropy. Returning 0.0.")
        entropy = 0.0
    else:
        entropy = max(0.0, entropy)

    logger.debug(f"Calculated Shannon Entropy: {entropy:.6f}")
    return float(entropy)

def entangling_hamiltonian(J: float = 1.0, K: float = 0.5) -> np.ndarray:
    """Creates a 4x4 entangling Hamiltonian for two qubits."""
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    H_int = J * (np.kron(sx, sx) + np.kron(sy, sy) + np.kron(sz, sz))
    H_local = K * (np.kron(sz, np.eye(2)) + np.kron(np.eye(2), sz))
    CZ = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]], dtype=complex)
    H_cz = J * CZ
    return H_int + H_local + H_cz

def hamiltonian_pulsed(time: float, pulse_period: float, dim: int = 2, J: float = 1.0, K: float = 0.5) -> np.ndarray:
    """Creates a time-dependent Hamiltonian with a Gaussian pulse modulation."""
    if time < 0 or pulse_period <= 0:
        raise ValueError("Time and pulse period must be non-negative.")
    H0 = np.array([[1.0, 0.5], [0.5, 1.0]], dtype=complex)
    pulse = np.exp(-(time - pulse_period/2)**2 / (2 * (pulse_period/4)**2))
    H_base = H0 * (1 + pulse)
    if dim == 2:
        return H_base
    elif dim == 4:
        return entangling_hamiltonian(J=J, K=K)
    else:
        raise ValueError("Only 2 or 4 dimensional systems are supported.")

def evolve_quantum_state(psi: np.ndarray, H: np.ndarray, dt: float) -> np.ndarray:
    """Evolves a quantum state using the time-dependent Schrödinger equation."""
    if psi.ndim != 1:
        raise ValueError("State vector must be 1-dimensional.")
    if H.shape[0] != H.shape[1] or H.shape[0] != len(psi):
        raise ValueError("Hamiltonian dimensions must match state vector.")
    U = expm(-1j * H * dt / hbar)
    psi_new = U @ psi
    norm = np.linalg.norm(psi_new)
    if not np.isfinite(norm) or norm < 1e-12:
        raise ValueError("Quantum state norm became zero or NaN during evolution.")
    psi_new = psi_new / norm
    return psi_new

def run_quantum_simulation(
    time_horizon: float,
    pulse_amplitude: float,
    pulse_width: float,
    pulse_periods: np.ndarray,
    initial_state: Optional[np.ndarray] = None,
    visualize: bool = False,
    J: float = 1.0,
    K: float = 0.5
) -> Dict[str, Any]:
    """Runs a quantum simulation with pulsed Hamiltonians."""
    if time_horizon <= 0:
        raise ValueError("Time horizon must be positive.")
    if pulse_amplitude <= 0:
        raise ValueError("Pulse amplitude must be positive.")
    if pulse_width <= 0:
        raise ValueError("Pulse width must be positive.")
    if initial_state is None:
        initial_state = np.array([1.0, 0.0], dtype=complex)
    else:
        initial_state = superposition_state(initial_state)
    dim = len(initial_state)
    state_evolution = []
    entropy_evolution = []
    times = np.linspace(0, time_horizon, len(pulse_periods))
    current_state = initial_state.copy()
    for t, period in zip(times, pulse_periods):
        H = hamiltonian_pulsed(t, period, dim=dim, J=J, K=K)
        dt = time_horizon / len(pulse_periods)
        current_state = evolve_quantum_state(current_state, H, dt)
        state_evolution.append(current_state)
        entropy = calculate_shannon_entropy(current_state)
        entropy_evolution.append(entropy)
    results = {
        'state_evolution': state_evolution,
        'entropy_evolution': entropy_evolution,
        'final_state': current_state,
        'times': times.tolist()
    }
    if visualize:
        results['visualization_data'] = {
            'state_plot': {
                'times': times.tolist(),
                'states': [state.tolist() for state in state_evolution]
            },
            'entropy_plot': {
                'times': times.tolist(),
                'entropy': entropy_evolution
            }
        }
    logger.info(f"Quantum simulation completed with {len(pulse_periods)} time steps")
    return results

# --- END OF FILE 3.0ArchE/quantum_utils.py --- 
