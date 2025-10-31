# --- START OF FILE 3.0ArchE/system_representation.py ---
# ResonantiA Protocol v3.0 - system_representation.py
# Defines classes for representing systems and their parameters using distributions.
# Enhanced in v3.0: System history now includes timestamps for temporal analysis.

import numpy as np
import copy
import time # Added for timestamping history
from scipy.stats import entropy, wasserstein_distance # For KLD and EMD
from typing import Dict, Any, Optional, List, Union, Tuple # Expanded type hints

class Distribution:
    """Base class for parameter distributions."""
    def __init__(self, name: str):
        self.name = name

    def update(self, value: Any):
        """Update the distribution with a new value."""
        raise NotImplementedError

    def get_value(self) -> Any:
        """Return the current representative value (e.g., mean)."""
        raise NotImplementedError

    def get_probabilities(self, num_bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Return probability distribution and bin edges/centers."""
        raise NotImplementedError

    def kl_divergence(self, other: 'Distribution', num_bins: int = 10) -> float:
        """Calculate Kullback-Leibler divergence to another distribution."""
        p_probs, _ = self.get_probabilities(num_bins)
        q_probs, _ = other.get_probabilities(num_bins)
        # Add small epsilon to avoid log(0) and division by zero
        epsilon = 1e-9
        p_probs = np.maximum(p_probs, epsilon)
        q_probs = np.maximum(q_probs, epsilon)
        # Ensure normalization (though get_probabilities should handle it)
        p_probs /= p_probs.sum()
        q_probs /= q_probs.sum()
        return entropy(p_probs, q_probs)

    def earth_movers_distance(self, other: 'Distribution', num_bins: int = 10) -> float:
        """Calculate Earth Mover's Distance (Wasserstein distance) to another distribution."""
        # Note: Requires values associated with probabilities for wasserstein_distance
        # This implementation might be simplified or need adjustment based on how bins are handled
        p_probs, p_bins = self.get_probabilities(num_bins)
        q_probs, q_bins = other.get_probabilities(num_bins)
        # Assuming bins represent values for wasserstein_distance (needs careful check)
        # Use bin centers as values
        p_values = (p_bins[:-1] + p_bins[1:]) / 2 if len(p_bins) > 1 else p_bins
        q_values = (q_bins[:-1] + q_bins[1:]) / 2 if len(q_bins) > 1 else q_bins
        # Ensure lengths match for wasserstein_distance if using values directly
        # A common approach is to use the combined range and resample/interpolate,
        # but for simplicity here, we'll assume the bins are comparable if lengths match.
        # If lengths differ, EMD calculation might be inaccurate or fail.
        # A more robust implementation might require resampling onto a common grid.
        if len(p_values) == len(q_values):
             # Use scipy.stats.wasserstein_distance which works on samples or distributions
             # We pass the probabilities (weights) and the corresponding values (bin centers)
             # Note: wasserstein_distance expects 1D arrays of values. If using probabilities directly,
             # it assumes values are indices [0, 1, ..., n-1]. Using bin centers is more appropriate.
             try:
                 # Ensure probabilities sum to 1
                 p_probs_norm = p_probs / p_probs.sum() if p_probs.sum() > 0 else p_probs
                 q_probs_norm = q_probs / q_probs.sum() if q_probs.sum() > 0 else q_probs
                 # Calculate EMD between the two distributions represented by values and weights
                 return wasserstein_distance(p_values, q_values, u_weights=p_probs_norm, v_weights=q_probs_norm)
             except Exception as e_emd:
                 print(f"Warning: EMD calculation failed: {e_emd}. Returning infinity.")
                 return float('inf')
        else:
            print(f"Warning: Bin lengths differ for EMD calculation ({len(p_values)} vs {len(q_values)}). Returning infinity.")
            return float('inf') # Indicate incompatibility or error

    def similarity(self, other: 'Distribution', num_bins: int = 10) -> float:
        """Calculate similarity based on KL divergence (exp(-KL)). Higher is more similar."""
        kl = self.kl_divergence(other, num_bins)
        return np.exp(-kl) if kl != float('inf') else 0.0

class GaussianDistribution(Distribution):
    """Represents a Gaussian distribution."""
    def __init__(self, name: str, mean: float = 0.0, std_dev: float = 1.0):
        super().__init__(name)
        self.mean = float(mean)
        self.std_dev = float(std_dev)
        if self.std_dev <= 0:
            raise ValueError("Standard deviation must be positive.")
        self._update_count = 0 # Track updates for potential adaptive std dev

    def update(self, value: float):
        """Update mean and std dev using Welford's online algorithm (simplified)."""
        # Simplified: Just update mean for now. Proper online update is more complex.
        # A more robust implementation would update variance/std_dev as well.
        try:
            new_val = float(value)
            self._update_count += 1
            # Simple moving average for mean (can be improved)
            self.mean = ((self._update_count - 1) * self.mean + new_val) / self._update_count
            # Placeholder for std dev update - could use Welford's online algorithm
            # self.std_dev = ...
        except (ValueError, TypeError):
            print(f"Warning: Invalid value '{value}' provided for Gaussian update. Ignoring.")

    def get_value(self) -> float:
        return self.mean

    def get_probabilities(self, num_bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Return probability densities over bins based on Gaussian PDF."""
        # Define range (e.g., mean +/- 3*std_dev)
        min_val = self.mean - 3 * self.std_dev
        max_val = self.mean + 3 * self.std_dev
        bins = np.linspace(min_val, max_val, num_bins + 1)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        # Calculate PDF values at bin centers (approximation)
        pdf_values = (1 / (self.std_dev * np.sqrt(2 * np.pi))) * \
                     np.exp(-0.5 * ((bin_centers - self.mean) / self.std_dev)**2)
        # Normalize probabilities (area under PDF for bins)
        bin_width = bins[1] - bins[0]
        probabilities = pdf_values * bin_width
        # Ensure sum to 1 (due to approximation/finite range)
        prob_sum = probabilities.sum()
        if prob_sum > 1e-9: probabilities /= prob_sum
        return probabilities, bins

class HistogramDistribution(Distribution):
    """Represents a distribution using a histogram."""
    def __init__(self, name: str, bins: int = 10, range_min: float = 0.0, range_max: float = 1.0):
        super().__init__(name)
        self.num_bins = int(bins)
        self.range_min = float(range_min)
        self.range_max = float(range_max)
        if self.range_min >= self.range_max: raise ValueError("range_min must be less than range_max.")
        if self.num_bins <= 0: raise ValueError("Number of bins must be positive.")
        # Initialize histogram counts and bin edges
        self.counts = np.zeros(self.num_bins, dtype=int)
        self.bin_edges = np.linspace(self.range_min, self.range_max, self.num_bins + 1)
        self.total_count = 0

    def update(self, value: float):
        """Increment the count of the bin the value falls into."""
        try:
            val = float(value)
            # Find the appropriate bin index
            # Clip value to range to handle edge cases
            val_clipped = np.clip(val, self.range_min, self.range_max)
            # Calculate bin index (handle value exactly equal to range_max)
            bin_index = np.searchsorted(self.bin_edges, val_clipped, side='right') - 1
            bin_index = max(0, min(bin_index, self.num_bins - 1)) # Ensure index is valid

            self.counts[bin_index] += 1
            self.total_count += 1
        except (ValueError, TypeError):
            print(f"Warning: Invalid value '{value}' provided for Histogram update. Ignoring.")

    def get_value(self) -> float:
        """Return the mean value based on the histogram."""
        if self.total_count == 0: return (self.range_min + self.range_max) / 2 # Return center if no data
        bin_centers = (self.bin_edges[:-1] + self.bin_edges[1:]) / 2
        return np.average(bin_centers, weights=self.counts)

    def get_probabilities(self, num_bins: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Return normalized probabilities from histogram counts."""
        # Ignore num_bins argument, use internal bins
        if self.total_count == 0:
            # Return uniform distribution if no data
            probabilities = np.ones(self.num_bins) / self.num_bins
        else:
            probabilities = self.counts / self.total_count
        return probabilities, self.bin_edges

class StringParam(Distribution):
    """Represents a categorical/string parameter."""
    def __init__(self, name: str, value: str = ""):
        super().__init__(name)
        self.value = str(value)

    def update(self, value: Any):
        self.value = str(value)

    def get_value(self) -> str:
        return self.value

    def get_probabilities(self, num_bins: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Returns a degenerate distribution (1.0 probability for current value)."""
        # Represent as a single bin with probability 1.0
        # Bins are not meaningful here, return value as 'bin'
        return np.array([1.0]), np.array([self.value]) # Return value itself instead of bin edges

    def kl_divergence(self, other: 'Distribution', num_bins: int = 10) -> float:
        """KL divergence for strings: 0 if equal, infinity otherwise."""
        if isinstance(other, StringParam) and self.value == other.value:
            return 0.0
        else:
            return float('inf')

    def earth_movers_distance(self, other: 'Distribution', num_bins: int = 10) -> float:
        """EMD for strings: 0 if equal, 1 otherwise (simple distance)."""
        if isinstance(other, StringParam) and self.value == other.value:
            return 0.0
        else:
            # Define a simple distance (e.g., 1) if strings are different
            return 1.0

    def similarity(self, other: 'Distribution', num_bins: int = 10) -> float:
        """Similarity for strings: 1 if equal, 0 otherwise."""
        return 1.0 if isinstance(other, StringParam) and self.value == other.value else 0.0


class System:
    """Represents a system with named parameters defined by distributions."""
    def __init__(self, system_id: str, name: str):
        self.system_id = system_id
        self.name = name
        self.parameters: Dict[str, Distribution] = {}
        # History stores tuples of (timestamp, state_dict)
        self.history: List[Tuple[float, Dict[str, Distribution]]] = []
        self.last_update_time: Optional[float] = None

    def add_parameter(self, param: Distribution):
        """Adds a parameter distribution to the system."""
        if not isinstance(param, Distribution):
            raise TypeError("Parameter must be an instance of Distribution or its subclass.")
        self.parameters[param.name] = param

    def update_state(self, new_state: Dict[str, Any]):
        """Updates the state of system parameters and records history with timestamp."""
        current_time = time.time() # Get current timestamp
        # Record current state in history *before* updating
        if self.parameters: # Only record if parameters exist
            try:
                # Store timestamp along with deep copy of current state
                self.history.append((self.last_update_time or current_time, copy.deepcopy(self.parameters)))
                # Limit history size if needed (e.g., keep last 10 states)
                # max_history = 10
                # if len(self.history) > max_history: self.history.pop(0)
            except Exception as e_copy:
                print(f"Warning: Could not deepcopy state for history recording: {e_copy}")

        # Update parameters with new values
        for name, value in new_state.items():
            if name in self.parameters:
                try:
                    self.parameters[name].update(value)
                except Exception as e_update:
                    print(f"Warning: Failed to update parameter '{name}' with value '{value}': {e_update}")
            else:
                print(f"Warning: Parameter '{name}' not found in system '{self.name}'. Ignoring update.")
        self.last_update_time = current_time # Update last update time

    def get_state(self) -> Dict[str, Any]:
        """Returns the current state of the system as a dictionary of values."""
        return {name: param.get_value() for name, param in self.parameters.items()}

    def get_parameter(self, name: str) -> Optional[Distribution]:
        """Retrieves a parameter by name."""
        return self.parameters.get(name)

    def get_history(self) -> List[Tuple[float, Dict[str, Distribution]]]:
        """Returns the recorded state history."""
        return self.history

    def compare(self, other_system: 'System') -> List[Dict[str, Any]]:
        """
        Compares this system with another, parameter by parameter.
        Returns a list of dictionaries detailing the comparison.
        """
        comparison_report = []
        all_param_names = set(self.parameters.keys()) | set(other_system.parameters.keys())

        for name in sorted(list(all_param_names)):
            param_a = self.get_parameter(name)
            param_b = other_system.get_parameter(name)
            
            report_item = {"parameter": name}

            if param_a and param_b:
                if type(param_a) is not type(param_b):
                    report_item.update({
                        "comparison_type": "TYPE_MISMATCH",
                        "system_a_type": param_a.__class__.__name__,
                        "system_b_type": param_b.__class__.__name__,
                    })
                else:
                    val_a = param_a.get_value()
                    val_b = param_b.get_value()
                    if val_a == val_b:
                        report_item.update({
                            "comparison_type": "IDENTICAL",
                            "value": val_a
                        })
                    else:
                        report_item.update({
                            "comparison_type": "VALUE_DIFFERENCE",
                            "system_a_value": val_a,
                            "system_b_value": val_b
                        })
            elif param_a and not param_b:
                report_item.update({
                    "comparison_type": "ONLY_IN_A",
                    "system_a_value": param_a.get_value()
                })
            elif not param_a and param_b:
                report_item.update({
                    "comparison_type": "ONLY_IN_B",
                    "system_b_value": param_b.get_value()
                })
            comparison_report.append(report_item)
        return comparison_report

    def calculate_divergence(self, other_system: 'System', method: str = 'kld', num_bins: int = 10) -> float:
        """Calculates aggregate divergence between this system and another."""
        total_divergence = 0.0
        common_params = 0
        for name, param in self.parameters.items():
            other_param = other_system.get_parameter(name)
            if other_param and type(param) == type(other_param): # Ensure types match for comparison
                try:
                    if method.lower() == 'kld':
                        div = param.kl_divergence(other_param, num_bins)
                    elif method.lower() == 'emd':
                        div = param.earth_movers_distance(other_param, num_bins)
                    else:
                        print(f"Warning: Unknown divergence method '{method}'. Skipping parameter '{name}'.")
                        continue
                    # Handle infinite divergence (e.g., non-overlapping support or string mismatch)
                    if div == float('inf'):
                        # Assign a large penalty for infinite divergence, or handle as needed
                        total_divergence += 1e6 # Large penalty
                    else:
                        total_divergence += div
                    common_params += 1
                except Exception as e_div:
                    print(f"Warning: Could not calculate {method} for parameter '{name}': {e_div}")
            elif other_param:
                 print(f"Warning: Type mismatch for parameter '{name}' ({type(param)} vs {type(other_param)}). Skipping divergence calculation.")

        return total_divergence / common_params if common_params > 0 else 0.0

    def calculate_similarity(self, other_system: 'System', num_bins: int = 10) -> float:
        """Calculates aggregate similarity based on KL divergence."""
        total_similarity = 0.0
        common_params = 0
        for name, param in self.parameters.items():
            other_param = other_system.get_parameter(name)
            if other_param and type(param) == type(other_param):
                try:
                    sim = param.similarity(other_param, num_bins)
                    total_similarity += sim
                    common_params += 1
                except Exception as e_sim:
                     print(f"Warning: Could not calculate similarity for parameter '{name}': {e_sim}")
            elif other_param:
                 print(f"Warning: Type mismatch for parameter '{name}' ({type(param)} vs {type(other_param)}). Skipping similarity calculation.")

        return total_similarity / common_params if common_params > 0 else 0.0

# --- END OF FILE 3.0ArchE/system_representation.py --- 