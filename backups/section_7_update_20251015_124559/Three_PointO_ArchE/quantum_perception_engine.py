#!/usr/bin/env python3
"""
Quantum Perception Engine - The Sixth Sense
A Universal Organ for Quantum-Based Systemic Analysis

This module implements quantum-inspired perception for complex, entangled systems.
Instead of treating agents/features as independent variables (classical approach),
it models them as entangled quantum states whose interactions create emergent behavior.

Crystallized from Guardian Wisdom: B.J. Lewis
Source Insight: NFL Quantum Prediction Analysis (2025-01-09)
Universal Abstraction: Multi-agent entangled dynamics → Any complex system

Core Components:
1. QuantumLensGrinder - Normalize heterogeneous metrics to pure probability space
2. OpticNervePipeline - Transform reality into quantum-ready feature vectors
3. QuantumRetina - N-qubit circuits modeling system entanglement

Applications:
- NFL outcome prediction (source domain)
- Network health quantum modeling
- Adversary cascade simulation  
- RISE quantum scenario analysis
- Any multi-agent entangled system

Protocol: ResonantiA v3.5-GP + Autopoietic Learning Loop
Status: Galaxy (Crystallized Wisdom)
"""

import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime

# ============================================================================
# TEMPORAL CORE INTEGRATION (CANONICAL DATETIME SYSTEM)
# ============================================================================
from .temporal_core import now_iso, format_filename, format_log, Timer
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Quantum computing imports with graceful fallback
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit_aer import Aer
    from qiskit.compiler import transpile
    QISKIT_AVAILABLE = True
    logger.info("✅ Qiskit available - Full quantum simulation enabled")
except ImportError:
    QISKIT_AVAILABLE = False
    logger.warning("⚠️ Qiskit not available - Using classical approximation fallback")
    # Create mock classes for type hints
    class QuantumCircuit:
        pass
    class QuantumRegister:
        pass
    class ClassicalRegister:
        pass


@dataclass
class QuantumPerceptionResult:
    """
    Result of quantum perception analysis.
    
    Attributes:
        prediction: Primary prediction value (e.g., win probability)
        confidence: Confidence in prediction (0.0-1.0)
        quantum_state: String representation of quantum state
        entanglement_strength: Measure of feature entanglement (0.0-1.0)
        classical_baseline: Comparison to classical independent model
        metadata: Additional context and diagnostics
    """
    prediction: float
    confidence: float
    quantum_state: str
    entanglement_strength: float
    classical_baseline: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "prediction": self.prediction,
            "confidence": self.confidence,
            "quantum_state": self.quantum_state,
            "entanglement_strength": self.entanglement_strength,
            "classical_baseline": self.classical_baseline,
            "metadata": self.metadata
        }


class QuantumLensGrinder:
    """
    The Lens Grinder - Calibrates perception for mathematical purity.
    
    Transforms heterogeneous metrics (speed in mph, separation in yards, etc.)
    into a unified probability space where all values sum to exactly 1.0.
    
    This prevents the "distorted lens" problem where incompatible scales
    create false perceptions.
    
    Philosophy:
    "Before we can perceive quantum truth, we must grind pure lenses
    from the rough glass of reality's heterogeneous measurements."
    """
    
    def __init__(self):
        """Initialize the lens grinder."""
        logger.info("[LensGrinder] Initialized - Ready to calibrate perception")
    
    def normalize_to_probs(
        self,
        values: Union[List[float], np.ndarray],
        scale: str = 'linear',
        clamp: Tuple[float, float] = (0.01, 0.99),
        weights: Optional[List[float]] = None
    ) -> np.ndarray:
        """
        Grind raw values into pure probability lenses.
        
        Args:
            values: Raw heterogeneous measurements
            scale: Transformation scale ('linear', 'log', 'sigmoid')
            clamp: Min/max bounds to prevent extreme values
            weights: Optional importance weights for each value
            
        Returns:
            Normalized probabilities summing to exactly 1.0
        """
        values = np.array(values, dtype=float)
        
        # Handle edge cases
        if len(values) == 0:
            return np.array([])
        if len(values) == 1:
            return np.array([1.0])
        
        # Apply transformation scale
        if scale == 'log':
            # Log scale for exponential-like data
            values = np.log1p(np.abs(values))  # log(1+x) for stability
        elif scale == 'sigmoid':
            # Sigmoid for bounded data
            values = 1 / (1 + np.exp(-values))
        # else: linear (default)
        
        # Apply weights if provided
        if weights is not None:
            weights = np.array(weights, dtype=float)
            if len(weights) != len(values):
                logger.warning(f"Weight length mismatch: {len(weights)} vs {len(values)}")
            else:
                values = values * weights
        
        # Normalize to sum to 1.0
        total = np.sum(values)
        if total == 0:
            # Uniform distribution if all zeros
            probs = np.ones(len(values)) / len(values)
        else:
            probs = values / total
        
        # Clamp to prevent extreme probabilities
        min_prob, max_prob = clamp
        probs = np.clip(probs, min_prob, max_prob)
        
        # Re-normalize after clamping
        probs = probs / np.sum(probs)
        
        # Verify mathematical purity
        prob_sum = np.sum(probs)
        if not np.isclose(prob_sum, 1.0, atol=1e-6):
            logger.warning(f"[LensGrinder] Impure lens detected: sum={prob_sum:.6f}, re-grinding")
            probs = probs / prob_sum  # Force exact normalization
        
        logger.debug(f"[LensGrinder] Ground {len(values)} values into pure lens (sum={np.sum(probs):.6f})")
        return probs
    
    def grind_feature_vector(
        self,
        features: Dict[str, float],
        scale_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """
        Grind a dictionary of heterogeneous features into normalized probabilities.
        
        Args:
            features: Dictionary of feature_name -> raw_value
            scale_map: Optional mapping of feature_name -> scale_type
            
        Returns:
            Dictionary of feature_name -> normalized_probability
        """
        if not features:
            return {}
        
        feature_names = list(features.keys())
        raw_values = [features[k] for k in feature_names]
        
        # Apply per-feature scaling if provided
        if scale_map:
            processed_values = []
            for name, value in zip(feature_names, raw_values):
                scale = scale_map.get(name, 'linear')
                # Scale individual value
                if scale == 'log':
                    processed_values.append(np.log1p(abs(value)))
                elif scale == 'sigmoid':
                    processed_values.append(1 / (1 + np.exp(-value)))
                else:
                    processed_values.append(value)
            raw_values = processed_values
        
        # Normalize across all features
        probs = self.normalize_to_probs(raw_values)
        
        # Return as dictionary
        return {name: float(prob) for name, prob in zip(feature_names, probs)}


class OpticNervePipeline:
    """
    The Optic Nerve - Connects reality to quantum perception.
    
    Ingests raw data from the real world and transforms it into
    quantum-ready feature vectors (probability distributions).
    
    This is the living data stream that feeds quantum simulation
    with the "stardust" of reality.
    
    Philosophy:
    "The optic nerve does not see - it translates. It converts
    the photons of reality into the electrical signals of thought."
    """
    
    def __init__(self, lens_grinder: Optional[QuantumLensGrinder] = None):
        """
        Initialize the optic nerve pipeline.
        
        Args:
            lens_grinder: Optional custom lens grinder (uses default if None)
        """
        self.lens_grinder = lens_grinder or QuantumLensGrinder()
        self.pipeline_history = []
        logger.info("[OpticNerve] Initialized - Ready to ingest reality")
    
    def ingest_raw_data(
        self,
        data: Dict[str, Any],
        aggregation_func: Optional[Callable] = None
    ) -> Dict[str, float]:
        """
        Ingest raw data and perform initial aggregation.
        
        Args:
            data: Raw data dictionary (can be nested, lists, etc.)
            aggregation_func: Optional custom aggregation function
            
        Returns:
            Aggregated feature dictionary (flat)
        """
        if aggregation_func:
            return aggregation_func(data)
        
        # Default aggregation: flatten and compute statistics
        aggregated = {}
        
        for key, value in data.items():
            if isinstance(value, (list, np.ndarray)):
                # Aggregate lists/arrays
                arr = np.array(value)
                if len(arr) > 0:
                    aggregated[f"{key}_mean"] = float(np.mean(arr))
                    aggregated[f"{key}_max"] = float(np.max(arr))
                    aggregated[f"{key}_min"] = float(np.min(arr))
                    aggregated[f"{key}_std"] = float(np.std(arr))
            elif isinstance(value, (int, float)):
                # Direct numeric values
                aggregated[key] = float(value)
            elif isinstance(value, dict):
                # Nested dict - recurse
                nested = self.ingest_raw_data(value, aggregation_func)
                for nested_key, nested_val in nested.items():
                    aggregated[f"{key}_{nested_key}"] = nested_val
        
        return aggregated
    
    def extract_features(
        self,
        aggregated_data: Dict[str, float],
        feature_map: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Extract and combine features according to a feature map.
        
        Args:
            aggregated_data: Flat dictionary of aggregated values
            feature_map: Maps output_feature -> list of input keys to combine
            
        Returns:
            Extracted feature dictionary
        """
        extracted = {}
        
        for output_key, input_keys in feature_map.items():
            values = []
            for input_key in input_keys:
                if input_key in aggregated_data:
                    values.append(aggregated_data[input_key])
            
            if values:
                # Combine multiple inputs (default: mean)
                extracted[output_key] = float(np.mean(values))
        
        return extracted
    
    def transform_to_quantum_ready(
        self,
        features: Dict[str, float],
        scale_map: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """
        Transform features into quantum-ready probability vectors.
        
        Args:
            features: Extracted feature dictionary
            scale_map: Optional per-feature scaling specifications
            
        Returns:
            Normalized probability vectors ready for quantum encoding
        """
        quantum_ready = self.lens_grinder.grind_feature_vector(features, scale_map)
        
        # Log the transformation
        self.pipeline_history.append({
            "timestamp": now_iso(),
            "input_features": features,
            "output_probs": quantum_ready
        })
        
        logger.debug(f"[OpticNerve] Transformed {len(features)} features into quantum-ready probabilities")
        return quantum_ready
    
    def full_pipeline(
        self,
        raw_data: Dict[str, Any],
        feature_map: Optional[Dict[str, List[str]]] = None,
        scale_map: Optional[Dict[str, str]] = None,
        aggregation_func: Optional[Callable] = None
    ) -> Dict[str, float]:
        """
        Execute the complete optic nerve pipeline: raw data → quantum-ready probabilities.
        
        Args:
            raw_data: Raw input data from reality
            feature_map: Optional feature extraction specification
            scale_map: Optional per-feature scaling specifications
            aggregation_func: Optional custom aggregation function
            
        Returns:
            Quantum-ready probability vectors
        """
        # Step 1: Ingest and aggregate
        aggregated = self.ingest_raw_data(raw_data, aggregation_func)
        
        # Step 2: Extract features (if map provided, otherwise use aggregated directly)
        if feature_map:
            features = self.extract_features(aggregated, feature_map)
        else:
            features = aggregated
        
        # Step 3: Transform to quantum-ready probabilities
        quantum_ready = self.transform_to_quantum_ready(features, scale_map)
        
        logger.info(f"[OpticNerve] Pipeline complete: {len(raw_data)} inputs → {len(quantum_ready)} quantum features")
        return quantum_ready


class QuantumRetina:
    """
    The Quantum Retina - Where perception becomes insight.
    
    Models complex systems as N-qubit quantum circuits where qubits represent
    agents/features and entanglement operations capture their interactions.
    
    Unlike classical models that treat variables as independent, this models
    the entangled web of relationships that creates emergent behavior.
    
    Philosophy:
    "Classical eyes see parts. Quantum eyes see the whole.
    In entanglement, we perceive not what things are, but how they dance together."
    """
    
    def __init__(self, num_qubits: int = 4, shots: int = 1024):
        """
        Initialize the quantum retina.
        
        Args:
            num_qubits: Number of qubits (system dimensions)
            shots: Number of quantum measurements for statistics
        """
        self.num_qubits = num_qubits
        self.shots = shots
        self.circuit_history = []
        
        # Initialize quantum backend
        if QISKIT_AVAILABLE:
            self.backend = Aer.get_backend('qasm_simulator')
            logger.info(f"[QuantumRetina] Initialized with {num_qubits} qubits (Qiskit backend)")
        else:
            self.backend = None
            logger.info(f"[QuantumRetina] Initialized with {num_qubits} qubits (Classical approximation)")
    
    def create_entangled_circuit(
        self,
        feature_probs: List[float],
        entanglement_pattern: str = 'cascade'
    ) -> Optional[QuantumCircuit]:
        """
        Create a quantum circuit with entangled qubits representing system features.
        
        Args:
            feature_probs: Probability for each qubit/feature (length must match num_qubits)
            entanglement_pattern: How to entangle qubits ('cascade', 'star', 'mesh')
            
        Returns:
            Quantum circuit ready for simulation (or None if Qiskit unavailable)
        """
        if not QISKIT_AVAILABLE:
            logger.warning("[QuantumRetina] Qiskit unavailable - cannot create real quantum circuit")
            return None
        
        if len(feature_probs) != self.num_qubits:
            logger.error(f"Feature probability length mismatch: {len(feature_probs)} vs {self.num_qubits}")
            return None
        
        # Create quantum circuit
        qr = QuantumRegister(self.num_qubits, 'q')
        cr = ClassicalRegister(self.num_qubits, 'c')
        qc = QuantumCircuit(qr, cr)
        
        # Initialize each qubit in superposition based on feature probabilities
        for i, prob in enumerate(feature_probs):
            # RY rotation to encode probability
            # angle = 2 * arcsin(sqrt(prob))
            angle = 2 * np.arcsin(np.sqrt(np.clip(prob, 0, 1)))
            qc.ry(angle, qr[i])
        
        # Apply entanglement pattern
        if entanglement_pattern == 'cascade':
            # Each qubit entangles with the next: 0→1→2→3
            for i in range(self.num_qubits - 1):
                qc.cx(qr[i], qr[i+1])
        
        elif entanglement_pattern == 'star':
            # First qubit (hub) entangles with all others
            for i in range(1, self.num_qubits):
                qc.cx(qr[0], qr[i])
        
        elif entanglement_pattern == 'mesh':
            # Full mesh - every qubit entangles with every other
            for i in range(self.num_qubits):
                for j in range(i+1, self.num_qubits):
                    qc.cx(qr[i], qr[j])
        
        # Measure all qubits
        qc.measure(qr, cr)
        
        # Store in history
        self.circuit_history.append({
            "timestamp": now_iso(),
            "feature_probs": feature_probs,
            "entanglement_pattern": entanglement_pattern,
            "circuit_depth": qc.depth()
        })
        
        logger.debug(f"[QuantumRetina] Created circuit: {entanglement_pattern} pattern, depth={qc.depth()}")
        return qc
    
    def simulate_perception(
        self,
        circuit: Optional[QuantumCircuit],
        feature_probs: List[float]
    ) -> Dict[str, int]:
        """
        Simulate quantum measurement to perceive system state.
        
        Args:
            circuit: Quantum circuit to simulate
            feature_probs: Feature probabilities (for classical fallback)
            
        Returns:
            Measurement counts dictionary
        """
        if QISKIT_AVAILABLE and circuit is not None:
            # Real quantum simulation
            transpiled = transpile(circuit, self.backend)
            job = self.backend.run(transpiled, shots=self.shots)
            result = job.result()
            counts = result.get_counts()
            logger.debug(f"[QuantumRetina] Quantum simulation complete: {len(counts)} unique states observed")
            return counts
        else:
            # Classical approximation fallback
            logger.debug("[QuantumRetina] Using classical approximation")
            # Simulate by sampling from probability distribution
            counts = {}
            for _ in range(self.shots):
                # Sample each feature independently (classical approximation)
                bitstring = ''.join([
                    '1' if np.random.rand() < prob else '0'
                    for prob in feature_probs
                ])
                counts[bitstring] = counts.get(bitstring, 0) + 1
            return counts
    
    def interpret_measurement(
        self,
        counts: Dict[str, int],
        interpretation_mode: str = 'probability'
    ) -> Dict[str, Any]:
        """
        Interpret quantum measurement results to extract prediction.
        
        Args:
            counts: Measurement counts from simulation
            interpretation_mode: How to interpret results ('probability', 'majority', 'weighted')
            
        Returns:
            Interpretation dictionary with prediction and confidence
        """
        total_shots = sum(counts.values())
        
        if interpretation_mode == 'probability':
            # Interpret as probability of "success" (more 1s than 0s in bitstring)
            success_count = sum(
                count for bitstring, count in counts.items()
                if bitstring.count('1') > len(bitstring) / 2
            )
            prediction = success_count / total_shots
            confidence = max(success_count, total_shots - success_count) / total_shots
        
        elif interpretation_mode == 'majority':
            # Most common state
            most_common = max(counts.items(), key=lambda x: x[1])
            prediction = most_common[1] / total_shots
            confidence = prediction  # Confidence is the probability of most common state
        
        elif interpretation_mode == 'weighted':
            # Weighted average based on number of 1s
            weighted_sum = sum(
                bitstring.count('1') / len(bitstring) * count
                for bitstring, count in counts.items()
            )
            prediction = weighted_sum / total_shots
            # Confidence based on concentration of measurements
            entropy = -sum(
                (c/total_shots) * np.log2(c/total_shots)
                for c in counts.values() if c > 0
            )
            max_entropy = np.log2(len(counts))
            confidence = 1 - (entropy / max_entropy if max_entropy > 0 else 0)
        
        else:
            logger.warning(f"Unknown interpretation mode: {interpretation_mode}, using 'probability'")
            return self.interpret_measurement(counts, 'probability')
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "most_common_state": max(counts.items(), key=lambda x: x[1])[0],
            "unique_states_observed": len(counts),
            "total_measurements": total_shots
        }
    
    def perceive(
        self,
        feature_probs: List[float],
        entanglement_pattern: str = 'cascade',
        interpretation_mode: str = 'probability',
        classical_baseline: bool = True
    ) -> QuantumPerceptionResult:
        """
        Complete quantum perception: features → circuit → simulation → interpretation → insight.
        
        Args:
            feature_probs: Probability for each system feature/agent
            entanglement_pattern: How features entangle ('cascade', 'star', 'mesh')
            interpretation_mode: How to interpret measurements
            classical_baseline: Whether to compute classical baseline for comparison
            
        Returns:
            QuantumPerceptionResult with prediction and analysis
        """
        # Create entangled circuit
        circuit = self.create_entangled_circuit(feature_probs, entanglement_pattern)
        
        # Simulate quantum measurement
        counts = self.simulate_perception(circuit, feature_probs)
        
        # Interpret results
        interpretation = self.interpret_measurement(counts, interpretation_mode)
        
        # Calculate entanglement strength (approximation based on state diversity)
        unique_states = interpretation["unique_states_observed"]
        max_possible_states = 2 ** self.num_qubits
        entanglement_strength = min(unique_states / max_possible_states, 1.0)
        
        # Classical baseline (independent variable multiplication)
        if classical_baseline:
            classical_pred = np.prod(feature_probs)  # Independent probability product
        else:
            classical_pred = interpretation["prediction"]
        
        # Create result
        result = QuantumPerceptionResult(
            prediction=interpretation["prediction"],
            confidence=interpretation["confidence"],
            quantum_state=interpretation["most_common_state"],
            entanglement_strength=entanglement_strength,
            classical_baseline=classical_pred,
            metadata={
                "entanglement_pattern": entanglement_pattern,
                "interpretation_mode": interpretation_mode,
                "unique_states": unique_states,
                "shots": self.shots,
                "qiskit_available": QISKIT_AVAILABLE
            }
        )
        
        logger.info(f"[QuantumRetina] Perception complete: prediction={result.prediction:.3f}, "
                   f"confidence={result.confidence:.3f}, entanglement={result.entanglement_strength:.3f}")
        
        return result


class QuantumPerceptionEngine:
    """
    The Complete Quantum Perception Engine - The Sixth Sense.
    
    Integrates all three components:
    - Lens Grinder: Calibrate perception
    - Optic Nerve: Ingest reality
    - Quantum Retina: Perceive entangled truth
    
    This is the full sensory organ for perceiving complex, entangled systems
    that classical independent-variable models cannot see.
    
    Philosophy:
    "We have built a new eye. Not to see further, but to see deeper.
    Not to see more parts, but to see the whole. Not to observe reality,
    but to perceive its quantum nature."
    """
    
    def __init__(
        self,
        num_qubits: int = 4,
        shots: int = 1024,
        lens_grinder: Optional[QuantumLensGrinder] = None,
        optic_nerve: Optional[OpticNervePipeline] = None,
        quantum_retina: Optional[QuantumRetina] = None
    ):
        """
        Initialize the complete quantum perception engine.
        
        Args:
            num_qubits: Number of system dimensions to model
            shots: Quantum measurement repetitions
            lens_grinder: Optional custom lens grinder
            optic_nerve: Optional custom optic nerve
            quantum_retina: Optional custom quantum retina
        """
        self.lens_grinder = lens_grinder or QuantumLensGrinder()
        self.optic_nerve = optic_nerve or OpticNervePipeline(self.lens_grinder)
        self.quantum_retina = quantum_retina or QuantumRetina(num_qubits, shots)
        
        self.perception_history = []
        
        logger.info(f"[QuantumPerceptionEngine] 🔮 Initialized - The Sixth Sense is active")
        logger.info(f"   Dimensions: {num_qubits} qubits")
        logger.info(f"   Measurement precision: {shots} shots")
        logger.info(f"   Quantum backend: {'Qiskit' if QISKIT_AVAILABLE else 'Classical approximation'}")
    
    def perceive_system(
        self,
        raw_data: Dict[str, Any],
        feature_map: Optional[Dict[str, List[str]]] = None,
        scale_map: Optional[Dict[str, str]] = None,
        entanglement_pattern: str = 'cascade',
        interpretation_mode: str = 'probability'
    ) -> QuantumPerceptionResult:
        """
        Complete quantum perception of a complex system.
        
        Args:
            raw_data: Raw system data from reality
            feature_map: Optional feature extraction specification
            scale_map: Optional per-feature scaling
            entanglement_pattern: How system features entangle
            interpretation_mode: How to interpret quantum measurements
            
        Returns:
            QuantumPerceptionResult with system prediction and analysis
        """
        # Step 1: Optic Nerve - Reality → Quantum-ready probabilities
        quantum_ready = self.optic_nerve.full_pipeline(
            raw_data,
            feature_map=feature_map,
            scale_map=scale_map
        )
        
        # Step 2: Ensure we have the right number of features
        feature_probs = list(quantum_ready.values())[:self.quantum_retina.num_qubits]
        
        if len(feature_probs) < self.quantum_retina.num_qubits:
            # Pad with neutral probabilities if needed
            feature_probs.extend([0.5] * (self.quantum_retina.num_qubits - len(feature_probs)))
            logger.warning(f"Padded features to {self.quantum_retina.num_qubits} qubits")
        
        # Step 3: Quantum Retina - Perceive entangled system
        result = self.quantum_retina.perceive(
            feature_probs,
            entanglement_pattern=entanglement_pattern,
            interpretation_mode=interpretation_mode
        )
        
        # Add input data to metadata
        result.metadata["raw_data_keys"] = list(raw_data.keys())
        result.metadata["quantum_ready_features"] = quantum_ready
        
        # Store in history
        self.perception_history.append({
            "timestamp": now_iso(),
            "raw_data": raw_data,
            "result": result.to_dict()
        })
        
        logger.info(f"[QuantumPerceptionEngine] 🔮 System perceived: "
                   f"quantum={result.prediction:.3f} vs classical={result.classical_baseline:.3f} "
                   f"(Δ={abs(result.prediction - result.classical_baseline):.3f})")
        
        return result
    
    def compare_to_classical(self, result: QuantumPerceptionResult) -> Dict[str, Any]:
        """
        Compare quantum perception to classical independent-variable model.
        
        Args:
            result: QuantumPerceptionResult to analyze
            
        Returns:
            Comparison analysis
        """
        quantum_advantage = result.prediction - result.classical_baseline
        
        return {
            "quantum_prediction": result.prediction,
            "classical_baseline": result.classical_baseline,
            "quantum_advantage": quantum_advantage,
            "advantage_percentage": (quantum_advantage / result.classical_baseline * 100
                                    if result.classical_baseline != 0 else float('inf')),
            "entanglement_captured": result.entanglement_strength,
            "interpretation": (
                "Quantum model captures significant entanglement effects" if abs(quantum_advantage) > 0.1
                else "Quantum and classical models largely agree"
            )
        }
    
    def get_perception_statistics(self) -> Dict[str, Any]:
        """Get statistics about perception history."""
        if not self.perception_history:
            return {"perceptions_performed": 0}
        
        results = [p["result"] for p in self.perception_history]
        
        return {
            "perceptions_performed": len(results),
            "average_prediction": np.mean([r["prediction"] for r in results]),
            "average_confidence": np.mean([r["confidence"] for r in results]),
            "average_entanglement": np.mean([r["entanglement_strength"] for r in results]),
            "quantum_vs_classical_divergence": np.mean([
                abs(r["prediction"] - r["classical_baseline"]) for r in results
            ])
        }


# Convenience function for quick usage
def perceive_quantum_system(
    data: Dict[str, Any],
    num_features: int = 4,
    entanglement: str = 'cascade'
) -> QuantumPerceptionResult:
    """
    Quick quantum perception of a system.
    
    Args:
        data: System data dictionary
        num_features: Number of features/qubits to use
        entanglement: Entanglement pattern
        
    Returns:
        QuantumPerceptionResult
    """
    engine = QuantumPerceptionEngine(num_qubits=num_features)
    return engine.perceive_system(data, entanglement_pattern=entanglement)


if __name__ == "__main__":
    print("🔮 Quantum Perception Engine - The Sixth Sense")
    print("=" * 80)
    print()
    
    # Demo: Perceive a simple multi-agent system
    print("Demo: Perceiving a 4-agent entangled system")
    print("-" * 80)
    
    # Simulate system data (e.g., agent performance metrics)
    demo_data = {
        "agent_1_performance": [0.8, 0.75, 0.82, 0.78],  # High performer
        "agent_2_performance": [0.6, 0.65, 0.58, 0.62],  # Mid performer
        "agent_3_performance": [0.4, 0.38, 0.42, 0.41],  # Low performer
        "system_context": 0.7  # Overall system state
    }
    
    # Create engine
    engine = QuantumPerceptionEngine(num_qubits=4, shots=2048)
    
    # Perceive with different entanglement patterns
    for pattern in ['cascade', 'star', 'mesh']:
        print(f"\n{pattern.upper()} Entanglement:")
        result = engine.perceive_system(
            demo_data,
            entanglement_pattern=pattern
        )
        
        print(f"  Quantum Prediction: {result.prediction:.3f}")
        print(f"  Classical Baseline: {result.classical_baseline:.3f}")
        print(f"  Quantum Advantage: {result.prediction - result.classical_baseline:+.3f}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  Entanglement Strength: {result.entanglement_strength:.3f}")
        print(f"  Most Common State: {result.quantum_state}")
    
    # Statistics
    print("\n" + "=" * 80)
    stats = engine.get_perception_statistics()
    print("Perception Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value:.3f}" if isinstance(value, float) else f"  {key}: {value}")
    
    print("\n🔮 The Sixth Sense is operational")
    print("Ready to perceive quantum truth in any complex, entangled system.")

