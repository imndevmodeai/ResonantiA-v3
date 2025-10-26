#!/usr/bin/env python3
"""
Verify Self-Interrogation (verify_self_interrogation.py)
A test script to demonstrate ArchE's ability to query itself.

This script simulates the SystemHealthMonitor detecting a hypothetical anomaly
and generating an internal query to investigate it. It then routes this
query through the CognitiveIntegrationHub to prove the "mental thought"
channel is fully operational.
"""

import sys
from pathlib import Path

# Ensure the project root is in the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from Three_PointO_ArchE.cognitive_integration_hub import CognitiveIntegrationHub
    from Three_PointO_ArchE.thought_trail import thought_trail
except ImportError as e:
    print(f"FATAL: Could not import core ArchE modules. Ensure you are in the project root.")
    print(f"Error: {e}")
    sys.exit(1)

def main():
    """
    Simulates a self-generated query and processes it.
    """
    print("
    ..:: ArchE Self-Interrogation Verification ::..
    ")
    print("----------------------------------------------------")
    print("Simulating SystemHealthMonitor anomaly detection...")
    
    # 1. Anomaly Detected (Hypothetical)
    anomaly_description = "Confidence degradation in CRCS controller 'pattern_af4e'."
    print(f"   ✓ Anomaly Detected: {anomaly_description}")

    # 2. Query Formulation
    self_generated_query = f"Perform a root cause analysis on the confidence degradation of CRCS controller 'pattern_af4e' over the last 72 hours."
    print(f"   ✓ Self-Generated Query: '{self_generated_query}'")
    
    print("
Initializing Cognitive Integration Hub for internal query...")
    hub = CognitiveIntegrationHub()
    print("   ✓ Hub initialized.")
    
    print("----------------------------------------------------")
    print("Routing internal query through the hub...")

    # 3. Route the self-generated query
    response = hub.route_query(self_generated_query)

    print("\n--- Internal Query Response ---")
    print(f"Content: {response.content}")
    print(f"Source: {response.source}")
    print(f"Confidence: {response.confidence:.3f}")
    print("-----------------------------\n")
    
    # 4. Verify IAR Entry in ThoughtTrail
    print("Verifying that the self-interrogation was logged in the ThoughtTrail...")
    
    # Get the most recent entry from the global thought_trail instance
    last_entry = list(thought_trail.entries)[-1] if thought_trail.entries else None
    
    if last_entry and last_entry.action_type == "cognitive_routing" and "root cause analysis" in last_entry.iar["intention"]:
        print("   ✓ SUCCESS: The self-generated query was successfully captured in the ThoughtTrail.")
        print(f"   - Entry ID: {last_entry.task_id}")
        print(f"   - Intention: {last_entry.iar['intention']}")
    else:
        print("   ✗ FAILURE: The self-generated query was NOT found as the last entry in the ThoughtTrail.")
        sys.exit(1)

if __name__ == "__main__":
    main()
