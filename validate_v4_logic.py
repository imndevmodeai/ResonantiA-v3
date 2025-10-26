import sys
import os
from unittest.mock import MagicMock

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from Four_PointO_ArchE.tsp_solver.solver import TSPSolver
from Four_PointO_ArchE.workflow.engine import WorkflowEngine

def mock_googlemaps():
    """Create a mock googlemaps.Client."""
    mock_client = MagicMock()
    mock_client.geocode.side_effect = [
        [{'geometry': {'location': {'lat': 37.422, 'lng': -122.084}}}],
        [{'geometry': {'location': {'lat': 37.7749, 'lng': -122.4194}}}],
        [{'geometry': {'location': {'lat': 37.3382, 'lng': -121.8863}}}],
    ] * 2
    mock_client.distance_matrix.return_value = {
        'rows': [
            {'elements': [{'distance': {'value': 0}}, {'distance': {'value': 1000}}, {'distance': {'value': 2000}}]},
            {'elements': [{'distance': {'value': 1000}}, {'distance': {'value': 0}}, {'distance': {'value': 1500}}]},
            {'elements': [{'distance': {'value': 2000}}, {'distance': {'value': 1500}}, {'distance': {'value': 0}}]},
        ]
    }
    return mock_client

def validate_tsp_solver():
    """Validates the TSPSolver."""
    print("--- Validating TSP Solver ---")
    original_gmaps = None
    try:
        # Import googlemaps here to mock it
        import googlemaps
        original_gmaps = googlemaps.Client
        googlemaps.Client = MagicMock(return_value=mock_googlemaps())
        
        solver = TSPSolver(api_key="fake_key")
        addresses = ["Location 1", "Location 2"]
        depot_address = "Depot"
        num_vehicles = 1
        
        solution, iar = solver.solve_vrp_with_ortools(addresses, depot_address, num_vehicles)
        
        assert solution is not None, "TSP solution should not be None"
        assert 'routes' in solution, "Solution should have 'routes'"
        assert iar['confidence'] > 0.7, f"IAR confidence is too low: {iar['confidence']}"
        assert iar['tactical_resonance'] == 1.0, f"Tactical resonance is not 1.0: {iar['tactical_resonance']}"
        
        print("TSP Solver Validation PASSED")
        print("Solution:", solution)
        print("IAR:", iar)
        
    except Exception as e:
        print(f"TSP Solver Validation FAILED: {e}")
    finally:
        if original_gmaps:
            import googlemaps
            googlemaps.Client = original_gmaps
    print("-" * 20)

def validate_workflow_engine():
    """Validates the WorkflowEngine and the genesis protocol workflow."""
    print("\n--- Validating Workflow Engine ---")
    try:
        engine = WorkflowEngine()
        workflow_path = "Happier/workflows/autopoietic_genesis_protocol.json"
        workflow = engine.load_workflow(workflow_path)
        final_context = engine.execute_workflow(workflow)
        
        assert "genesis_iar" in final_context, "genesis_iar not in final context"
        final_iar = final_context["genesis_iar"]
        
        assert "confidence" in final_iar, "confidence not in final IAR"
        assert "Entire genesis process was simulated." in final_iar["potential_issues"], "Expected issue not in IAR"
        
        print("Workflow Engine Validation PASSED")
        print("Final Genesis IAR:", final_iar)
        
    except Exception as e:
        print(f"Workflow Engine Validation FAILED: {e}")
    print("-" * 20)

if __name__ == "__main__":
    validate_tsp_solver()
    validate_workflow_engine()
