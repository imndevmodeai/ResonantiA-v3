#--- START OF FILE 3.0ArchE/cfp_framework.py ---
# ResonantiA Protocol v3.0 - cfp_framework.py
# Implements the Comparative Fluxual Processing (CFP) Framework.
# Incorporates Quantum-Inspired principles and State Evolution logic.
# Returns results including mandatory Integrated Action Reflection (IAR).

from typing import Union, Dict, Any, Optional, List, Tuple, Callable # Expanded type hints
import numpy as np
# Import necessary scientific libraries (ensure they are in requirements.txt)
from scipy.integrate import quad, solve_ivp # For numerical integration & ODE solving example
from scipy.linalg import expm, LinAlgError # For matrix exponentiation (Hamiltonian evolution example) & error handling
import logging
import json # For IAR preview serialization
import time # For timing analysis

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

# --- IAR Helper ---
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = json.dumps(preview, default=str) if isinstance(preview, (dict, list)) else str(preview)
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception:
        try: preview_str = str(preview); preview_str = preview_str[:150] + "..." if len(preview_str) > 150 else preview_str
        except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}


class CFPFramework:
    """
    Comparative Fluxual Processing (CFP) Framework - Quantum Enhanced w/ Evolution (v3.0).

    Models and compares the dynamics of two configured systems over time.
    Incorporates quantum-inspired principles (superposition, entanglement via mutual info)
    and implements state evolution logic (e.g., Hamiltonian, conceptual ODE).
    Calculates metrics like Quantum Flux Difference and Entanglement Correlation.
    Returns results dictionary including a detailed IAR reflection assessing the analysis.
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
        hamiltonian_b: Optional[np.ndarray] = None, # Optional Hamiltonian matrix for system B
        ode_func_a: Optional[Callable] = None, # Optional ODE function d|psi>/dt for system A
        ode_func_b: Optional[Callable] = None, # Optional ODE function d|psi>/dt for system B
        **kwargs # Allow additional config passthrough
    ):
        """
        Initializes the CFP Framework instance. Enhanced for v3.0 evolution models.
        """
        # (Validation code identical to previous version - checks imports, types, dimensions)
        if not QUANTUM_UTILS_AVAILABLE: raise ImportError("Quantum Utils required but not found.")
        if not isinstance(system_a_config, dict) or not isinstance(system_b_config, dict): raise TypeError("System configs must be dictionaries.")
        if time_horizon <= 0 or integration_steps <= 0: raise ValueError("Time horizon and integration steps must be positive.")

        self.system_a_config = system_a_config
        self.system_b_config = system_b_config
        self.observable_name = observable
        self.time_horizon = float(time_horizon)
        self.integration_steps = int(integration_steps)
        self.evolution_model_type = evolution_model_type.lower()
        self.hamiltonian_a = hamiltonian_a
        self.hamiltonian_b = hamiltonian_b
        self.ode_func_a = ode_func_a # Store ODE function if provided
        self.ode_func_b = ode_func_b # Store ODE function if provided
        self.extra_config = kwargs # Store other config

        self.state_a_initial_raw = self._validate_and_get_state(self.system_a_config, 'A')
        self.state_b_initial_raw = self._validate_and_get_state(self.system_b_config, 'B')
        dim_a = len(self.state_a_initial_raw); dim_b = len(self.state_b_initial_raw)
        if dim_a != dim_b: raise ValueError(f"State dimensions must match ({dim_a} vs {dim_b})")
        self.system_dimension = dim_a

        if self.evolution_model_type == 'hamiltonian':
            self.hamiltonian_a = self._validate_hamiltonian(self.hamiltonian_a, 'A')
            self.hamiltonian_b = self._validate_hamiltonian(self.hamiltonian_b, 'B')
        elif self.evolution_model_type == 'ode_solver':
            if not callable(self.ode_func_a) or not callable(self.ode_func_b):
                 raise ValueError("ODE functions ('ode_func_a', 'ode_func_b') must be provided and callable for 'ode_solver' evolution type.")
            # Further validation of ODE function signature could be added here

        self.observable_operator = self._get_operator(self.observable_name)
        logger.info(f"CFP Framework (v3.0) initialized: Observable='{self.observable_name}', T={self.time_horizon}s, Dim={self.system_dimension}, Evolution='{self.evolution_model_type}'")

    # --- Validation and Operator Methods (Identical to previous version) ---
    def _validate_and_get_state(self, system_config: Dict[str, Any], label: str) -> np.ndarray:
        state = system_config.get('quantum_state'); # ... (rest of validation code)
        if state is None: raise ValueError(f"System {label} config missing 'quantum_state'.")
        vec = np.array(state, dtype=complex); # ... (rest of validation)
        if vec.ndim != 1: raise ValueError(f"System {label} 'quantum_state' must be 1D.")
        if vec.size == 0: raise ValueError(f"System {label} 'quantum_state' cannot be empty.")
        return vec
    def _validate_hamiltonian(self, H: Optional[np.ndarray], label: str) -> np.ndarray:
        if H is None: raise ValueError(f"Hamiltonian for system {label} required for 'hamiltonian' evolution."); # ... (rest of validation)
        if not isinstance(H, np.ndarray): raise TypeError(f"Hamiltonian {label} must be NumPy array."); # ... (rest of validation)
        expected_shape = (self.system_dimension, self.system_dimension)
        if H.shape != expected_shape: raise ValueError(f"Hamiltonian {label} shape {H.shape} incorrect, expected {expected_shape}.")
        if not np.allclose(H, H.conj().T, atol=1e-8): logger.warning(f"Hamiltonian {label} not Hermitian.")
        return H
    def _get_operator(self, observable_name: str) -> np.ndarray:
        dim = self.system_dimension; op: Optional[np.ndarray] = None; name_lower = observable_name.lower(); # ... (rest of operator definition logic)
        if name_lower == "position": op = np.diag(np.linspace(-1, 1, dim)).astype(complex)
        elif name_lower == "energy": op = np.diag(np.arange(dim)).astype(complex)
        # Add other operators...
        if op is None: op = np.identity(dim, dtype=complex); logger.warning(f"Unsupported observable '{observable_name}'. Using Identity."); # ... (rest of logic)
        return op.astype(complex)

    # --- State Evolution Method (Enhanced v3.0) ---
    def _evolve_state(self, initial_state_vector: np.ndarray, dt: float, system_label: str) -> np.ndarray:
        """
        [Enhanced v3.0] Evolves the quantum state vector over time interval dt.
        Uses the evolution model specified during initialization ('hamiltonian', 'ode_solver', 'placeholder').

        Args:
            initial_state_vector: The starting state vector (NumPy complex array).
            dt: The time interval for evolution.
            system_label: 'A' or 'B' to select the appropriate Hamiltonian/ODE function.

        Returns:
            The evolved state vector (NumPy complex array). Returns original state on error.
        """
        if dt == 0: return initial_state_vector

        if self.evolution_model_type == 'hamiltonian':
            H = self.hamiltonian_a if system_label == 'A' else self.hamiltonian_b
            if H is None: logger.error(f"Hamiltonian missing for system {system_label} despite 'hamiltonian' type. Returning unchanged state."); return initial_state_vector
            try:
                U = expm(-1j * H * dt) # Assuming hbar=1
                evolved_state = U @ initial_state_vector
                norm = np.linalg.norm(evolved_state)
                return evolved_state / norm if norm > 1e-15 else evolved_state
            except (LinAlgError, ValueError, TypeError) as e_evolve:
                logger.error(f"Hamiltonian evolution failed for system {system_label} at dt={dt}: {e_evolve}", exc_info=True)
                return initial_state_vector

        elif self.evolution_model_type == 'ode_solver':
            ode_func = self.ode_func_a if system_label == 'A' else self.ode_func_b
            if not callable(ode_func): # Should be caught in init, but safeguard
                 logger.error(f"ODE function missing for system {system_label} despite 'ode_solver' type. Returning unchanged state.")
                 return initial_state_vector
            try:
                # --- Conceptual ODE Solver Implementation ---
                # Define the Schrodinger equation RHS: d|psi>/dt = -i * H * |psi> / hbar
                # Note: The ODE function passed in `ode_func` needs to implement this logic,
                # potentially taking the Hamiltonian or other parameters implicitly or explicitly.
                # For this example, we assume ode_func has signature: func(t, psi_flat) -> d(psi_flat)/dt
                # We need to flatten/unflatten the complex state vector for solve_ivp.

                def complex_ode_wrapper(t, y_flat, ode_function):
                    """Wrapper for solve_ivp with complex numbers."""
                    psi = y_flat.view(np.complex128) # Reshape flat float array back to complex vector
                    d_psi_dt = ode_function(t, psi) # Call the user-provided ODE function
                    return d_psi_dt.view(np.float64) # Return flattened float array

                # Initial state needs to be flattened array of floats (real, imag interleaved)
                y0_flat = initial_state_vector.view(np.float64)
                t_span = (0, dt) # Integrate from 0 to dt

                # Use solve_ivp (e.g., with RK45 method)
                sol = solve_ivp(complex_ode_wrapper, t_span, y0_flat, args=(ode_func,), method='RK45', rtol=1e-6, atol=1e-9)

                if not sol.success:
                    logger.error(f"ODE solver failed for system {system_label} at dt={dt}: {sol.message}")
                    return initial_state_vector

                # Extract final state, reshape back to complex vector
                y_final_flat = sol.y[:, -1]
                evolved_state = y_final_flat.view(np.complex128)

                # Renormalize
                norm = np.linalg.norm(evolved_state)
                return evolved_state / norm if norm > 1e-15 else evolved_state

            except Exception as e_ode:
                logger.error(f"ODE solver evolution failed for system {system_label} at dt={dt}: {e_ode}", exc_info=True)
                return initial_state_vector

        elif self.evolution_model_type == 'placeholder' or self.evolution_model_type == 'none':
            return initial_state_vector

        else:
            logger.warning(f"Unknown evolution model type '{self.evolution_model_type}'. Returning unchanged state.")
            return initial_state_vector

    # --- Core Calculation Methods (Identical to previous version, use _evolve_state) ---
    def compute_quantum_flux_difference(self) -> Optional[float]:
        logger.info(f"Computing Quantum Flux Difference (CFP_Quantum) for observable '{self.observable_name}' over T={self.time_horizon}...")
        try: state_a_initial = superposition_state(self.state_a_initial_raw); state_b_initial = superposition_state(self.state_b_initial_raw)
        except Exception as e: logger.error(f"State normalization failed: {e}"); return None
        op = self.observable_operator
        def integrand(t: float) -> float:
            try:
                state_a_t = self._evolve_state(state_a_initial, t, 'A') # Uses implemented evolution
                state_b_t = self._evolve_state(state_b_initial, t, 'B') # Uses implemented evolution
                if state_a_t.ndim == 1: state_a_t = state_a_t[:, np.newaxis]
                if state_b_t.ndim == 1: state_b_t = state_b_t[:, np.newaxis]
                exp_a = np.real((state_a_t.conj().T @ op @ state_a_t)[0,0])
                exp_b = np.real((state_b_t.conj().T @ op @ state_b_t)[0,0])
                diff_sq = (exp_a - exp_b)**2
                return diff_sq if not np.isnan(diff_sq) else np.nan
            except Exception as e_inner: logger.error(f"Error in integrand at t={t}: {e_inner}"); return np.nan
        try:
            integral_result, abserr, infodict = quad(integrand, 0, self.time_horizon, limit=self.integration_steps * 5, full_output=True, epsabs=1.49e-08, epsrel=1.49e-08)
            logger.info(f"Integration completed. Result: {integral_result:.6f}, Est. Abs Error: {abserr:.4g}, Evals: {infodict.get('neval', 0)}")
            if 'message' in infodict and infodict['message'] != 'OK': logger.warning(f"Integration warning: {infodict['message']}")
            return float(integral_result) if not np.isnan(integral_result) else None
        except Exception as e_quad: logger.error(f"Error during numerical integration: {e_quad}"); return None

    def quantify_entanglement_correlation(self) -> Optional[float]:
        # (Code identical to previous version - uses quantum_utils)
        if not QUANTUM_UTILS_AVAILABLE: logger.warning("Quantum utils unavailable."); return None
        logger.info("Quantifying Entanglement Correlation (MI)...")
        try: state_a = superposition_state(self.state_a_initial_raw); state_b = superposition_state(self.state_b_initial_raw); dims = [len(state_a), len(state_b)]; combined_state_product = entangled_state(state_a, state_b); mutual_info = compute_multipartite_mutual_information(combined_state_product, dims); return float(mutual_info) if not np.isnan(mutual_info) else None
        except Exception as e: logger.error(f"Error calculating entanglement: {e}"); return None
    def compute_system_entropy(self, system_label: str) -> Optional[float]:
        # (Code identical to previous version - uses quantum_utils)
        if not QUANTUM_UTILS_AVAILABLE: logger.warning("Quantum utils unavailable."); return None
        logger.info(f"Computing initial Shannon Entropy for System {system_label}...")
        try: initial_state = self.state_a_initial_raw if system_label == 'A' else self.state_b_initial_raw; entropy = calculate_shannon_entropy(initial_state); return float(entropy) if not np.isnan(entropy) else None
        except Exception as e: logger.error(f"Error computing Shannon entropy for {system_label}: {e}"); return None
    def compute_spooky_flux_divergence(self) -> Optional[float]:
        # (Code identical to previous version - requires baseline implementation)
        logger.warning("Spooky Flux Divergence calculation requires unimplemented classical baseline. Returning None.")
        return None

    # --- Run Analysis Method (Enhanced IAR v3.0) ---
    def run_analysis(self) -> Dict[str, Any]:
        """
        Runs the full suite of configured CFP analyses (QFD, Entanglement, Entropy).
        Returns results including mandatory IAR reflection assessing the process.
        """
        logger.info(f"--- Starting Full CFP Analysis (v3.0) for Observable='{self.observable_name}', T={self.time_horizon}, Evolution='{self.evolution_model_type}' ---")
        primary_results: Dict[str, Any] = {}
        reflection_status = "Failure"; summary = "CFP analysis init failed."; confidence = 0.0; alignment = "N/A"; issues = []; preview = None
        start_time = time.time()

        try:
            # Store key parameters
            primary_results['observable_analyzed'] = self.observable_name
            primary_results['time_horizon'] = self.time_horizon
            primary_results['evolution_model_used'] = self.evolution_model_type
            primary_results['system_dimension'] = self.system_dimension

            # --- Execute Calculations ---
            qfd = self.compute_quantum_flux_difference()
            primary_results['quantum_flux_difference'] = qfd

            ec = self.quantify_entanglement_correlation()
            primary_results['entanglement_correlation_MI'] = ec

            ea = self.compute_system_entropy('A')
            primary_results['entropy_system_a'] = ea

            eb = self.compute_system_entropy('B')
            primary_results['entropy_system_b'] = eb

            sfd = self.compute_spooky_flux_divergence()
            primary_results['spooky_flux_divergence'] = sfd

            # --- Generate IAR Reflection ---
            calculated_metrics = [k for k, v in primary_results.items() if v is not None and k not in ['observable_analyzed', 'time_horizon', 'evolution_model_used', 'system_dimension']]
            potential_issues = []

            # Add issues based on evolution model and calculation failures
            if self.evolution_model_type == 'placeholder':
                potential_issues.append("State evolution was placeholder (no actual dynamics simulated). QFD may not be meaningful.")
            elif self.evolution_model_type == 'ode_solver' and (not callable(self.ode_func_a) or not callable(self.ode_func_b)):
                 potential_issues.append("ODE solver selected but valid functions not provided during init.")
            elif self.evolution_model_type not in ['hamiltonian', 'ode_solver', 'placeholder', 'none']:
                 potential_issues.append(f"Unknown or unimplemented evolution model '{self.evolution_model_type}' used.")

            if qfd is None and 'quantum_flux_difference' in primary_results: potential_issues.append("Quantum Flux Difference calculation failed.")
            if ec is None and 'entanglement_correlation_MI' in primary_results: potential_issues.append("Entanglement Correlation calculation failed.")
            if sfd is None and 'spooky_flux_divergence' in primary_results: potential_issues.append("Spooky Flux Divergence not calculated (requires classical baseline).")
            if not QUANTUM_UTILS_AVAILABLE: potential_issues.append("Quantum utils unavailable, quantum metrics simulated/limited.")

            if not calculated_metrics: # If no key metrics calculated successfully
                reflection_status = "Failure"; summary = "CFP analysis failed to calculate key metrics."; confidence = 0.1; alignment = "Failed to meet analysis goal."
            else:
                reflection_status = "Success" # Success if at least one metric calculated
                summary = f"CFP analysis completed using evolution '{self.evolution_model_type}'. Calculated: {calculated_metrics}."
                # Base confidence on QFD success and evolution model validity
                confidence = 0.85 if qfd is not None and self.evolution_model_type != 'placeholder' else 0.5
                if self.evolution_model_type == 'placeholder': confidence = max(0.2, confidence * 0.5) # Lower confidence for placeholder
                if potential_issues: confidence = max(0.1, confidence * 0.8) # Lower confidence if issues exist
                alignment = "Aligned with comparing dynamic system states."

            issues = potential_issues if potential_issues else None
            preview_data = {k: v for k, v in primary_results.items() if v is not None and k not in ['observable_analyzed', 'time_horizon', 'evolution_model_used', 'system_dimension']}
            preview = preview_data if preview_data else None

            logger.info(f"--- CFP Analysis Complete (Duration: {time.time() - start_time:.2f}s) ---")
            # Combine primary results and the final reflection
            return {**primary_results, "reflection": _create_reflection(reflection_status, summary, confidence, alignment, issues, preview)}

        except Exception as e_run:
            # Catch unexpected errors during the overall run_analysis orchestration
            logger.error(f"Critical unexpected error during CFP run_analysis: {e_run}", exc_info=True)
            error_msg = f"Critical error in run_analysis: {e_run}"
            summary = f"CFP analysis failed critically: {error_msg}"
            issues = ["Unexpected system error during analysis orchestration."]
            # Return error structure with reflection
            return {"error": error_msg, "reflection": _create_reflection("Failure", summary, 0.0, "N/A", issues, None)}

# --- END OF FILE 3.0ArchE/cf