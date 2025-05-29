# --- START OF FILE 3.0ArchE/quantum_utils.py ---
# ResonantiA Protocol v3.0 - quantum_utils.py
# Provides utility functions for quantum state vector manipulation, density matrix
# calculations, and information-theoretic measures (entropy, mutual information)
# primarily supporting the CfpframeworK (Section 7.6).

import numpy as np
# Import necessary math functions from scipy and standard math library
from scipy.linalg import logm, sqrtm, LinAlgError # Used for Von Neumann entropy (logm, sqrtm not strictly needed for VN but useful for other metrics)
from math import log2, sqrt # Use log base 2 for information measures
import logging
from typing import Union, List, Optional, Tuple, cast # Expanded type hints

logger = logging.getLogger(__name__)
# Basic logging config if running standalone or logger not configured externally
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - QuantumUtils - %(levelname)s - %(message)s')

# --- State Vector Manipulation ---

def superposition_state(quantum_state: Union[List, np.ndarray], amplitude_factor: float = 1.0) -> np.ndarray:
    """
    Normalizes a list or NumPy array into a valid quantum state vector (L2 norm = 1).
    Optionally multiplies by an amplitude factor before normalization.
    Ensures the output is a 1D complex NumPy array.

    Args:
        quantum_state: Input list or NumPy array representing the state.
        amplitude_factor: Optional float factor to multiply state by before normalization.

    Returns:
        A 1D complex NumPy array representing the normalized quantum state vector.

    Raises:
        TypeError: If input is not a list or NumPy array.
        ValueError: If input cannot be converted to 1D complex array, is empty, or has zero norm.
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
        if norm < 1e-15: # Use a small epsilon to avoid floating point issues
            raise ValueError("Input quantum state has zero norm and cannot be normalized.")

        # Normalize the state vector
        normalized_state = state / norm
        logger.debug(f"Input state normalized. Original norm: {norm:.4f}")
        return normalized_state
    except (ValueError, TypeError) as e:
        # Re-raise validation errors with context
        raise e
    except Exception as e_conv:
        # Catch other potential errors during conversion/normalization
        raise ValueError(f"Error processing input quantum state: {e_conv}")

def entangled_state(state_a: Union[List, np.ndarray], state_b: Union[List, np.ndarray], coefficients: Optional[np.ndarray] = None) -> np.ndarray:
    """
    Creates a combined quantum state vector representing the tensor product (|a> ⊗ |b>)
    of two input state vectors. Normalizes the resulting combined state.
    The 'coefficients' argument is currently ignored (intended for future generalized entanglement).

    Args:
        state_a: State vector for the first subsystem (list or NumPy array).
        state_b: State vector for the second subsystem (list or NumPy array).
        coefficients: Optional coefficients for generalized entanglement (currently ignored).

    Returns:
        A normalized 1D complex NumPy array representing the combined state vector.

    Raises:
        TypeError: If inputs are not lists or NumPy arrays.
        ValueError: If input states are invalid (e.g., wrong dimensions, empty).
    """
    # Validate input types
    if not isinstance(state_a, (list, np.ndarray)): raise TypeError(f"Input 'state_a' must be list/array.")
    if not isinstance(state_b, (list, np.ndarray)): raise TypeError(f"Input 'state_b' must be list/array.")

    try:
        # Convert inputs to 1D complex arrays
        vec_a = np.array(state_a, dtype=complex)
        vec_b = np.array(state_b, dtype=complex)
        if vec_a.ndim != 1 or vec_b.ndim != 1: raise ValueError("Input states must be 1-dimensional vectors.")
        if vec_a.size == 0 or vec_b.size == 0: raise ValueError("Input states cannot be empty.")
    except Exception as e_conv:
        raise ValueError(f"Error converting input states to vectors: {e_conv}")

    # Calculate the tensor product using np.kron
    combined_state = np.kron(vec_a, vec_b)

    # Log warning if coefficients are provided but ignored
    if coefficients is not None:
        logger.warning("The 'coefficients' parameter is currently ignored in 'entangled_state' (v3.0). Using simple tensor product.")

    try:
        # Normalize the resulting combined state
        final_state = superposition_state(combined_state) # Reuse normalization function
        logger.debug(f"Created combined state (tensor product) of dimension {final_state.size}.")
        return final_state
    except ValueError as e_norm:
        # Catch normalization errors for the combined state
        raise ValueError(f"Could not normalize the combined tensor product state: {e_norm}")

# --- Density Matrix and Entropy Calculations ---

def _density_matrix(state_vector: np.ndarray) -> np.ndarray:
    """
    Calculates the density matrix (rho = |psi><psi|) for a pure quantum state vector.
    Internal helper function.

    Args:
        state_vector: A normalized 1D complex NumPy array representing the state vector |psi>.

    Returns:
        A 2D complex NumPy array representing the density matrix.

    Raises:
        ValueError: If the input is not a 1D array.
    """
    # Ensure input is a NumPy array and 1D
    state_vector = np.asarray(state_vector, dtype=complex)
    if state_vector.ndim != 1:
        raise ValueError("Input state_vector must be 1-dimensional.")

    # Reshape to column vector for outer product
    # state_vector[:, np.newaxis] creates a column vector (N, 1)
    # state_vector.conj().T creates a row vector (1, N) containing conjugate values
    column_vector = state_vector[:, np.newaxis]
    density_mat = column_vector @ column_vector.conj().T # Outer product

    # Verification (optional, for debugging): Check trace is close to 1
    trace = np.trace(density_mat)
    if not np.isclose(trace, 1.0, atol=1e-8):
        logger.warning(f"Density matrix trace is {trace.real:.6f}, expected 1. Input vector norm might not be exactly 1.")

    logger.debug(f"Computed density matrix (shape {density_mat.shape}).")
    return density_mat

def partial_trace(density_matrix: np.ndarray, keep_subsystem: int, dims: List[int]) -> np.ndarray:
    """
    Computes the partial trace of a density matrix over specified subsystems.

    Args:
        density_matrix: The density matrix of the combined system (2D NumPy array).
        keep_subsystem: The index of the subsystem to *keep* (0-based).
        dims: A list of integers representing the dimensions of each subsystem.
            The product of dims must equal the dimension of the density_matrix.

    Returns:
        The reduced density matrix of the kept subsystem (2D NumPy array).

    Raises:
        ValueError: If inputs are invalid (dims, keep_subsystem index, matrix shape).
    """
    num_subsystems = len(dims)
    if not all(isinstance(d, int) and d > 0 for d in dims):
        raise ValueError("dims must be a list of positive integers.")
    if not (0 <= keep_subsystem < num_subsystems):
        raise ValueError(f"Invalid subsystem index {keep_subsystem} for {num_subsystems} subsystems.")

    total_dim = np.prod(dims)
    if density_matrix.shape != (total_dim, total_dim):
        raise ValueError(f"Density matrix shape {density_matrix.shape} is inconsistent with total dimension {total_dim} derived from dims {dims}.")

    # Verification (optional): Check properties of input matrix
    # if not np.allclose(density_matrix, density_matrix.conj().T, atol=1e-8):
    #     logger.warning("Input density matrix may not be Hermitian.")
    # trace_val = np.trace(density_matrix)
    # if not np.isclose(trace_val, 1.0, atol=1e-8):
    #     logger.warning(f"Input density matrix trace is {trace_val.real:.6f}, expected 1.")

    try:
        # Reshape the density matrix into a tensor with 2*num_subsystems indices
        # Shape will be (d1, d2, ..., dn, d1, d2, ..., dn)
        rho_tensor = density_matrix.reshape(dims + dims)
    except ValueError as e_reshape:
        raise ValueError(f"Cannot reshape density matrix with shape {density_matrix.shape} to dims {dims + dims}: {e_reshape}")

    # --- Use np.einsum for efficient partial trace ---
    # Generate index strings for einsum
    # Example: 2 subsystems, dims=[2,3], keep=0
    # rho_tensor shape = (2, 3, 2, 3)
    # Indices: 'ab' for kets, 'cd' for bras -> 'abcd'
    # Keep subsystem 0 (index 'a' and 'c')
    # Trace over subsystem 1 (indices 'b' and 'd' must match) -> bra index 'd' becomes 'b'
    # Input string: 'abcb'
    # Output string: 'ac' (indices of kept subsystem)
    # Einsum string: 'abcb->ac'
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' # Sufficient for many subsystems
    if 2 * num_subsystems > len(alphabet):
        raise ValueError("Too many subsystems for default alphabet in partial trace.")

    ket_indices = list(alphabet[:num_subsystems])
    bra_indices = list(alphabet[num_subsystems : 2 * num_subsystems])

    # Build the einsum input string by tracing over unwanted subsystems
    einsum_input_indices = list(ket_indices) # Start with ket indices
    for i in range(num_subsystems):
        if i == keep_subsystem:
            einsum_input_indices.append(bra_indices[i]) # Keep the distinct bra index for the kept subsystem
        else:
            einsum_input_indices.append(ket_indices[i]) # Use the ket index for the bra index to trace over it

    # Build the einsum output string (indices of the kept subsystem)
    output_indices = ket_indices[keep_subsystem] + bra_indices[keep_subsystem]

    einsum_str = f"{''.join(einsum_input_indices)}->{output_indices}"
    logger.debug(f"Performing partial trace with einsum string: '{einsum_str}'")

    try:
        # Calculate partial trace using Einstein summation
        reduced_density_matrix = np.einsum(einsum_str, rho_tensor, optimize='greedy') # Optimize path finding
    except Exception as e_einsum:
        raise ValueError(f"Failed to compute partial trace via np.einsum: {e_einsum}")

    # Verification (optional): Check trace of reduced matrix
    # reduced_trace = np.trace(reduced_density_matrix)
    # if not np.isclose(reduced_trace, 1.0, atol=1e-8):
    #     logger.warning(f"Reduced density matrix trace is {reduced_trace.real:.6f}, expected 1.")

    logger.debug(f"Reduced density matrix for subsystem {keep_subsystem} calculated (shape {reduced_density_matrix.shape}).")
    return reduced_density_matrix

def von_neumann_entropy(density_matrix: np.ndarray) -> float:
    """
    Computes the Von Neumann entropy S(rho) = -Tr(rho * log2(rho)) for a density matrix.
    Uses the eigenvalue method: S = -sum(lambda_i * log2(lambda_i)).

    Args:
        density_matrix: The density matrix (2D complex NumPy array).

    Returns:
        The Von Neumann entropy (float, non-negative). Returns np.nan on error.

    Raises:
        ValueError: If the input is not a square matrix.
    """
    rho = np.asarray(density_matrix, dtype=complex)
    # Validate shape
    if rho.ndim != 2 or rho.shape[0] != rho.shape[1]:
        raise ValueError(f"Density matrix must be square, got shape {rho.shape}.")

    # Calculate eigenvalues. Use eigvalsh for Hermitian matrices (faster, real eigenvalues).
    # Add small identity matrix perturbation for numerical stability if matrix is singular? Maybe not needed.
    try:
        # Ensure matrix is Hermitian for eigvalsh, otherwise use eigvals
        # Add tolerance check for Hermitian property
        # if not np.allclose(rho, rho.conj().T, atol=1e-8):
        #     logger.warning("Input matrix for Von Neumann entropy is not Hermitian. Using general eigenvalue solver.")
        #     eigenvalues_complex = np.linalg.eigvals(rho)
        #     eigenvalues = np.real(eigenvalues_complex) # Entropy uses real part
        # else:
        eigenvalues = np.linalg.eigvalsh(rho) # Assumes Hermitian
    except LinAlgError as e_eig:
        logger.error(f"Eigenvalue computation failed for Von Neumann entropy: {e_eig}. Returning NaN.")
        return np.nan

    # Filter out zero or negative eigenvalues (log2 is undefined for them)
    # Use a small tolerance epsilon > 0
    tolerance = 1e-15
    positive_eigenvalues = eigenvalues[eigenvalues > tolerance]

    # If no positive eigenvalues (e.g., zero matrix), entropy is 0
    if len(positive_eigenvalues) == 0:
        return 0.0

    try:
        # Calculate entropy: S = -sum(lambda_i * log2(lambda_i))
        entropy = -np.sum(positive_eigenvalues * np.log2(positive_eigenvalues))
    except FloatingPointError as e_fp:
        # Catch potential issues like log2(very small number)
        logger.error(f"Floating point error during Von Neumann entropy calculation: {e_fp}. Returning NaN.")
        return np.nan

    # Ensure entropy is non-negative (within tolerance) and not NaN
    if entropy < -1e-12: # Allow for small numerical errors
        logger.warning(f"Calculated negative Von Neumann entropy ({entropy:.4g}). Clamping to 0.0.")
        entropy = 0.0
    elif np.isnan(entropy):
        logger.warning("Calculated NaN Von Neumann entropy. Returning 0.0.")
        entropy = 0.0
    else:
        # Ensure non-negativity strictly
        entropy = max(0.0, entropy)

    logger.debug(f"Calculated Von Neumann Entropy: {entropy:.6f}")
    return float(entropy)

def compute_multipartite_mutual_information(state_vector: np.ndarray, dims: List[int]) -> float:
    """
    Computes the bipartite mutual information I(A:B) = S(A) + S(B) - S(AB)
    for a pure state vector of a combined system AB.

    Args:
        state_vector: The normalized state vector of the combined system AB.
        dims: A list of two integers [dim_A, dim_B] specifying the dimensions
            of the subsystems A and B.

    Returns:
        The mutual information (float, non-negative). Returns np.nan on error.

    Raises:
        NotImplementedError: If more than two subsystems are specified in dims.
        ValueError: If inputs (state_vector, dims) are invalid.
    """
    # Currently implemented only for bipartite systems
    if len(dims) != 2:
        raise NotImplementedError("Mutual information calculation currently only supports bipartite systems (len(dims) must be 2).")
    if not all(isinstance(d, int) and d > 0 for d in dims):
        raise ValueError("dims must be a list of two positive integers.")

    try:
        # Ensure input state is normalized
        normalized_state = superposition_state(state_vector)
        total_dim = np.prod(dims)
        if normalized_state.size != total_dim:
            raise ValueError(f"State vector size {normalized_state.size} does not match total dimension {total_dim} from dims {dims}.")
    except (ValueError, TypeError) as e_state:
        raise ValueError(f"Invalid input state vector for mutual information calculation: {e_state}")

    try:
        # Calculate density matrix of the combined system AB
        rho_ab = _density_matrix(normalized_state)
        # Calculate reduced density matrices for subsystems A and B
        rho_a = partial_trace(rho_ab, keep_subsystem=0, dims=dims)
        rho_b = partial_trace(rho_ab, keep_subsystem=1, dims=dims)
    except ValueError as e_trace:
        # Catch errors during density matrix or partial trace calculation
        raise ValueError(f"Error calculating density matrices or partial trace for mutual information: {e_trace}")

    # Calculate Von Neumann entropies for subsystems and combined system
    # For a pure state |psi_AB>, S(AB) = 0
    # S(A) = S(B) for a pure bipartite state (entanglement entropy)
    entropy_rho_a = von_neumann_entropy(rho_a)
    entropy_rho_b = von_neumann_entropy(rho_b)
    # S(AB) = 0 for a pure state. Calculating it serves as a check, but we can assume 0.
    # entropy_rho_ab = von_neumann_entropy(rho_ab) # Should be close to 0 for pure state

    # Check for NaN results from entropy calculations
    if np.isnan(entropy_rho_a) or np.isnan(entropy_rho_b):
        logger.error("NaN entropy encountered during mutual information calculation. Returning NaN.")
        return np.nan

    # Mutual Information I(A:B) = S(A) + S(B) - S(AB)
    # For a pure state, S(AB)=0, so I(A:B) = S(A) + S(B) = 2 * S(A) = 2 * S(B)
    mutual_info = entropy_rho_a + entropy_rho_b # Since S(AB) = 0 for pure state

    # Ensure mutual information is non-negative (within tolerance) and not NaN
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
    """
    Computes the Shannon entropy H(p) = -sum(p_i * log2(p_i)) of the probability
    distribution derived from the squared magnitudes of the state vector components.

    Args:
        quantum_state_vector: A 1D complex NumPy array representing the state vector.

    Returns:
        The Shannon entropy (float, non-negative). Returns np.nan on error.

    Raises:
        ValueError: If the input is not a 1D array.
    """
    state = np.asarray(quantum_state_vector, dtype=complex)
    if state.ndim != 1:
        raise ValueError("Input quantum_state_vector must be 1-dimensional.")

    # Calculate probabilities p_i = |psi_i|^2
    probabilities = np.abs(state)**2

    # Ensure probabilities sum to 1 (within tolerance)
    total_prob = np.sum(probabilities)
    epsilon = 1e-9 # Tolerance for probability sum check
    if not np.isclose(total_prob, 1.0, atol=epsilon):
        logger.warning(f"Input state probabilities sum to {total_prob:.6f}, expected 1. Normalizing probability distribution for entropy calculation.")
        if total_prob > 1e-15: # Avoid division by zero if norm was actually zero
            probabilities /= total_prob
        else:
            logger.error("Input state has zero total probability. Cannot calculate Shannon entropy.")
            return 0.0 # Entropy of zero vector is arguably 0

    # Filter out zero probabilities (log2(0) is undefined)
    tolerance_prob = 1e-15
    non_zero_probs = probabilities[probabilities > tolerance_prob]

    # If only one non-zero probability (or none), entropy is 0
    if len(non_zero_probs) <= 1:
        return 0.0

    try:
        # Calculate Shannon entropy: H = -sum(p_i * log2(p_i))
        entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))
    except FloatingPointError as e_fp:
        logger.error(f"Floating point error during Shannon entropy calculation: {e_fp}. Returning NaN.")
        return np.nan

    # Ensure entropy is non-negative (within tolerance) and not NaN
    if entropy < -1e-12:
        logger.warning(f"Calculated negative Shannon entropy ({entropy:.4g}). Clamping to 0.0.")
        entropy = 0.0
    elif np.isnan(entropy):
        logger.warning("Calculated NaN Shannon entropy. Returning 0.0.")
        entropy = 0.0
    else:
        entropy = max(0.0, entropy) # Ensure non-negativity

    logger.debug(f"Calculated Shannon Entropy: {entropy:.6f}")
    return float(entropy)

# --- END OF FILE 3.0ArchE/quantum_utils.py --- 