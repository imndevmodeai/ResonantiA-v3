import numpy as np
import logging
import json
from scipy.stats import entropy as scipy_entropy, wasserstein_distance
from difflib import SequenceMatcher
from typing import Dict, Any, Optional, Union, List, Tuple
import copy

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Distribution:
    def __init__(self, name: str):
        self.name = name
        self.type = "unknown"
    def update(self, value: Any, *params):
        raise NotImplementedError
    def kld(self, other: 'Distribution') -> Optional[float]:
        return None
    def emd(self, other: 'Distribution') -> Optional[float]:
        return None
    def similarity(self, other: 'Distribution') -> float:
        kld_val = self.kld(other)
        emd_val = self.emd(other)
        sim_score = 0.0
        count = 0
        if kld_val is not None and np.isfinite(kld_val):
            sim_score += np.exp(-abs(kld_val))
            count += 1
        if emd_val is not None and np.isfinite(emd_val):
            sim_score += 1.0 / (1.0 + abs(emd_val))
            count += 1
        return float(sim_score / count) if count > 0 else 0.0
    def get_params(self) -> Dict[str, Any]:
        return {"type": self.type}
    def copy(self) -> 'Distribution':
        return copy.deepcopy(self)

class GaussianDistribution(Distribution):
    def __init__(self, name: str, mean: float, std: float):
        super().__init__(name)
        self.type = "gaussian"
        self.mean = float(mean)
        self.std = float(std)
    def update(self, value: float, observed_std: Optional[float] = None):
        # Simplified update
        self.mean = (self.mean + float(value)) / 2.0
    def kld(self, other: Distribution) -> Optional[float]:
        if not isinstance(other, GaussianDistribution): return None
        s0, s1, m0, m1 = self.std, other.std, self.mean, other.mean
        if s0 <= 0 or s1 <= 0: return np.inf
        # Note: Corrected formula for log base e. For log base 2, a factor is needed.
        # Using natural log for simplicity here.
        return (np.log(s1 / s0) + (s0**2 + (m0 - m1)**2) / (2 * s1**2) - 0.5)
    def emd(self, other: Distribution) -> Optional[float]:
        if not isinstance(other, GaussianDistribution): return None
        return abs(self.mean - other.mean)
    def get_params(self) -> Dict[str, Any]:
        return {"type": self.type, "mean": self.mean, "std": self.std}

class StringParam(Distribution):
    def __init__(self, name: str, value: str):
        super().__init__(name)
        self.type = "string"
        self.value = str(value)
    def update(self, value: Any, *params):
        self.value = str(value)
    def similarity(self, other: Distribution) -> float:
        if isinstance(other, StringParam):
            return SequenceMatcher(None, self.value, other.value).ratio()
        return 0.0
    def get_params(self) -> Dict[str, Any]:
        return {"type": self.type, "value": self.value}

class System:
    def __init__(self, name: str, parameters: Dict[str, Distribution]):
        self.name = name
        self.parameters = parameters
    def similarity(self, other_system: 'System') -> float:
        total_sim = 0.0
        common_params = 0
        for param_name, param1 in self.parameters.items():
            if param_name in other_system.parameters:
                param2 = other_system.parameters[param_name]
                if type(param1) is type(param2):
                    total_sim += param1.similarity(param2)
                    common_params += 1
        return total_sim / common_params if common_params > 0 else 0.0
