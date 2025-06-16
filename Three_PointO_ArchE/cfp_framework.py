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
from .utils.reflection_utils import _create_reflection # Canonical import for IAR creation

# Use relative imports for internal modules
try:
    # Import quantum utilities (superposition, entanglement, entropy calculations)
    from .quantum_utils import (superposition_state, entangled_state,
                                compute_multipartite_mutual_information,
                                calculate_shannon_entropy, von_neumann_entropy)
    QUANTUM_UTILS_AVAILABLE = True
    logger_q = logging.getLogger(__name__) # Use current module logger
    logger_q.info("quantum_utils.py loaded successfully for CFP.")
except ImportError:
    QUANTUM_UTILS_AVAILABLE = False
    # Define dummy functions if quantum_utils is not available to allow basic structure loading
    def superposition_state(state, factor=1.0): return np.array(state, dtype=complex)
    def entangled_state(a, b, coeffs=None): return np.kron(a,b)
    def compute_multipartite_mutual_information(state, dims): return 0.0
    def calculate_shannon_entropy(state): return 0.0
    def von_neumann_entropy(matrix): return 0.0
    logger_q = logging.getLogger(__name__)
    logger_q.warning("quantum_utils.py not found or failed to import. CFP quantum features will be simulated or unavailable.")
try:
    from . import config # Import configuration settings
except ImportError:
    # Fallback config if running standalone or structure differs
    class FallbackConfig: CFP_DEFAULT_TIMEFRAME = 1.0; CFP_EVOLUTION_MODEL_TYPE = "placeholder"
    config = FallbackConfig()
    logging.warning("config.py not found for cfp_framework, using fallback configuration.")

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
        time_horizon: float = config.CFP_DEFAULT_TIMEFRAME, # Duration of simulated evolution
        integration_steps: int = 100, # Hint for numerical integration resolution
        evolution_model_type: str = config.CFP_EVOLUTION_MODEL_TYPE, # Type of evolution ('placeholder', 'hamiltonian', 'ode_solver', etc.)
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
        Calculates Spooky Flux Divergence (Conceptual).
        Requires defining and calculating a 'classical' baseline flux for comparison.
        Currently returns None as baseline is not implemented.
        """
        logger.warning("Spooky Flux Divergence calculation requires a classical baseline flux which is not implemented in this version. Returning None.")
        # Conceptual Steps:
        # 1. Define a classical analogue system or evolution rule.
        # 2. Calculate the flux difference based on the classical evolution (e.g., classical_flux_difference).
        # 3. Calculate the quantum flux difference (qfd = self.compute_quantum_flux_difference()).
        # 4. Compute divergence, e.g., abs(qfd - classical_flux_difference) or a ratio.
        return None # Return None until implemented

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

    # --- New Methods for Classical and Feedback Testing (Placeholder Implementations) ---

    def compare_classical_states(self, state1: Union[List[float], np.ndarray], state2: Union[List[float], np.ndarray], method: str = 'euclidean') -> Dict[str, Any]:
        """
        [PLACEHOLDER] Compares two classical state vectors using specified method (Euclidean, Manhattan, Cosine).
        This is a placeholder implementation for classical comparison within the CFP framework.
        Returns a dictionary with comparison results and IAR reflection.
        """
        try:
            vec1 = np.array(state1, dtype=float)
            vec2 = np.array(state2, dtype=float)

            if len(vec1) != len(vec2):
                raise ValueError("State vectors must have the same dimension for comparison.")
            if len(vec1) == 0:
                return {"distance": 0.0, "method_used": method, "reflection": _create_reflection("Success", "Compared empty vectors.", 1.0, "N/A", [], "Distance: 0.0")}


            if method.lower() == 'euclidean':
                distance = np.linalg.norm(vec1 - vec2)
                summary = f"Euclidean distance calculated: {distance:.4f}"
                status = "Success"
                confidence = 1.0
                issues = []
            elif method.lower() == 'manhattan':
                distance = np.sum(np.abs(vec1 - vec2))
                summary = f"Manhattan distance calculated: {distance:.4f}"
                status = "Success"
                confidence = 1.0
                issues = []
            elif method.lower() == 'cosine':
                # Handle zero vectors for cosine similarity
                norm_v1 = np.linalg.norm(vec1)
                norm_v2 = np.linalg.norm(vec2)
                if norm_v1 == 0 or norm_v2 == 0:
                    raise ValueError("Cannot compute cosine similarity if one or both vectors have zero magnitude.")

                similarity = np.dot(vec1, vec2) / (norm_v1 * norm_v2)
                distance = 1 - similarity # Cosine distance
                summary = f"Cosine similarity calculated: {similarity:.4f}, distance: {distance:.4f}"
                status = "Success"
                confidence = 1.0
                issues = []
                return {"similarity": similarity, "distance": distance, "method_used": method, "reflection": _create_reflection(status, summary, confidence, "N/A", issues, f"Sim: {similarity:.2f}, Dist: {distance:.2f}")}
            else:
                raise ValueError(f"Comparison method '{method}' not supported.")

            return {"distance": distance, "method_used": method, "reflection": _create_reflection(status, summary, confidence, "N/A", issues, f"Distance: {distance:.2f}")}

        except Exception as e:
            error_summary = f"Error during classical state comparison: {type(e).__name__}: {str(e)}"
            logger.error(error_summary, exc_info=True)
            return {"distance": None, "similarity": None, "method_used": method, "reflection": _create_reflection("Failure", error_summary, 0.0, "N/A", [str(e)], None)}

    # Global best tracking (simple, for feedback loop testing)
    _global_best_distance: float = float('inf')

    def get_global_best(self) -> float:
        """Returns the current best known distance (or cost) globally recorded by the CFP system."""
        return self._global_best_distance

    def reset_global_best(self):
        """Resets the global best distance to infinity. Used for re-running scenarios."""
        self._global_best_distance = float('inf')
        logger.info("Global best distance reset.")

    def process_feedback_request(self, agent_id: str, current_distance: float, previous_distance: float, effort_spent: float = 0.0) -> Dict[str, Any]:
        """
        [PLACEHOLDER] Processes feedback from an agent/system and provides a directive.
        Updates global best, assesses improvement, and suggests next steps.
        Returns a dictionary with directive, agent feedback, and IAR reflection.
        """
        status = "Success"
        summary = f"Feedback processed for agent {agent_id}."
        confidence = 1.0
        potential_issues = []
        directive = "continue_refinement"
        action = "refine_further" # Default action
        notes = []
        reset_to_best_known = False

        try:
            # Update global best if current performance is better
            if current_distance < self._global_best_distance:
                self._global_best_distance = current_distance
                notes.append(f"New global best distance recorded: {current_distance:.4f}")
                directive = "exploit" # Exploit new best performance
                action = "exploit_current_best"
            
            # Assess improvement relative to previous step
            improvement = previous_distance - current_distance
            if improvement > 0:
                notes.append(f"Agent {agent_id} improved by {improvement:.4f} (from {previous_distance:.4f} to {current_distance:.4f}).")
                # If it's a new global best, it's already an 'exploit' directive.
                # Otherwise, it's a 'refine_further' within local search space.
                if directive != "exploit":
                     directive = "refine_further"
                     action = "refine_further"
            elif improvement < 0:
                notes.append(f"Agent {agent_id} worsened by {-improvement:.4f} (from {previous_distance:.4f} to {current_distance:.4f}).")
                # Check if it's significantly worse than global best
                if current_distance > self._global_best_distance * 1.05: # Simple threshold for 'stuck'
                    notes = ["Stuck and far from global best. Suggesting reset."] # Set directly to ensure it's the only and first note
                    directive = "maintain_or_explore_gently"
                    action = "reset_to_best_known"
                    reset_to_best_known = True
                else:
                    directive = "refine_further" # Slight worsening, try to refine locally
                    action = "refine_further"
            else: # No improvement
                # Check if it's significantly worse than global best
                if current_distance > self._global_best_distance * 1.05: # Simple threshold for 'stuck'
                    notes = ["Stuck and far from global best. Suggesting reset."] # Set directly to ensure it's the only and first note
                    directive = "maintain_or_explore_gently"
                    action = "reset_to_best_known"
                    reset_to_best_known = True
                else:
                    notes.append(f"Agent {agent_id} did not improve (distance: {current_distance:.4f}).")
                    directive = "refine_further" # Still close, try more local refinement
                    action = "refine_further"

            # Consider effort spent (conceptual)
            if effort_spent > 0 and improvement <= 0 and directive != "reset_to_best_known":
                notes.append(f"Agent expended {effort_spent} effort with no improvement. Consider broader exploration or strategic shift.")
                if confidence > 0.5: confidence = 0.5 # Reduce confidence if effort is wasted

        except Exception as e:
            status = "Failure"
            summary = f"Error processing feedback: {str(e)}"
            confidence = 0.0
            potential_issues.append(str(e))
            directive = "error"
            action = "error_halt"
            logger.error(summary, exc_info=True)

        feedback_details = {
            "agent_id": agent_id,
            "current_distance": current_distance,
            "previous_distance": previous_distance,
            "improvement": improvement,
            "global_best_distance": self._global_best_distance,
            "effort_spent": effort_spent,
            "action": action,
            "notes": notes,
            "reset_to_best_known": reset_to_best_known
        }

        # Use the canonical _create_reflection from reflection_utils
        reflection = _create_reflection(
            status=status,
            summary=summary,
            confidence=confidence,
            alignment="Feedback processing completed",
            issues=potential_issues,
            preview=f"Directive: {directive}, Agent: {agent_id}"
        )

        return {
            "directive": directive,
            "agent_feedback": feedback_details,
            "reflection": reflection
        }

# --- END OF FILE 3.0ArchE/cfp_framework.py --- 