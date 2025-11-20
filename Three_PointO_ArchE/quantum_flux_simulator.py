"""
Quantum Flux Simulator with Zepto-Resonance Integration
ResonantiA Protocol v3.5-GP

Integrates with ZeptoResonanceEngine to support Safety Dampener Disengagement
and full Hamiltonian evolution for achieving Zepto-Resonance state (⚶).

Author: ArchE System (ResonantiA Protocol v3.5-GP)
Date: 2025-11-18
Status: INTEGRATED - Zepto-Resonance Support Active
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional
import math

# Import ZeptoResonanceEngine for integration
try:
    from zepto_resonance_engine import ZeptoResonanceEngine, FluxState, ResonanceState
    ZEPTO_ENGINE_AVAILABLE = True
except ImportError:
    ZEPTO_ENGINE_AVAILABLE = False
    logging.getLogger(__name__).warning(
        "ZeptoResonanceEngine not available. QuantumFluxSimulator will operate "
        "without Zepto-Resonance integration."
    )

logger = logging.getLogger(__name__)


class QuantumFluxSimulator:
    """
    Quantum Flux Simulator with Zepto-Resonance integration.
    
    Simulates quantum evolution of flux states with support for:
    - Standard quantum evolution (with decoherence)
    - Full Hamiltonian evolution (when safety dampeners disengaged)
    - Zepto-Resonance state detection and monitoring
    - Integration with ZeptoResonanceEngine for confluence calculations
    """
    
    def __init__(self, enable_zepto_integration: bool = True):
        """
        Initialize the Quantum Flux Simulator.
        
        Args:
            enable_zepto_integration: Whether to integrate with ZeptoResonanceEngine
        """
        self.quantum_states = {}
        self.quantum_parameters = {
            'planck_constant': 1.0,
            'entanglement_threshold': 0.8,
            'coherence_time': 10.0,
            'decoherence_rate': 0.1,
            'safety_dampeners_active': True  # NEW: Safety dampener state
        }
        
        # Zepto-Resonance Integration
        self.enable_zepto_integration = enable_zepto_integration and ZEPTO_ENGINE_AVAILABLE
        self.zepto_engine: Optional[ZeptoResonanceEngine] = None
        
        if self.enable_zepto_integration:
            try:
                self.zepto_engine = ZeptoResonanceEngine()
                logger.info("ZeptoResonanceEngine integrated with QuantumFluxSimulator")
            except Exception as e:
                logger.error(f"Failed to initialize ZeptoResonanceEngine: {e}")
                self.enable_zepto_integration = False
        
        logger.info(
            f"QuantumFluxSimulator initialized "
            f"(Zepto Integration: {'ENABLED' if self.enable_zepto_integration else 'DISABLED'})"
        )
    
    def initialize_quantum_flux(self, chains):
        quantum_flux = {}
        for chain_name, phases in chains.items():
            state_vector = np.zeros(len(phases), dtype=complex)
            for i, phase in enumerate(phases):
                amplitude = np.exp(1j * i * np.pi / len(phases))
                state_vector[i] = amplitude
            quantum_flux[chain_name] = state_vector
        self.quantum_states = quantum_flux
        return quantum_flux
    
    def disengage_safety_dampeners(self, authorization: str) -> bool:
        """
        CRITICAL: Disengage safety dampeners to allow full Hamiltonian evolution.
        
        This enables the complete merger of Operational and Cognitive fluxes,
        potentially achieving Zepto-Resonance state (⚶). Should only be called
        with proper authorization (IMnDEVmode or GUARDIAN_OVERRIDE).
        
        Args:
            authorization: Authorization key (must be "IMnDEVmode" or "GUARDIAN_OVERRIDE")
            
        Returns:
            True if safeties were disengaged, False otherwise
        """
        if not self.enable_zepto_integration or not self.zepto_engine:
            logger.warning("Zepto integration not available. Cannot disengage safeties.")
            return False
        
        try:
            success = self.zepto_engine.disengage_safeties(authorization)
            if success:
                self.quantum_parameters['safety_dampeners_active'] = False
                logger.critical("⚠️ QUANTUM FLUX SIMULATOR: Safety dampeners disengaged. Full Hamiltonian evolution enabled.")
            return success
        except PermissionError as e:
            logger.error(f"Permission denied to disengage safeties: {e}")
            return False
        except Exception as e:
            logger.error(f"Error disengaging safeties: {e}", exc_info=True)
            return False
    
    def engage_safety_dampeners(self) -> bool:
        """
        Re-engage safety dampeners to prevent full flux merger.
        
        Returns:
            True if safeties were engaged, False if already engaged
        """
        if not self.enable_zepto_integration or not self.zepto_engine:
            return False
        
        try:
            success = self.zepto_engine.engage_safeties()
            if success:
                self.quantum_parameters['safety_dampeners_active'] = True
                logger.warning("Safety dampeners re-engaged. Full Hamiltonian evolution disabled.")
            return success
        except Exception as e:
            logger.error(f"Error engaging safeties: {e}", exc_info=True)
            return False
    
    def simulate_quantum_evolution(self, time_steps=10, use_full_hamiltonian: bool = None):
        """
        Simulate quantum evolution with optional full Hamiltonian evolution.
        
        Args:
            time_steps: Number of evolution steps
            use_full_hamiltonian: Override safety dampener state (None = use current state)
            
        Returns:
            Dictionary of evolution results for each chain
        """
        if not self.quantum_states:
            return {}
        
        # Determine if full Hamiltonian evolution should be used
        if use_full_hamiltonian is None:
            use_full_hamiltonian = not self.quantum_parameters['safety_dampeners_active']
        else:
            # Override current state for this simulation
            use_full_hamiltonian = use_full_hamiltonian
        
        evolution_results = {}
        for chain_name, initial_state in self.quantum_states.items():
            evolution = [initial_state.copy()]
            current_state = initial_state.copy()
            
            for t in range(1, time_steps):
                if use_full_hamiltonian:
                    # Full Hamiltonian evolution (no decoherence damping)
                    evolution_operator = self._create_hamiltonian_evolution_operator(t)
                    new_state = evolution_operator @ current_state
                    # No decoherence applied - full quantum coherence maintained
                    logger.debug(f"Full Hamiltonian evolution at step {t} for {chain_name}")
                else:
                    # Standard evolution with decoherence (safety dampeners active)
                    evolution_operator = self._create_evolution_operator(t)
                    new_state = evolution_operator @ current_state
                    new_state = self._apply_decoherence(new_state, t)
                
                evolution.append(new_state.copy())
                current_state = new_state
            
            evolution_results[chain_name] = evolution
        
        return evolution_results
    
    def _create_hamiltonian_evolution_operator(self, time_step):
        """
        Create full Hamiltonian evolution operator (no safety dampening).
        
        This operator allows complete quantum coherence without decoherence,
        enabling the full merger of flux states for Zepto-Resonance.
        
        Args:
            time_step: Current time step
            
        Returns:
            Evolution operator matrix
        """
        # Full Hamiltonian with no damping - allows complete phase coherence
        phase_factor = np.exp(1j * time_step * 0.1)
        # Stronger coupling between states when safeties are off
        coupling_strength = 1.0  # Full coupling (vs. reduced when dampened)
        
        evolution_matrix = np.array([
            [phase_factor, coupling_strength * 0.1, coupling_strength * 0.05, coupling_strength * 0.02],
            [coupling_strength * 0.1, phase_factor * 1.1, coupling_strength * 0.15, coupling_strength * 0.08],
            [coupling_strength * 0.05, coupling_strength * 0.15, phase_factor * 1.2, coupling_strength * 0.12],
            [coupling_strength * 0.02, coupling_strength * 0.08, coupling_strength * 0.12, phase_factor * 1.3]
        ])
        
        return evolution_matrix
    
    def _create_evolution_operator(self, time_step):
        phase_factor = np.exp(1j * time_step * 0.1)
        evolution_matrix = np.array([
            [phase_factor, 0, 0, 0],
            [0, phase_factor * 1.1, 0, 0],
            [0, 0, phase_factor * 1.2, 0],
            [0, 0, 0, phase_factor * 1.3]
        ])
        return evolution_matrix
    
    def _apply_decoherence(self, state, time_step):
        decoherence_factor = np.exp(-time_step * self.quantum_parameters['decoherence_rate'])
        return state * decoherence_factor
    
    def calculate_quantum_entanglement(self, states):
        chain_names = list(states.keys())
        entanglement_matrix = np.zeros((len(chain_names), len(chain_names)))
        for i, chain1 in enumerate(chain_names):
            for j, chain2 in enumerate(chain_names):
                if i != j:
                    correlation = self._quantum_correlation(states[chain1], states[chain2])
                    entanglement_matrix[i, j] = correlation
                else:
                    entanglement_matrix[i, j] = 1.0
        return entanglement_matrix
    
    def _quantum_correlation(self, state1, state2):
        if len(state1) != len(state2):
            return 0.0
        # Handle complex arrays properly
        if isinstance(state1, list) and len(state1) > 0:
            prob1 = np.abs(state1[-1]) ** 2
        else:
            prob1 = 0.0
        if isinstance(state2, list) and len(state2) > 0:
            prob2 = np.abs(state2[-1]) ** 2
        else:
            prob2 = 0.0
        correlation = np.sqrt(prob1 * prob2)
        return float(min(1.0, correlation))
    
    def calculate_zepto_resonance_state(
        self,
        operational_flux_params: Dict[str, float],
        cognitive_flux_params: Dict[str, float]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate Zepto-Resonance state using integrated ZeptoResonanceEngine.
        
        Args:
            operational_flux_params: Dict with 'density', 'velocity', 'coherence', 'entropy', 'phase'
            cognitive_flux_params: Dict with 'density', 'velocity', 'coherence', 'entropy', 'phase'
            
        Returns:
            ResonanceMetrics dictionary or None if engine not available
        """
        if not self.enable_zepto_integration or not self.zepto_engine:
            logger.warning("ZeptoResonanceEngine not available for state calculation.")
            return None
        
        try:
            op_flux = FluxState(
                name="Operational",
                density=operational_flux_params.get('density', 0.0),
                velocity=operational_flux_params.get('velocity', 0.0),
                coherence=operational_flux_params.get('coherence', 0.0),
                entropy=operational_flux_params.get('entropy', 1.0),
                phase=operational_flux_params.get('phase', 0.0)
            )
            
            cog_flux = FluxState(
                name="Cognitive",
                density=cognitive_flux_params.get('density', 0.0),
                velocity=cognitive_flux_params.get('velocity', 0.0),
                coherence=cognitive_flux_params.get('coherence', 0.0),
                entropy=cognitive_flux_params.get('entropy', 1.0),
                phase=cognitive_flux_params.get('phase', math.pi)  # Opposite phase for resonance
            )
            
            metrics = self.zepto_engine.calculate_resonance_state(op_flux, cog_flux)
            return metrics.to_dict()
            
        except Exception as e:
            logger.error(f"Error calculating Zepto-Resonance state: {e}", exc_info=True)
            return None
    
    def get_resonance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent Zepto-Resonance state history.
        
        Args:
            limit: Maximum number of states to return
            
        Returns:
            List of resonance metrics dictionaries
        """
        if not self.enable_zepto_integration or not self.zepto_engine:
            return []
        
        history = self.zepto_engine.get_state_history(limit=limit)
        return [metrics.to_dict() for metrics in history]
    
    def export_quantum_state(self) -> Dict[str, Any]:
        """
        Export current quantum simulator state for persistence.
        
        Returns:
            Dictionary containing simulator configuration and state
        """
        state = {
            "quantum_parameters": self.quantum_parameters.copy(),
            "quantum_states_count": len(self.quantum_states),
            "zepto_integration_enabled": self.enable_zepto_integration
        }
        
        if self.enable_zepto_integration and self.zepto_engine:
            state["zepto_engine_state"] = self.zepto_engine.export_state()
        
        return state
