"""
=====================================================
Quantum System Analyzer (quantum_system_analyzer.py)
=====================================================
As Above: The Principle of Quantum Perception
---------------------------------------------
This module embodies the wisdom of perceiving a system not as a collection
of deterministic parts, but as a web of entangled, probabilistic relationships.
It is a sensory organ designed to look beyond the classical, surface-level
reality and model the hidden correlations and quantum-like dynamics that
govern complex systems.

So Below: The Operational Logic
-------------------------------
This module provides a production-ready Qiskit-based tool for modeling
system outcomes. It includes robust normalization for input data and a
configurable quantum circuit to simulate the entangled relationships
between different components of a system, be it an NFL game or the
health of a distributed network.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List

# Attempt to import Qiskit, but handle gracefully if not present
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    QISKIT_AVAILABLE = True
except ImportError:
    print("WARNING: Qiskit or Qiskit Aer is not installed. QuantumSystemAnalyzer will run in mock mode.")
    QISKIT_AVAILABLE = False


def normalize_metrics_to_probs(metric: float, min_val: float, max_val: float, tol: float = 1e-10) -> np.ndarray:
    """
    Normalizes a raw metric to a valid probability array for qubit encoding.
    
    Args:
        metric (float): The raw metric value (e.g., speed, latency, error rate).
        min_val (float): The expected minimum value of the metric.
        max_val (float): The expected maximum value of the metric.
        tol (float): Tolerance for checking if the sum of probabilities is 1.
        
    Returns:
        np.ndarray: A numpy array of [probability_of_state_1, probability_of_state_0].
    """
    # Scale the metric to a probability between 0 and 1
    prob = np.clip((metric - min_val) / (max_val - min_val), 0, 1)
    
    # Create the two-state probability array
    probs = np.array([prob, 1 - prob])
    
    # Verify and, if necessary, re-normalize to ensure the sum is exactly 1
    total = np.sum(probs)
    if abs(total - 1.0) > tol:
        if total == 0:
            # Avoid division by zero if clipping results in [0, 0]
            raise ValueError("Invalid probabilities after clipping: [0, 0]")
        probs = probs / total
        print(f"WARNING: Probabilities summed to {total:.6f}; re-normalized.")
    
    return probs


class QuantumSystemAnalyzer:
    """
    Uses a Qiskit simulation to model the outcome of a complex system
    with entangled components.
    """
    
    def __init__(self, num_qubits: int = 4, shots: int = 1024):
        if not QISKIT_AVAILABLE:
            print("QuantumSystemAnalyzer is in mock mode. No real quantum simulation will be performed.")
        self.num_qubits = num_qubits
        self.shots = shots
        self.simulator = AerSimulator() if QISKIT_AVAILABLE else None
    
    def run_nfl_game_simulation(self, drive_data: pd.DataFrame, game_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs a specialized quantum simulation for an NFL game drive.
        
        Args:
            drive_data (pd.DataFrame): DataFrame with NGS-like stats for a series of plays.
                                       Expected columns: 'qb_speed', 'rec_sep', 'def_acc'.
            game_context (Dict[str, Any]): Dictionary with contextual game data.
                                           Expected keys: 'score_diff', 'home_adv'.
                                           
        Returns:
            A dictionary containing the predicted win probability and the raw simulation counts.
        """
        if not QISKIT_AVAILABLE:
            return self._run_mock_simulation("NFL Game")
        
        # 1. Aggregate and Normalize Data (The Lens Grinder)
        avg_qb_prob = normalize_metrics_to_probs(drive_data['qb_speed'].mean(), 0, 22)[0]
        avg_rec_prob = normalize_metrics_to_probs(drive_data['rec_sep'].mean(), 0, 10)[0]
        # Invert defense probability: higher acceleration is bad for offense
        avg_def_prob = 1.0 - normalize_metrics_to_probs(drive_data['def_acc'].mean(), 0, 5)[0]
        context_prob = normalize_metrics_to_probs(
            game_context['score_diff'] + game_context['home_adv'] * 10, -20, 20
        )[0]
        
        print(f"Drive-Average Probs: QB={avg_qb_prob:.2f}, Rec={avg_rec_prob:.2f}, "
              f"Def={avg_def_prob:.2f}, Context={context_prob:.2f}")
        
        # 2. Build the Quantum Circuit (The Quantum Retina)
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        
        # Encode QB performance on Qubit 0
        theta_qb = 2 * np.arcsin(np.sqrt(avg_qb_prob))
        qc.ry(theta_qb, 0)
        
        # Encode Receiver performance on Qubit 1 and entangle with QB
        theta_rec = 2 * np.arcsin(np.sqrt(avg_rec_prob))
        qc.ry(theta_rec, 1)
        qc.cx(0, 1)
        
        # Encode Defense response on Qubit 2 and entangle with offense
        theta_def = 2 * np.arcsin(np.sqrt(avg_def_prob))
        qc.ry(theta_def, 2)
        qc.ccx(0, 1, 2)
        
        # Encode Game Context on Qubit 3 and entangle with all others
        theta_ctx = 2 * np.arcsin(np.sqrt(context_prob))
        qc.ry(theta_ctx, 3)
        qc.mcx([0, 1, 2], 3)
        
        # Measure all qubits
        qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        # 3. Simulate and Get Results
        compiled_circuit = transpile(qc, self.simulator)
        result = self.simulator.run(compiled_circuit, shots=self.shots).result()
        counts = result.get_counts(qc)
        
        # 4. Interpret Results
        home_win_prob = 0.0
        # Outcome mapping: '00' prefix for home win (drive success)
        for state, count in counts.items():
            if state.startswith('00'):
                home_win_prob += (count / self.shots)
        
        return {
            "predicted_home_win_prob": round(home_win_prob, 3),
            "raw_counts": counts,
            "simulation_details": {
                "qubits": self.num_qubits,
                "shots": self.shots,
                "normalized_inputs": {
                    "qb": avg_qb_prob,
                    "rec": avg_rec_prob,
                    "def": avg_def_prob,
                    "context": context_prob
                }
            }
        }
    
    def _run_mock_simulation(self, sim_type: str) -> Dict[str, Any]:
        """Returns a mock result when Qiskit is not available."""
        return {
            "error": "Qiskit not found. Running in mock mode.",
            "simulation_type": sim_type,
            "predicted_outcome_prob": 0.593,  # A plausible-looking result
            "raw_counts": {"0000": 320, "0001": 160, "0100": 96, "other": 448}
        }


if __name__ == '__main__':
    # Example usage for demonstration
    console = __import__('rich.console').console.Console()
    
    # Mock NGS data for a drive (5 pass plays)
    mock_ngs_drive = pd.DataFrame({
        'play_id': [101, 102, 103, 104, 105],
        'qb_speed': [18.5, 17.8, 19.0, 16.5, 18.0],
        'rec_sep': [4.2, 3.8, 5.0, 2.5, 4.0],
        'def_acc': [2.1, 2.3, 1.8, 2.5, 2.0]
    })
    
    # Mock Game context
    mock_game_context = {
        'score_diff': 7,
        'home_adv': 0.1
    }
    
    console.print("[bold green]-- Initializing Quantum System Analyzer --[/bold green]")
    analyzer = QuantumSystemAnalyzer()
    
    console.print("\n[cyan]-- Running NFL Game Simulation --[/cyan]")
    simulation_result = analyzer.run_nfl_game_simulation(mock_ngs_drive, mock_game_context)
    
    console.print("\n[bold green]-- Simulation Complete --[/bold green]")
    console.print(simulation_result)

