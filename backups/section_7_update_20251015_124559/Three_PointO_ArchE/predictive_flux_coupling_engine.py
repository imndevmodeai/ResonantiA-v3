# --- START OF FILE 3.0ArchE/predictive_flux_coupling_engine.py ---
# ResonantiA Protocol v3.1-CA - predictive_flux_coupling_engine.py
# Implements Predictive Flux Coupling (PFC) and Comparative Ensemble Forecasting (CEF)
# Advanced temporal analysis capabilities for CFP framework enhancement
# Returns results including mandatory Integrated Action Reflection (IAR)

import numpy as np
import pandas as pd
import logging
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from collections import deque, defaultdict

# Relative imports for ArchE framework integration
try:
    from .cfp_framework import CfpframeworK
    from .predictive_modeling_tool import run_prediction
    from .adaptive_cognitive_orchestrator import PatternEvolutionEngine
    from . import config
    CFP_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ArchE framework components not available: {e}")
    CFP_AVAILABLE = False

# Scientific computing imports
try:
    from scipy.stats import pearsonr
    from scipy.spatial.distance import jensenshannon
    from sklearn.metrics import mutual_info_score
    from sklearn.feature_selection import mutual_info_regression
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logging.warning("SciPy/sklearn not available, using fallback implementations")

logger = logging.getLogger(__name__)

class PredictiveFluxCouplingEngine:
    """
    Implements Predictive Flux Coupling (PFC) analysis for temporal system dynamics.
    
    PFC quantifies the degree to which flux dynamics of system A predict 
    flux dynamics of system B at future time lags, combining correlation
    and information flow components.
    """
    
    def __init__(self):
        self.analysis_history = deque(maxlen=100)
        self.coupling_cache = {}
        logger.info("[PFC] Predictive Flux Coupling Engine initialized")
    
    def calculate_pfc_metric(
        self,
        flux_a: List[float],
        flux_b: List[float],
        delta: int = 1,
        window_size: int = 20,
        normalize_te: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate Predictive Flux Coupling metric between two flux time series.
        
        Args:
            flux_a: Flux time series for system A (F_A(t))
            flux_b: Flux time series for system B (F_B(t))
            delta: Time lag (prediction horizon)
            window_size: Window size for analysis
            normalize_te: Whether to normalize transfer entropy
            
        Returns:
            Dict containing PFC analysis results and IAR reflection
        """
        start_time = time.time()
        primary_result = {"error": None, "pfc_score": None}
        
        try:
            # Validate inputs
            if len(flux_a) < window_size or len(flux_b) < window_size:
                raise ValueError(f"Insufficient data: need at least {window_size} points")
            
            if delta >= len(flux_b):
                raise ValueError(f"Delta {delta} too large for data length {len(flux_b)}")
            
            # Convert to numpy arrays
            fa = np.array(flux_a, dtype=float)
            fb = np.array(flux_b, dtype=float)
            
            # Calculate time-lagged cross-correlation component
            correlation_component = self._calculate_lagged_correlation(fa, fb, delta, window_size)
            
            # Calculate normalized information flow component
            info_flow_component = self._calculate_transfer_entropy(fa, fb, delta, window_size, normalize_te)
            
            # Combine components for PFC metric
            # PFC = max(0, correlation) * information_flow
            pfc_score = max(0.0, correlation_component) * info_flow_component
            
            # Store results
            primary_result.update({
                "pfc_score": float(pfc_score),
                "correlation_component": float(correlation_component),
                "information_flow_component": float(info_flow_component),
                "delta": delta,
                "window_size": window_size,
                "data_length_a": len(flux_a),
                "data_length_b": len(flux_b),
                "analysis_timestamp": now_iso()
            })
            
            # Generate IAR reflection
            confidence = self._assess_pfc_confidence(fa, fb, pfc_score, correlation_component, info_flow_component)
            
            reflection = {
                "status": "Success",
                "summary": f"PFC analysis completed: score={pfc_score:.4f}, correlation={correlation_component:.4f}, info_flow={info_flow_component:.4f}",
                "confidence": confidence,
                "alignment_check": "Aligned with predictive coupling analysis objective",
                "potential_issues": self._identify_pfc_issues(fa, fb, correlation_component, info_flow_component),
                "processing_time": time.time() - start_time,
                "crystallization_potential": 0.8 if pfc_score > 0.5 else 0.3
            }
            
            # Cache results for pattern learning
            analysis_record = {
                "timestamp": now_iso(),
                "pfc_score": pfc_score,
                "correlation": correlation_component,
                "info_flow": info_flow_component,
                "delta": delta,
                "confidence": confidence
            }
            self.analysis_history.append(analysis_record)
            
            logger.info(f"[PFC] Analysis complete: PFC={pfc_score:.4f}, confidence={confidence:.3f}")
            
        except Exception as e:
            logger.error(f"[PFC] Analysis failed: {e}", exc_info=True)
            primary_result["error"] = str(e)
            reflection = {
                "status": "Failure",
                "summary": f"PFC analysis failed: {e}",
                "confidence": 0.0,
                "alignment_check": "Failed to complete analysis",
                "potential_issues": [f"Calculation error: {e}"],
                "processing_time": time.time() - start_time,
                "crystallization_potential": 0.0
            }
        
        primary_result["reflection"] = reflection
        return primary_result
    
    def _calculate_lagged_correlation(
        self, 
        flux_a: np.ndarray, 
        flux_b: np.ndarray, 
        delta: int, 
        window_size: int
    ) -> float:
        """Calculate time-lagged cross-correlation component C_AB(δ, W, T)"""
        try:
            # Ensure we have enough data for the lag
            end_idx = len(flux_a) - delta
            if end_idx < window_size:
                return 0.0
            
            # Extract windowed data
            start_idx = max(0, end_idx - window_size)
            fa_window = flux_a[start_idx:end_idx]
            fb_lagged_window = flux_b[start_idx + delta:end_idx + delta]
            
            # Calculate Pearson correlation
            if SCIPY_AVAILABLE:
                correlation, p_value = pearsonr(fa_window, fb_lagged_window)
                return correlation if not np.isnan(correlation) else 0.0
            else:
                # Fallback correlation calculation
                return np.corrcoef(fa_window, fb_lagged_window)[0, 1]
                
        except Exception as e:
            logger.warning(f"[PFC] Correlation calculation failed: {e}")
            return 0.0
    
    def _calculate_transfer_entropy(
        self, 
        flux_a: np.ndarray, 
        flux_b: np.ndarray, 
        delta: int, 
        window_size: int,
        normalize: bool = True
    ) -> float:
        """Calculate normalized information flow component I_AB(δ, W, T)"""
        try:
            # Simplified transfer entropy estimation using mutual information
            # This is a practical approximation of the full TE calculation
            
            end_idx = len(flux_a) - delta
            if end_idx < window_size:
                return 0.0
            
            start_idx = max(0, end_idx - window_size)
            
            # Prepare data for transfer entropy approximation
            fa_window = flux_a[start_idx:end_idx]
            fb_current = flux_b[start_idx:end_idx]
            fb_future = flux_b[start_idx + delta:end_idx + delta]
            
            if SCIPY_AVAILABLE:
                # Use sklearn's mutual information as TE approximation
                # TE ≈ MI(F_B(t+δ), F_A(t)) - MI(F_B(t+δ), F_B(t))
                mi_a_to_b_future = mutual_info_score(
                    self._discretize_signal(fa_window),
                    self._discretize_signal(fb_future)
                )
                mi_b_to_b_future = mutual_info_score(
                    self._discretize_signal(fb_current),
                    self._discretize_signal(fb_future)
                )
                
                te_estimate = max(0.0, mi_a_to_b_future - mi_b_to_b_future)
                
                if normalize and mi_a_to_b_future > 0:
                    # Normalize by the entropy of the target
                    entropy_b_future = self._calculate_entropy(fb_future)
                    te_normalized = te_estimate / entropy_b_future if entropy_b_future > 0 else 0.0
                    return min(1.0, te_normalized)
                else:
                    return min(1.0, te_estimate)
            else:
                # Fallback: simplified correlation-based information flow
                corr_direct = np.corrcoef(fa_window, fb_future)[0, 1]
                corr_auto = np.corrcoef(fb_current, fb_future)[0, 1]
                return max(0.0, abs(corr_direct) - abs(corr_auto))
                
        except Exception as e:
            logger.warning(f"[PFC] Transfer entropy calculation failed: {e}")
            return 0.0
    
    def _discretize_signal(self, signal: np.ndarray, bins: int = 10) -> np.ndarray:
        """Discretize continuous signal for mutual information calculation"""
        try:
            # Use quantile-based binning for robust discretization
            quantiles = np.linspace(0, 1, bins + 1)
            bin_edges = np.quantile(signal, quantiles)
            bin_edges[-1] += 1e-10  # Ensure last bin includes maximum value
            discretized = np.digitize(signal, bin_edges) - 1
            return np.clip(discretized, 0, bins - 1)
        except Exception:
            # Fallback to simple linear binning
            return np.digitize(signal, bins=bins) - 1
    
    def _calculate_entropy(self, signal: np.ndarray) -> float:
        """Calculate Shannon entropy of discretized signal"""
        try:
            discretized = self._discretize_signal(signal)
            values, counts = np.unique(discretized, return_counts=True)
            probabilities = counts / len(discretized)
            entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
            return entropy
        except Exception:
            return 0.0
    
    def _assess_pfc_confidence(
        self, 
        flux_a: np.ndarray, 
        flux_b: np.ndarray, 
        pfc_score: float,
        correlation: float,
        info_flow: float
    ) -> float:
        """Assess confidence in PFC analysis results"""
        confidence_factors = []
        
        # Data quality factor
        data_quality = min(1.0, len(flux_a) / 50.0)  # More data = higher confidence
        confidence_factors.append(data_quality)
        
        # Signal stability factor
        stability_a = 1.0 - (np.std(flux_a) / (np.mean(np.abs(flux_a)) + 1e-10))
        stability_b = 1.0 - (np.std(flux_b) / (np.mean(np.abs(flux_b)) + 1e-10))
        stability_factor = (stability_a + stability_b) / 2.0
        confidence_factors.append(max(0.1, min(1.0, stability_factor)))
        
        # Coupling strength factor
        coupling_strength = min(1.0, pfc_score * 2.0)  # Higher PFC = higher confidence
        confidence_factors.append(coupling_strength)
        
        # Component consistency factor
        component_consistency = 1.0 - abs(correlation - info_flow) / 2.0
        confidence_factors.append(max(0.1, component_consistency))
        
        return np.mean(confidence_factors)
    
    def _identify_pfc_issues(
        self, 
        flux_a: np.ndarray, 
        flux_b: np.ndarray,
        correlation: float,
        info_flow: float
    ) -> List[str]:
        """Identify potential issues with PFC analysis"""
        issues = []
        
        if len(flux_a) < 30:
            issues.append("Limited data may affect reliability")
        
        if abs(correlation) < 0.1:
            issues.append("Very weak correlation detected")
        
        if info_flow < 0.1:
            issues.append("Low information flow detected")
        
        if np.std(flux_a) < 1e-6 or np.std(flux_b) < 1e-6:
            issues.append("Signal may be too stable/constant for meaningful analysis")
        
        if not SCIPY_AVAILABLE:
            issues.append("Using fallback methods due to missing scipy/sklearn")
        
        return issues if issues else None

# Integration function for ArchE action registry
def run_predictive_flux_analysis(operation: str, **kwargs) -> Dict[str, Any]:
    """
    Main entry point for predictive flux analysis operations.
    Integrates PFC and CEF capabilities with ArchE's action system.
    """
    logger.info(f"[PredictiveFlux] Running operation: {operation}")
    
    if operation == "calculate_pfc":
        engine = PredictiveFluxCouplingEngine()
        return engine.calculate_pfc_metric(**kwargs)
    
    else:
        return {
            "error": f"Unknown predictive flux operation: {operation}",
            "reflection": {
                "status": "Failure",
                "summary": f"Unknown operation: {operation}",
                "confidence": 0.0,
                "alignment_check": "Failed - unknown operation",
                "potential_issues": [f"Operation '{operation}' not implemented"]
            }
        }

# --- END OF FILE ---
