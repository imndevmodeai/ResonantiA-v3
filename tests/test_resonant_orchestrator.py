"""
Test script for the Resonant Orchestrator.
"""
import asyncio
import json
from datetime import datetime
from Three_PointO_ArchE.resonant_orchestrator import ResonantOrchestrator

async def test_resonant_execution():
    """Test the Resonant Orchestrator with a complex execution chain."""
    orchestrator = ResonantOrchestrator()
    
    # Define a complex target with multiple aspects
    target = {
        "type": "system_analysis",
        "aspects": [
            "code_quality",
            "workflow_health",
            "system_integrity"
        ],
        "constraints": {
            "timeout": 300,  # 5 minutes
            "parallel_execution": True
        }
    }
    
    # Define the execution context
    context = {
        "timestamp": datetime.now().isoformat(),
        "environment": "development",
        "priority": "high",
        "resources": {
            "max_parallel_tasks": 4,
            "memory_limit": "2GB"
        }
    }
    
    # Execute the resonant chain
    results = await orchestrator.execute_resonant_chain(
        target=target,
        context=context,
        max_depth=3
    )
    
    # Save results
    output_file = f"outputs/resonant_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResonant execution completed. Results saved to: {output_file}")

if __name__ == "__main__":
    asyncio.run(test_resonant_execution()) 