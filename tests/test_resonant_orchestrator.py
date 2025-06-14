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
    
    # Define a complex target with multiple aspects and nested requirements
    target = {
        "type": "system_analysis",
        "aspects": [
            "code_quality",
            "workflow_health",
            "system_integrity"
        ],
        "requirements": {
            "code_quality": {
                "metrics": ["complexity", "coverage", "style"],
                "thresholds": {
                    "complexity": 10,
                    "coverage": 0.8,
                    "style": "strict"
                }
            },
            "workflow_health": {
                "metrics": ["success_rate", "execution_time", "resource_usage"],
                "thresholds": {
                    "success_rate": 0.95,
                    "execution_time": 300,
                    "resource_usage": "moderate"
                }
            },
            "system_integrity": {
                "metrics": ["dependencies", "security", "performance"],
                "thresholds": {
                    "dependencies": "up_to_date",
                    "security": "high",
                    "performance": "optimal"
                }
            }
        },
        "constraints": {
            "timeout": 600,  # 10 minutes
            "parallel_execution": True,
            "resource_limits": {
                "cpu": "80%",
                "memory": "4GB",
                "disk": "1GB"
            }
        }
    }
    
    # Define the execution context with detailed environment information
    context = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "type": "development",
            "version": "3.0.0",
            "python_version": "3.12.0",
            "os": "linux"
        },
        "priority": "high",
        "resources": {
            "max_parallel_tasks": 4,
            "memory_limit": "4GB",
            "cpu_limit": "80%",
            "disk_limit": "1GB"
        },
        "monitoring": {
            "enabled": True,
            "metrics": [
                "execution_time",
                "resource_usage",
                "success_rate",
                "error_rate"
            ],
            "alert_thresholds": {
                "execution_time": 300,
                "memory_usage": "3GB",
                "error_rate": 0.05
            }
        },
        "adaptation": {
            "enabled": True,
            "strategies": [
                "retry_with_backoff",
                "fallback_to_simpler_tool",
                "parallel_execution",
                "resource_reallocation"
            ]
        }
    }
    
    # Execute the resonant chain
    results = await orchestrator.execute_resonant_chain(
        target=target,
        context=context,
        max_depth=3
    )
    
    # Save detailed results
    output_file = f"outputs/resonant_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "target": target,
            "context": context,
            "results": results,
            "metadata": {
                "execution_time": datetime.now().isoformat(),
                "version": "1.0.0",
                "orchestrator": "ResonantOrchestrator"
            }
        }, f, indent=2)
    
    print(f"\nResonant execution completed. Results saved to: {output_file}")
    
    # Display execution summary
    print("\nExecution Summary:")
    print("=" * 80)
    print(f"Total Steps: {len(results.get('steps', []))}")
    print(f"Parallel Groups: {len(results.get('parallel_results', []))}")
    print(f"Adaptations: {len(results.get('adaptations', []))}")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_resonant_execution()) 