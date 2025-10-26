import numpy as np
import matplotlib.pyplot as plt
import logging
from Three_PointO_ArchE.quantum_utils import (
    run_quantum_simulation,
    partial_trace,
    von_neumann_entropy
)

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_quantum_compass_story():
    """
    Simulates the story of the quantum compass and plots the evolution of entanglement.
    """
    logging.info("Starting the 'Quantum Compass' simulation...")

    # --- 1. Initial State: The Entangled Electrons (Bell State) ---
    # We use the Bell state |Ψ⁻⟩ = (|↑↓⟩ - |↓↑⟩) / sqrt(2)
    # This state represents perfect anti-correlation.
    spin_up = np.array([1, 0], dtype=complex)
    spin_down = np.array([0, 1], dtype=complex)
    initial_state = (np.kron(spin_up, spin_down) - np.kron(spin_down, spin_up)) / np.sqrt(2)
    logging.info(f"Initial state created (Bell state |Ψ⁻⟩) with dimension {len(initial_state)}.")

    # --- 2. The Environment: The Star's Turbulent Magnetic Field ---
    time_horizon = 15.0  # Total time of the journey
    num_steps = 100    # Number of measurements taken
    
    # Simulate a "turbulent" or "noisy" field with random pulse periods
    # This represents the chaotic fluctuations of the star's magnetic field.
    pulse_periods = np.random.rand(num_steps) * 3.0 + 0.5
    logging.info(f"Simulating a journey of {time_horizon}s with {num_steps} turbulent field fluctuations.")

    # --- 3. The Physics: Interaction Strengths ---
    # Strong internal coupling to keep them entangled
    J_coupling_strength = 1.0
    # Weaker external magnetic field from the star
    K_local_field = 0.25
    
    # --- 4. Run the Simulation ---
    logging.info("Running the quantum simulation...")
    results = run_quantum_simulation(
        time_horizon=time_horizon,
        pulse_amplitude=1.0,  # Amplitude is constant, timing is chaotic
        pulse_width=0.1,
        pulse_periods=pulse_periods,
        initial_state=initial_state,
        J=J_coupling_strength,
        K=K_local_field
    )
    logging.info("Simulation complete. Analyzing results...")

    # --- 5. Analyze the Entanglement ---
    entanglement_history = []
    for state in results['state_evolution']:
        # For each point in time, calculate the entanglement entropy
        full_density_matrix = np.outer(state, state.conj())
        # We trace out one electron to see the state of the other
        reduced_density_matrix = partial_trace(full_density_matrix, keep_subsystem=0, dims=[2, 2])
        # The entropy of the reduced matrix measures the entanglement
        entropy = von_neumann_entropy(reduced_density_matrix)
        entanglement_history.append(entropy)
    
    # --- 6. Visualize the Story's Outcome ---
    logging.info("Generating plot of the entanglement history...")
    times = results['times']
    
    plt.figure(figsize=(12, 7))
    plt.plot(times, entanglement_history, label='Entanglement between Alice & Bob', color='c', marker='o', linestyle='-', markersize=4)
    
    # Add a horizontal line for maximum possible entanglement (log2(2) = 1)
    plt.axhline(y=1.0, color='r', linestyle='--', label='Max Entanglement (1.0)')
    
    plt.title("The Quantum Compass Story: Entanglement vs. a Turbulent Star", fontsize=16)
    plt.xlabel("Time of Journey (seconds)", fontsize=12)
    plt.ylabel("Von Neumann Entropy (Entanglement)", fontsize=12)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.ylim(0, 1.1)
    
    output_filename = 'quantum_compass_story.png'
    plt.savefig(output_filename)
    logging.info(f"Plot saved to '{output_filename}'.")
    plt.show()

if __name__ == "__main__":
    run_quantum_compass_story() 