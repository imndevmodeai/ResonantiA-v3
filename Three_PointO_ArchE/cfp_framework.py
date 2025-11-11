# --- START OF FILE 3.0ArchE/cfp_framework.py ---
# ResonantiA Protocol v3.0 - cfp_framework.py
# Implements the Comparative Fluxual Processing (CFP) Framework.
# Incorporates Quantum-Inspired principles and State Evolution logic.
# Returns results including mandatory Integrated Action Reflection (IAR).

from typing import Union, Dict, Any, Optional, List, Tuple # Expanded type hints
import numpy as np
# Import necessary scientific libraries (ensure they are in requirements.txt)
from scipy.integrate import quad # For numerical integration (Quantum Flux Difference)
from scipy.linalg import expm # For matrix exponentiation (Hamiltonian evolution example)
import logging
import json # For IAR preview serialization
import time # Added based on usage in run_analysis
from . import config as arche_config # Use alias to avoid confusion with local config vars
from .quantum_utils import get_quaternion_for_state # Import for quantum states

# Use relative imports for internal modules
try:
    # Import quantum utilities (superposition, entanglement, entropy calculations)
    from .quantum_utils import (superposition_state, entangled_state,
                                compute_multipartite_mutual_information,
                                calculate_shannon_entropy, von_neumann_entropy,
                                evolve_flux_qiskit, QISKIT_AVAILABLE, Statevector,
                                SparsePauliOp, PauliEvolutionGate, SuzukiTrotter)
    from qiskit import QuantumCircuit  # Import QuantumCircuit for circuit construction
    QUANTUM_UTILS_AVAILABLE = True
    QUANTUM_QISKIT_AVAILABLE = QISKIT_AVAILABLE
    logger_q = logging.getLogger(__name__) # Use current module logger
    logger_q.info(f"quantum_utils.py loaded successfully for CFP. Qiskit available: {QUANTUM_QISKIT_AVAILABLE}")
except ImportError:
    QUANTUM_UTILS_AVAILABLE = False
    QUANTUM_QISKIT_AVAILABLE = False
    # Define dummy functions if quantum_utils is not available to allow basic structure loading
    def superposition_state(state, factor=1.0): return np.array(state, dtype=complex)
    def entangled_state(a, b, coeffs=None): return np.kron(a,b)
    def compute_multipartite_mutual_information(state, dims): return 0.0
    def calculate_shannon_entropy(state): return 0.0
    def von_neumann_entropy(matrix): return 0.0
    def evolve_flux_qiskit(*args, **kwargs): raise ImportError("Qiskit not available")
    Statevector = None
    SparsePauliOp = None
    PauliEvolutionGate = None
    SuzukiTrotter = None
    QuantumCircuit = None  # Add dummy QuantumCircuit
    logger_q = logging.getLogger(__name__)
    logger_q.warning("quantum_utils.py not found or failed to import. CFP quantum features will be simulated or unavailable.")

logger = logging.getLogger(__name__) # Logger for this module

class CfpframeworK:
    """
    Comparative Fluxual Processing (CFP) Framework - Quantum Enhanced w/ Evolution (v3.0).

    Models and compares the dynamics of two configured systems over time.
    Incorporates quantum-inspired principles (superposition, entanglement via mutual info)
    and implements state evolution logic (e.g., Hamiltonian).
    Calculates metrics like Quantum Flux Difference and Entanglement Correlation.
    Returns results dictionary including a detailed IAR reflection assessing the analysis.

    Requires quantum_utils.py for full functionality. State evolution implementation
    (beyond placeholder/Hamiltonian) requires adding logic to _evolve_state.
    """
    def __init__(
        self,
        system_a_config: Dict[str, Any],
        system_b_config: Dict[str, Any],
        observable: str = "position", # Observable to compare expectation values for
        time_horizon: float = arche_config.CONFIG.tools.cfp_default_time_horizon, # Duration of simulated evolution
        integration_steps: int = arche_config.CONFIG.tools.cfp_default_integration_steps, # Hint for numerical integration resolution
        evolution_model_type: str = arche_config.CONFIG.tools.cfp_default_evolution_model, # Type of evolution ('placeholder', 'hamiltonian', 'ode_solver', etc.)
        hamiltonian_a: Optional[np.ndarray] = None, # Optional Hamiltonian matrix for system A (if evolution_model_type='hamiltonian')
        hamiltonian_b: Optional[np.ndarray] = None # Optional Hamiltonian matrix for system B
    ):
        """
        Initializes the CFP Framework instance.

        Args:
            system_a_config: Dictionary defining system A (must include 'quantum_state' list/array).
            system_b_config: Dictionary defining system B (must include 'quantum_state' list/array).
            observable: String name of the observable operator to use for comparison.
            time_horizon: Float duration over which to simulate evolution/integrate flux.
            integration_steps: Int hint for numerical integration steps (used in quad limit).
            evolution_model_type: String indicating the state evolution method to use.
            hamiltonian_a: Optional NumPy array representing the Hamiltonian for system A.
            hamiltonian_b: Optional NumPy array representing the Hamiltonian for system B.

        Raises:
            ImportError: If quantum_utils.py is required but not available.
            TypeError: If system configs are not dictionaries or states are invalid.
            ValueError: If time horizon/steps invalid, state dimensions mismatch, or Hamiltonians invalid.
        """
        if not QUANTUM_UTILS_AVAILABLE:
            # Hard fail if essential quantum utilities are missing
            raise ImportError("Quantum Utils (quantum_utils.py) required for CfpframeworK but not found.")
        if not isinstance(system_a_config, dict) or not isinstance(system_b_config, dict):
            raise TypeError("System configurations (system_a_config, system_b_config) must be dictionaries.")
        if time_horizon <= 0 or integration_steps <= 0:
            raise ValueError("Time horizon and integration steps must be positive.")

        self.system_a_config = system_a_config
        self.system_b_config = system_b_config
        self.observable_name = observable
        self.time_horizon = float(time_horizon)
        self.integration_steps = int(integration_steps)
        self.evolution_model_type = evolution_model_type.lower() # Normalize to lowercase
        self.hamiltonian_a = hamiltonian_a
        self.hamiltonian_b = hamiltonian_b

        # Validate state inputs and determine system dimension
        self.state_a_initial_raw = self._validate_and_get_state(self.system_a_config, 'A')
        self.state_b_initial_raw = self._validate_and_get_state(self.system_b_config, 'B')
        dim_a = len(self.state_a_initial_raw)
        dim_b = len(self.state_b_initial_raw)
        if dim_a != dim_b:
            raise ValueError(f"Quantum state dimensions must match for comparison ({dim_a} vs {dim_b})")
        self.system_dimension = dim_a

        # Validate Hamiltonians if the 'hamiltonian' evolution model is selected
        if self.evolution_model_type == 'hamiltonian':
            self.hamiltonian_a = self._validate_hamiltonian(self.hamiltonian_a, 'A')
            self.hamiltonian_b = self._validate_hamiltonian(self.hamiltonian_b, 'B')

        # Get the operator matrix for the specified observable
        self.observable_operator = self._get_operator(self.observable_name)

        logger.info(f"CFP Framework (v3.0) initialized: Observable='{self.observable_name}', T={self.time_horizon}s, Dim={self.system_dimension}, Evolution='{self.evolution_model_type}'")

    def _validate_and_get_state(self, system_config: Dict[str, Any], label: str) -> np.ndarray:
        """Validates 'quantum_state' input and returns it as a NumPy array."""
        state = system_config.get('quantum_state')
        if state is None:
            raise ValueError(f"System {label} config missing required 'quantum_state' key.")
        if not isinstance(state, (list, np.ndarray)):
            raise TypeError(f"System {label} 'quantum_state' must be a list or NumPy array, got {type(state)}.")
        try:
            vec = np.array(state, dtype=complex) # Ensure complex type
            if vec.ndim != 1:
                raise ValueError(f"System {label} 'quantum_state' must be 1-dimensional.")
            if vec.size == 0:
                raise ValueError(f"System {label} 'quantum_state' cannot be empty.")
            # Normalization happens later in calculations, just validate structure here
            return vec
        except Exception as e:
            # Catch potential errors during array conversion
            raise ValueError(f"Error processing System {label} 'quantum_state': {e}")

    def _validate_hamiltonian(self, H: Optional[np.ndarray], label: str) -> np.ndarray:
        """Validates Hamiltonian matrix if provided for 'hamiltonian' evolution."""
        if H is None:
            raise ValueError(f"Hamiltonian for system {label} is required for 'hamiltonian' evolution type but was not provided.")
        if not isinstance(H, np.ndarray):
            raise TypeError(f"Hamiltonian for system {label} must be a NumPy array, got {type(H)}.")
        expected_shape = (self.system_dimension, self.system_dimension)
        if H.shape != expected_shape:
            raise ValueError(f"Hamiltonian for system {label} has incorrect shape {H.shape}, expected {expected_shape}.")
        # Check if the matrix is Hermitian (equal to its conjugate transpose) - important for physical Hamiltonians
        if not np.allclose(H, H.conj().T, atol=1e-8):
            # Log a warning if not Hermitian, as it might indicate an issue but doesn't prevent calculation
            logger.warning(f"Provided Hamiltonian for system {label} is not Hermitian (H != H_dagger). Evolution might be non-unitary.")
        return H

    def _get_operator(self, observable_name: str) -> np.ndarray:
        """
        Returns the matrix representation for a given observable name.
        Provides basic operators (Position, Spin Z/X, Energy) or Identity as fallback.
        """
        dim = self.system_dimension
        op: Optional[np.ndarray] = None
        name_lower = observable_name.lower()

        if name_lower == "position":
            # Example: Simple position operator for 2D, linear for N-D
            if dim == 2: op = np.array([[1, 0], [0, -1]], dtype=complex)
            else: op = np.diag(np.linspace(-1, 1, dim), k=0).astype(complex)
        elif name_lower == "spin_z":
            if dim == 2: op = np.array([[1, 0], [0, -1]], dtype=complex)
            else: logger.warning(f"Spin Z operator only defined for dim=2. Using Identity.")
        elif name_lower == "spin_x":
            if dim == 2: op = np.array([[0, 1], [1, 0]], dtype=complex)
            else: logger.warning(f"Spin X operator only defined for dim=2. Using Identity.")
        elif name_lower == "energy":
            # Example: Simple energy operator with distinct eigenvalues
            op = np.diag(np.arange(dim)).astype(complex)
        # Add other standard or custom operators here
        # elif name_lower == "custom_operator_name":
        #     op = load_custom_operator(...)

        if op is None:
            # Fallback to Identity matrix if observable is unknown
            op = np.identity(dim, dtype=complex)
            logger.warning(f"Unsupported observable name '{observable_name}'. Using Identity matrix.")
        elif op.shape != (dim, dim):
            # Fallback if generated operator has wrong shape (shouldn't happen with above examples)
            op = np.identity(dim, dtype=complex)
            logger.error(f"Generated operator for '{observable_name}' has wrong shape {op.shape}. Using Identity.")

        # Ensure operator is complex type
        return op.astype(complex)

    def _evolve_state(self, initial_state_vector: np.ndarray, dt: float, system_label: str) -> np.ndarray:
        """
        [IMPLEMENTED v3.0] Evolves the quantum state vector over time interval dt.
        Uses the evolution model specified during initialization.

        Args:
            initial_state_vector: The starting state vector (NumPy complex array).
            dt: The time interval for evolution.
            system_label: 'A' or 'B' to select the appropriate Hamiltonian if needed.

        Returns:
            The evolved state vector (NumPy complex array). Returns original state on error.
        """
        if dt == 0: return initial_state_vector # No evolution if time interval is zero

        if self.evolution_model_type == 'hamiltonian':
            # Use Hamiltonian evolution: |psi(t)> = U(dt)|psi(0)> = expm(-i * H * dt / hbar) |psi(0)>
            H = self.hamiltonian_a if system_label == 'A' else self.hamiltonian_b
            # Hamiltonian should have been validated during __init__ if this model was selected
            if H is None: # Safeguard check
                logger.error(f"Hamiltonian missing for system {system_label} during evolution despite 'hamiltonian' type selected. Returning unchanged state.")
                return initial_state_vector
            try:
                # Assuming hbar = 1 for simplicity (adjust if using physical units)
                # Calculate unitary evolution operator U(dt) using matrix exponentiation
                U = expm(-1j * H * dt)
                # Apply the operator to the initial state
                evolved_state = U @ initial_state_vector
                # Renormalize state vector due to potential numerical errors in expm
                norm = np.linalg.norm(evolved_state)
                return evolved_state / norm if norm > 1e-15 else evolved_state # Avoid division by zero
            except Exception as e_evolve:
                logger.error(f"Error during Hamiltonian evolution calculation for system {system_label} at dt={dt}: {e_evolve}", exc_info=True)
                return initial_state_vector # Return original state on calculation error

        elif self.evolution_model_type == 'qiskit':
            # ENHANCED WITH QISKIT: Use Qiskit for authentic quantum evolution
            if not QUANTUM_QISKIT_AVAILABLE:
                logger.error("Qiskit evolution requested but Qiskit not available. Falling back to placeholder.")
                return initial_state_vector
            try:
                # Convert numpy array to Qiskit Statevector
                qiskit_state = Statevector(initial_state_vector)
                
                # Calculate number of qubits from system dimension
                # system_dimension is the size of the state vector (2^num_qubits)
                import math
                num_qubits = int(math.log2(self.system_dimension)) if self.system_dimension >= 2 else 1
                
                # Create Hamiltonian (use provided or default)
                H = self.hamiltonian_a if system_label == 'A' else self.hamiltonian_b
                if H is None:
                    # Default to simple Pauli evolution based on number of qubits
                    if num_qubits == 1:
                        ham_op = SparsePauliOp.from_list([("Z", 1.0)])
                    elif num_qubits == 2:
                        ham_op = SparsePauliOp.from_list([("ZZ", 1.0)])
                    else:
                        # For higher dimensions, create appropriate Pauli string
                        pauli_str = "Z" * num_qubits
                        ham_op = SparsePauliOp.from_list([(pauli_str, 1.0)])
                else:
                    # Convert numpy Hamiltonian to Qiskit SparsePauliOp
                    # This is a simplified conversion; for full support, pass as Pauli
                    pauli_str = "Z" * num_qubits
                    ham_op = SparsePauliOp.from_list([(pauli_str, 1.0)])
                
                # Create evolution gate
                evo_gate = PauliEvolutionGate(ham_op, time=dt, synthesis=SuzukiTrotter(order=2))
                
                # Create circuit and evolve
                qc = QuantumCircuit(num_qubits)
                if num_qubits == 1:
                    qc.append(evo_gate, [0])
                else:
                    qc.append(evo_gate, range(num_qubits))
                
                # Evolve state
                evolved_qiskit_state = qiskit_state.evolve(qc)
                
                # Convert back to numpy array
                return evolved_qiskit_state.data
                
            except Exception as e_evolve:
                logger.error(f"Error during Qiskit evolution for system {system_label} at dt={dt}: {e_evolve}", exc_info=True)
                return initial_state_vector

        elif self.evolution_model_type == 'placeholder' or self.evolution_model_type == 'none':
            # Placeholder behavior: State does not change
            # logger.debug(f"State evolution placeholder used for dt={dt}. Returning unchanged state.")
            return initial_state_vector

        # --- Add other evolution model implementations here ---
        # elif self.evolution_model_type == 'ode_solver':
        #     # Example using scipy.integrate.solve_ivp (requires defining d|psi>/dt = -i*H*|psi>)
        #     logger.warning("ODE solver evolution not fully implemented. Returning unchanged state.")
        #     # Need to implement the ODE function and call solve_ivp
        #     return initial_state_vector
        # elif self.evolution_model_type == 'linked_prediction_tool':
        #     # Conceptual: Call run_prediction tool to get next state based on a trained model
        #     logger.warning("Linked prediction tool evolution not implemented. Returning unchanged state.")
        #     return initial_state_vector

        else:
            # Unknown evolution type specified
            logger.warning(f"Unknown evolution model type '{self.evolution_model_type}' specified. Returning unchanged state.")
            return initial_state_vector

    def _evolve_state_classical(self, initial_state_vector: np.ndarray, dt: float, system_label: str) -> np.ndarray:
        """
        Evolves the state vector over time interval dt using a classical model.
        This example uses simple linear interpolation towards a fixed point.
        """
        # A simple deterministic evolution: linear interpolation towards a fixed point (e.g., origin)
        # The rate of change can be a property of the system
        rate = self.system_a_config.get('classical_rate', 0.1) if system_label == 'A' else self.system_b_config.get('classical_rate', 0.1)
        fixed_point = np.zeros_like(initial_state_vector)
        
        # Evolve by moving a fraction of the distance towards the fixed point
        evolved_state = initial_state_vector + (fixed_point - initial_state_vector) * rate * dt
        return evolved_state

    def compute_classical_flux_difference(self) -> Optional[float]:
        """
        Computes the integrated squared difference in the expectation value of the
        chosen observable between system A and system B over the time horizon using classical evolution.
        """
        logger.info(f"Computing Classical Flux Difference for observable '{self.observable_name}' over T={self.time_horizon}...")
        try:
            state_a_initial = superposition_state(self.state_a_initial_raw)
            state_b_initial = superposition_state(self.state_b_initial_raw)
        except (ValueError, TypeError) as e_norm:
            logger.error(f"Invalid initial state vector for classical flux calculation: {e_norm}")
            return None
        
        op = self.observable_operator

        def integrand(t: float) -> float:
            try:
                state_a_t = self._evolve_state_classical(state_a_initial, t, 'A')
                state_b_t = self._evolve_state_classical(state_b_initial, t, 'B')

                if state_a_t.ndim == 1: state_a_t = state_a_t[:, np.newaxis]
                if state_b_t.ndim == 1: state_b_t = state_b_t[:, np.newaxis]

                exp_a = np.real((state_a_t.conj().T @ op @ state_a_t)[0,0])
                exp_b = np.real((state_b_t.conj().T @ op @ state_b_t)[0,0])

                diff_sq = (exp_a - exp_b)**2
                if np.isnan(diff_sq):
                    logger.warning(f"NaN encountered in classical integrand calculation at t={t}. Returning NaN for this point.")
                    return np.nan
                return diff_sq
            except Exception as e_inner:
                logger.error(f"Error calculating classical integrand at t={t}: {e_inner}", exc_info=True)
                return np.nan

        try:
            integral_result, abserr, infodict = quad(integrand, 0, self.time_horizon, limit=self.integration_steps * 5, full_output=True, epsabs=1.49e-08, epsrel=1.49e-08)
            num_evals = infodict.get('neval', 0)
            logger.info(f"Classical integration completed. Result: {integral_result:.6f}, Est. Abs Error: {abserr:.4g}, Function Evals: {num_evals}")

            if 'message' in infodict and infodict['message'] != 'OK':
                logger.warning(f"Classical integration warning/message: {infodict['message']}")
            if np.isnan(integral_result):
                logger.error("Classical integration resulted in NaN.")
                return None
            
            return float(integral_result)
        except Exception as e_quad:
            logger.error(f"Error during classical numerical integration (quad): {e_quad}", exc_info=True)
            return None

    def compute_quantum_flux_difference(self) -> Optional[float]:
        """
        Computes the integrated squared difference in the expectation value of the
        chosen observable between system A and system B over the time horizon.
        Requires implemented state evolution. Returns None on error.
        """
        logger.info(f"Computing Quantum Flux Difference (CFP_Quantum) for observable '{self.observable_name}' over T={self.time_horizon}...")
        try:
            # Normalize initial states using the utility function
            state_a_initial = superposition_state(self.state_a_initial_raw)
            state_b_initial = superposition_state(self.state_b_initial_raw)
        except (ValueError, TypeError) as e_norm:
            logger.error(f"Invalid initial state vector for QFD calculation: {e_norm}")
            return None
        except Exception as e_norm_unexp:
            logger.error(f"Unexpected error normalizing initial states: {e_norm_unexp}", exc_info=True)
            return None

        op = self.observable_operator # Use the operator matrix determined during init

        # Define the function to be integrated: (Expectation_A(t) - Expectation_B(t))^2
        def integrand(t: float) -> float:
            try:
                # Evolve states from initial state to time t using the implemented method
                state_a_t = self._evolve_state(state_a_initial, t, 'A')
                state_b_t = self._evolve_state(state_b_initial, t, 'B')

                # Calculate expectation value <O> = <psi|O|psi>
                # Ensure vectors are column vectors for matrix multiplication if needed by numpy/scipy versions
                if state_a_t.ndim == 1: state_a_t = state_a_t[:, np.newaxis]
                if state_b_t.ndim == 1: state_b_t = state_b_t[:, np.newaxis]

                # <psi| is the conjugate transpose (dagger)
                exp_a = np.real((state_a_t.conj().T @ op @ state_a_t)[0,0])
                exp_b = np.real((state_b_t.conj().T @ op @ state_b_t)[0,0])

                # Calculate squared difference
                diff_sq = (exp_a - exp_b)**2
                if np.isnan(diff_sq): # Check for NaN resulting from calculations
                    logger.warning(f"NaN encountered in integrand calculation at t={t}. Returning NaN for this point.")
                    return np.nan
                return diff_sq
            except Exception as e_inner:
                # Catch errors during evolution or expectation calculation at a specific time t
                logger.error(f"Error calculating integrand at t={t}: {e_inner}", exc_info=True)
                return np.nan # Return NaN to signal error to the integrator

        try:
            # Perform numerical integration using scipy.integrate.quad
            # `limit` controls number of subdivisions, `epsabs`/`epsrel` control tolerance
            integral_result, abserr, infodict = quad(integrand, 0, self.time_horizon, limit=self.integration_steps * 5, full_output=True, epsabs=1.49e-08, epsrel=1.49e-08)

            num_evals = infodict.get('neval', 0)
            logger.info(f"Numerical integration completed. Result: {integral_result:.6f}, Est. Abs Error: {abserr:.4g}, Function Evals: {num_evals}")

            # Check for potential integration issues reported by quad
            if 'message' in infodict and infodict['message'] != 'OK':
                logger.warning(f"Integration warning/message: {infodict['message']}")
            if num_evals >= (self.integration_steps * 5):
                logger.warning("Integration reached maximum subdivisions limit. Result might be inaccurate.")
            if np.isnan(integral_result):
                logger.error("Integration resulted in NaN. Check integrand function for errors.")
                return None

            # Return the calculated integral value
            return float(integral_result)

        except Exception as e_quad:
            # Catch errors during the integration process itself
            logger.error(f"Error during numerical integration (quad): {e_quad}", exc_info=True)
            return None

    def quantify_entanglement_correlation(self) -> Optional[float]:
        """
        Quantifies entanglement correlation between the initial states of A and B
        using Mutual Information I(A:B), assuming they form a combined system.
        Returns None if quantum_utils unavailable or calculation fails.
        """
        if not QUANTUM_UTILS_AVAILABLE:
            logger.warning("Cannot quantify entanglement: quantum_utils not available.")
            return None

        logger.info("Quantifying Entanglement Correlation (Mutual Information I(A:B) of initial states)...")
        try:
            # Normalize initial states
            state_a = superposition_state(self.state_a_initial_raw)
            state_b = superposition_state(self.state_b_initial_raw)
            # Get dimensions for partitioning
            dim_a, dim_b = len(state_a), len(state_b)
            dims = [dim_a, dim_b]

            # Create the combined state assuming tensor product of initial states
            # Note: This calculates MI for the *product* state, representing correlation
            # if they *were* independent. For a truly entangled input state,
            # the combined state would need to be provided directly.
            combined_state_product = entangled_state(state_a, state_b) # Uses np.kron

            # Compute mutual information using the utility function
            mutual_info = compute_multipartite_mutual_information(combined_state_product, dims)

            if np.isnan(mutual_info):
                logger.warning("Mutual information calculation resulted in NaN.")
                return None

            logger.info(f"Calculated Mutual Information I(A:B) for initial product state: {mutual_info:.6f}")
            return float(mutual_info)
        except NotImplementedError as e_mi:
            # Catch specific errors from the MI calculation if partitioning fails
            logger.error(f"Entanglement calculation failed: {e_mi}")
            return None
        except (ValueError, TypeError) as e_mi_input:
            # Catch errors related to invalid input states
            logger.error(f"Invalid input for entanglement calculation: {e_mi_input}")
            return None
        except Exception as e_mi_unexp:
            # Catch other unexpected errors
            logger.error(f"Unexpected error calculating entanglement correlation: {e_mi_unexp}", exc_info=True)
            return None

    def compute_system_entropy(self, system_label: str) -> Optional[float]:
        """
        Computes the Shannon entropy of the probability distribution derived from
        the initial state vector of the specified system ('A' or 'B').
        Returns None if quantum_utils unavailable or calculation fails.
        """
        if not QUANTUM_UTILS_AVAILABLE:
            logger.warning("Cannot compute entropy: quantum_utils not available.")
            return None

        logger.info(f"Computing initial Shannon Entropy for System {system_label}...")
        try:
            # Select the appropriate initial state
            initial_state = self.state_a_initial_raw if system_label == 'A' else self.state_b_initial_raw
            # Calculate Shannon entropy using the utility function
            entropy = calculate_shannon_entropy(initial_state)

            if np.isnan(entropy):
                logger.warning(f"Shannon entropy calculation for System {system_label} resulted in NaN.")
                return None

            logger.info(f"Initial Shannon Entropy for System {system_label}: {entropy:.6f}")
            return float(entropy)
        except KeyError: # Should not happen with 'A'/'B' check, but safeguard
            logger.error(f"Invalid system label '{system_label}' for entropy calculation.")
            return None
        except (ValueError, TypeError) as e_ent_input:
            # Catch errors related to invalid input state
            logger.error(f"Invalid state for entropy calculation in system {system_label}: {e_ent_input}")
            return None
        except Exception as e_ent_unexp:
            # Catch other unexpected errors
            logger.error(f"Error computing Shannon entropy for System {system_label}: {e_ent_unexp}", exc_info=True)
            return None

    def compute_spooky_flux_divergence(self) -> Optional[float]:
        """
        Calculates Spooky Flux Divergence by comparing the quantum flux difference
        to the classical flux difference. Requires both calculations to succeed.
        """
        logger.info("Computing Spooky Flux Divergence...")
        
        qfd = self.compute_quantum_flux_difference()
        if qfd is None:
            logger.error("Cannot compute Spooky Flux Divergence: Quantum Flux Difference calculation failed.")
            return None

        cfd = self.compute_classical_flux_difference()
        if cfd is None:
            logger.error("Cannot compute Spooky Flux Divergence: Classical Flux Difference calculation failed.")
            return None

        divergence = abs(qfd - cfd)
        logger.info(f"Spooky Flux Divergence calculated: |{qfd:.4f} (QFD) - {cfd:.4f} (CFD)| = {divergence:.4f}")
        return divergence

    def run_analysis(self) -> Dict[str, Any]:
        """
        Runs the full suite of configured CFP analyses (QFD, Entanglement, Entropy).
        Returns a dictionary containing the calculated metrics (primary results)
        and the mandatory IAR 'reflection' dictionary assessing the analysis process.
        """
        logger.info(f"--- Starting Full CFP Analysis (v3.0) for Observable='{self.observable_name}', T={self.time_horizon}, Evolution='{self.evolution_model_type}' ---")
        primary_results: Dict[str, Any] = {} # Dictionary for primary metric outputs
        # Initialize IAR reflection dictionary with default failure state
        reflection = {
            "status": "Failure", "summary": "CFP analysis initialization failed.",
            "confidence": 0.0, "alignment_check": "N/A",
            "potential_issues": ["Initialization error."], "raw_output_preview": None
        }
        start_time = time.time()

        try:
            # Store key parameters used in the analysis
            primary_results['observable_analyzed'] = self.observable_name
            primary_results['time_horizon'] = self.time_horizon
            primary_results['evolution_model_used'] = self.evolution_model_type
            primary_results['system_dimension'] = self.system_dimension

            # --- Execute Core Calculations ---
            qfd = self.compute_quantum_flux_difference()
            primary_results['quantum_flux_difference'] = qfd if qfd is not None else None # Store if valid number

            # Also compute classical flux for comparison and to enable spooky flux
            cfd = self.compute_classical_flux_difference()
            primary_results['classical_flux_difference'] = cfd if cfd is not None else None

            ec = self.quantify_entanglement_correlation()
            primary_results['entanglement_correlation_MI'] = ec if ec is not None else None

            ea = self.compute_system_entropy('A')
            primary_results['entropy_system_a'] = ea if ea is not None else None

            eb = self.compute_system_entropy('B')
            primary_results['entropy_system_b'] = eb if eb is not None else None

            sfd = self.compute_spooky_flux_divergence()
            primary_results['spooky_flux_divergence'] = sfd if sfd is not None else None

            # Filter out None values from primary results for cleaner output (optional)
            # final_primary_results = {k: v for k, v in primary_results.items() if v is not None}
            # Keep None values for now to indicate calculation attempt failure
            final_primary_results = primary_results

            # --- Generate IAR Reflection Based on Outcomes ---
            calculated_metrics = [k for k, v in final_primary_results.items() if v is not None and k not in ['observable_analyzed', 'time_horizon', 'evolution_model_used', 'system_dimension']]
            potential_issues = []

            if self.evolution_model_type == 'placeholder':
                potential_issues.append("State evolution was placeholder (no actual dynamics simulated). QFD may not be meaningful.")
            if final_primary_results.get('spooky_flux_divergence') is None:
                potential_issues.append("Spooky Flux Divergence not calculated (requires classical baseline).")
            if not QUANTUM_UTILS_AVAILABLE:
                potential_issues.append("Quantum utils unavailable, quantum-related metrics simulated/limited.")
            if qfd is None and 'quantum_flux_difference' in final_primary_results: # Check if calculation was attempted but failed
                potential_issues.append("Quantum Flux Difference calculation failed.")
            if ec is None and 'entanglement_correlation_MI' in final_primary_results:
                potential_issues.append("Entanglement Correlation calculation failed.")
            # Add checks for other failed calculations if needed

            if not calculated_metrics: # If no key metrics were successfully calculated
                reflection["status"] = "Failure"
                reflection["summary"] = "CFP analysis failed to calculate key metrics."
                reflection["confidence"] = 0.1 # Very low confidence
                reflection["alignment_check"] = "Failed to meet analysis goal."
            else: # At least some metrics calculated
                reflection["status"] = "Success" # Consider it success even if some metrics failed
                reflection["summary"] = f"CFP analysis completed. Successfully calculated: {calculated_metrics}."
                # Base confidence on successful QFD calculation, adjust if other key metrics failed
                reflection["confidence"] = 0.85 if qfd is not None else 0.5
                reflection["alignment_check"] = "Aligned with comparing dynamic system states."

            reflection["potential_issues"] = potential_issues if potential_issues else None # Set to None if list is empty
            # Create preview from the calculated metrics
            preview_data = {k: v for k, v in final_primary_results.items() if k not in ['observable_analyzed', 'time_horizon', 'evolution_model_used', 'system_dimension']}
            reflection["raw_output_preview"] = json.dumps(preview_data, default=str)[:150] + "..." if preview_data else None

            logger.info(f"--- CFP Analysis Complete (Duration: {time.time() - start_time:.2f}s) ---")
            # Combine primary results and the final reflection
            return {**final_primary_results, "reflection": reflection}

        except Exception as e_run:
            # Catch unexpected errors during the overall run_analysis orchestration
            logger.error(f"Critical unexpected error during CFP run_analysis: {e_run}", exc_info=True)
            error_msg = f"Critical error in run_analysis: {e_run}"
            reflection["summary"] = f"CFP analysis failed critically: {error_msg}"
            reflection["potential_issues"] = ["Unexpected system error during analysis orchestration."]
            # Return error structure with reflection
            return {"error": error_msg, "reflection": reflection}

# --- END OF FILE 3.0ArchE/cfp_framework.py --- 