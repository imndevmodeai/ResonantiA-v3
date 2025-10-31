import json
from Three_PointO_ArchE.autopoietic_learning_loop import AutopoieticLearningLoop

def run_nebula_formation():
    """
    Simulates the Nebulae formation epoch of the learning loop.
    1. Initializes the learning loop.
    2. Feeds it the stardust data we just captured.
    3. Runs the pattern detection.
    4. Generates a proposal for the detected pattern.
    5. Prints the proposal for Guardian review.
    """
    print("🌟 Initializing Autopoietic Learning Loop for Nebulae Formation...")
    # Initialize with protocol_chunks for ACO
    learning_loop = AutopoieticLearningLoop(protocol_chunks=["Analyze code for missing decorators"], guardian_review_enabled=True)
    
    print("   ✓ Learning loop initialized")
    
    # Load the stardust we captured
    try:
        with open("logs/stardust_iar_gaps.json", "r") as f:
            stardust_entries = json.load(f)
        print(f"   ✓ Loaded {len(stardust_entries)} stardust entries from log file")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"   ✗ ERROR: Could not load stardust file: {e}")
        return

    # Capture the stardust
    for entry in stardust_entries:
        learning_loop.capture_stardust(entry)
    
    print(f"   ✓ Captured {learning_loop.metrics['stardust_captured']} experiences into the learning buffer")
    
    # Run the learning cycle to detect patterns
    print("\n🔄 Running learning cycle to detect nebulae...")
    cycle_results = learning_loop.run_learning_cycle(
        min_occurrences=3,
        detect_patterns=True,
        propose_solutions=True,
        failure_threshold=0.3
    )
    
    print(f"   ✓ Cycle complete: {cycle_results['nebulae_detected']} nebulae detected")
    
    # Get the proposal from the Guardian queue
    guardian_queue = learning_loop.get_guardian_queue()
    if not guardian_queue:
        print("\n   ✗ No patterns met the threshold for a proposal.")
        return
        
    print(f"\n🔥 {len(guardian_queue)} item(s) sent to Guardian Queue for Ignition.")
    
    # Display the first proposal for review
    first_proposal = guardian_queue[0]
    print("\n" + "="*80)
    print("GUARDIAN REVIEW: PROPOSED WISDOM FOR IGNITION")
    print("="*80)
    print(f"Pattern ID: {first_proposal['pattern_id']}")
    print(f"Pattern Signature: {first_proposal['signature']}")
    print(f"Occurrences: {first_proposal['occurrences']}")
    print(f"Success Rate (of failure): {first_proposal['success_rate']:.1%}")
    print("\n--- Proposed Solution ---")
    print(first_proposal['proposed_solution'])
    print("="*80)
    
if __name__ == "__main__":
    run_nebula_formation()
