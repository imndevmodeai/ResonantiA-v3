import unittest
from unittest.mock import MagicMock, patch
import pytest
import numpy as np
from ResonantiA.ArchE.cfp_framework import CFPFramework

# Helper to create a default CFPFramework instance for tests that don't need specific quantum setups
@pytest.fixture
def cfp_default_instance():
    # Initialize with minimal valid quantum system_configs for testing classical/general methods
    mock_system_config = {
        'quantum_state': [1.0, 0.0], # Minimal valid state
        # Add other keys if CFPFramework init or tested methods require them
    }
    return CFPFramework(
        system_a_config=mock_system_config,
        system_b_config=mock_system_config,
        evolution_model_type='placeholder', # Override to avoid needing Hamiltonians for these tests
        config_override={'log_level': 'ERROR'} # This was from original, keep if still relevant or handled by kwargs
    )

class TestCFPFrameworkClassicalMethods:

    def test_compare_classical_states_euclidean(self, cfp_default_instance):
        state1 = [1.0, 2.0, 3.0]
        state2 = [4.0, 5.0, 6.0]
        # Expected: sqrt((4-1)^2 + (5-2)^2 + (6-3)^2) = sqrt(3^2 + 3^2 + 3^2) = sqrt(9 + 9 + 9) = sqrt(27)
        expected_distance = np.sqrt(27)
        result = cfp_default_instance.compare_classical_states(state1, state2, method='euclidean')
        assert result['reflection']['status'] == 'Success'
        assert np.isclose(result['distance'], expected_distance)
        assert result['method_used'] == 'euclidean'

    def test_compare_classical_states_manhattan(self, cfp_default_instance):
        state1 = np.array([1.0, 2.0, 3.0])
        state2 = np.array([4.0, -1.0, 7.0])
        # Expected: |4-1| + |-1-2| + |7-3| = 3 + 3 + 4 = 10
        expected_distance = 10.0
        result = cfp_default_instance.compare_classical_states(state1, state2, method='manhattan')
        assert result['reflection']['status'] == 'Success'
        assert np.isclose(result['distance'], expected_distance)
        assert result['method_used'] == 'manhattan'

    def test_compare_classical_states_cosine(self, cfp_default_instance):
        state1 = [1.0, 0.0]
        state2 = [0.0, 1.0] # Orthogonal vectors
        # Cosine similarity = (1*0 + 0*1) / (sqrt(1^2+0^2) * sqrt(0^2+1^2)) = 0 / (1*1) = 0
        # Cosine distance = 1 - similarity = 1
        expected_similarity = 0.0
        expected_distance = 1.0
        result = cfp_default_instance.compare_classical_states(state1, state2, method='cosine')
        assert result['reflection']['status'] == 'Success'
        assert np.isclose(result['similarity'], expected_similarity)
        assert np.isclose(result['distance'], expected_distance) # Distance is 1 - similarity
        assert result['method_used'] == 'cosine'

        state3 = [1.0, 1.0]
        state4 = [2.0, 2.0] # Collinear vectors
        # Cosine similarity = (1*2 + 1*2) / (sqrt(1^2+1^2) * sqrt(2^2+2^2)) = 4 / (sqrt(2)*sqrt(8)) = 4 / sqrt(16) = 4/4 = 1
        # Cosine distance = 1 - similarity = 0
        expected_similarity_2 = 1.0
        expected_distance_2 = 0.0
        result2 = cfp_default_instance.compare_classical_states(state3, state4, method='cosine')
        assert result2['reflection']['status'] == 'Success'
        assert np.isclose(result2['similarity'], expected_similarity_2)
        assert np.isclose(result2['distance'], expected_distance_2)
        assert result2['method_used'] == 'cosine'

    def test_compare_classical_states_invalid_method(self, cfp_default_instance):
        state1 = [1,2]
        state2 = [3,4]
        result = cfp_default_instance.compare_classical_states(state1, state2, method='nonexistent_method')
        assert result['reflection']['status'] == 'Failure'
        assert "Comparison method 'nonexistent_method' not supported" in result['reflection']['summary']
        assert result.get('distance') is None
        assert result.get('similarity') is None

    def test_compare_classical_states_mismatched_lengths(self, cfp_default_instance):
        state1 = [1,2,3]
        state2 = [4,5]
        result_euc = cfp_default_instance.compare_classical_states(state1, state2, method='euclidean')
        assert result_euc['reflection']['status'] == 'Failure'
        assert "State vectors must have the same dimension" in result_euc['reflection']['summary']
        
        result_cos = cfp_default_instance.compare_classical_states(state1, state2, method='cosine')
        assert result_cos['reflection']['status'] == 'Failure'
        assert "State vectors must have the same dimension" in result_cos['reflection']['summary']

    def test_compare_classical_states_empty_vectors(self, cfp_default_instance):
        state1 = []
        state2 = []
        result = cfp_default_instance.compare_classical_states(state1, state2, method='euclidean')
        # Current implementation treats empty vectors as valid for Euclidean (distance 0), so Success
        assert result['reflection']['status'] == 'Success'
        
    def test_compare_classical_states_zero_vector_cosine(self, cfp_default_instance):
        state1 = [0.0, 0.0]
        state2 = [1.0, 1.0]
        result = cfp_default_instance.compare_classical_states(state1, state2, method='cosine')
        assert result['reflection']['status'] == 'Failure'

        result2 = cfp_default_instance.compare_classical_states(state2, state1, method='cosine')
        assert result2['reflection']['status'] == 'Failure'
        assert 'Cannot compute cosine similarity if one or both vectors have zero magnitude' in result2['reflection']['summary']
        
        result3 = cfp_default_instance.compare_classical_states([0.0,0.0], [0.0,0.0], method='cosine')
        assert result3['reflection']['status'] == 'Failure'
        assert 'Cannot compute cosine similarity if one or both vectors have zero magnitude' in result3['reflection']['summary']

class TestCFPFrameworkFeedbackMethods:

    def test_global_best_management(self, cfp_default_instance):
        cfp = cfp_default_instance
        
        # Initial state
        assert cfp.get_global_best() == float('inf'), "Initial global best should be infinity"
        
        # Reset (should remain inf if not set)
        cfp.reset_global_best()
        assert cfp.get_global_best() == float('inf'), "Global best should be infinity after reset if never set"

        # Process first feedback
        # Note: The interim process_feedback_request returns 'reflection' directly.
        feedback_result1 = cfp.process_feedback_request("agent1", 100.0, 120.0)
        assert feedback_result1['reflection']['status'] == 'Success'
        assert cfp.get_global_best() == 100.0, "Global best should be updated"

        # Process better feedback
        cfp.process_feedback_request("agent2", 50.0, 60.0)
        assert cfp.get_global_best() == 50.0

        # Process worse feedback
        cfp.process_feedback_request("agent3", 75.0, 80.0)
        assert cfp.get_global_best() == 50.0

        # Process feedback with same distance
        cfp.process_feedback_request("agent4", 50.0, 55.0)
        assert cfp.get_global_best() == 50.0

        # Reset global best
        cfp.reset_global_best()
        assert cfp.get_global_best() == float('inf'), "Global best should be reset to infinity"

    def test_process_feedback_request_basic_structure(self, cfp_default_instance):
        cfp = cfp_default_instance
        current_dist = 200.0
        prev_dist = 210.0
        feedback_output = cfp.process_feedback_request("test_agent", current_dist, prev_dist, effort_spent=5)
        
        assert 'reflection' in feedback_output
        assert feedback_output['directive'] is not None # Check a key from the main dict
        assert feedback_output['reflection']['status'] == 'Success'
        assert 'summary' in feedback_output['reflection']
        assert 'agent_feedback' in feedback_output
        
        agent_fb_data = feedback_output['agent_feedback']
        # The interim method doesn't explicitly return improvement_detected or global_best_distance in its direct output dict
        # These are side effects or internal logic elements reflected in logs/global state.
        # We check global_best via get_global_best()
        assert cfp.get_global_best() <= current_dist # Global best should be at least as good as current

    def test_process_feedback_request_exploration_directive(self, cfp_default_instance):
        cfp = cfp_default_instance
        cfp.process_feedback_request("agent_init", 100.0, 120.0) # Set a global best to 100.0
        
        # Agent significantly worse than global best (150.0 vs 100.0 * 1.05 = 105.0)
        # The config_params like exploration_threshold_factor are not directly used by the interim process_feedback_request,
        # it has a hardcoded 1.05 factor. So, we test against that.
        feedback_worse = cfp.process_feedback_request("stagnant_agent", 150.0, 150.0, effort_spent=1)
        assert feedback_worse.get('directive') == 'maintain_or_explore_gently' # Check returned directive
        assert 'Stuck and far from global best' in feedback_worse['agent_feedback'].get('notes', [])[0]
        assert feedback_worse['agent_feedback'].get('reset_to_best_known') == True

        # Agent not improving but not far enough to trigger explore (e.g. 102 vs 100*1.05)
        # Should get 'refine_further' or similar if no improvement but not drastically worse
        feedback_stuck_close = cfp.process_feedback_request("stuck_agent_close", 102.0, 102.0)
        assert feedback_stuck_close['agent_feedback'].get('action') == 'refine_further' # Updated expected action

    def test_process_feedback_request_exploit_directive(self, cfp_default_instance):
        cfp = cfp_default_instance
        # Set initial global best to 100.0
        cfp.process_feedback_request("agent_init", 100.0, 120.0) 
        assert cfp.get_global_best() == 100.0
        
        # Agent made an improvement, new global best is 90.0
        feedback_improve = cfp.process_feedback_request("improving_agent", 90.0, 95.0)
        assert feedback_improve.get('directive') == 'exploit' # Check returned directive
        assert cfp.get_global_best() == 90.0
        
        # Agent reports its previous best (90.0), no improvement over its own state,
        # but this is still the current global best. Should suggest refining further.
        feedback_stuck_at_current_best = cfp.process_feedback_request("stuck_at_current_best_agent", 90.0, 90.0)
        assert cfp.get_global_best() == 90.0 # Global best unchanged
        # current_distance (90) > global_best (90) * 1.05 is false (90 > 94.5 is false)
        # So, it should fall into the 'refine_further' else block.
        assert feedback_stuck_at_current_best['agent_feedback'].get('action') == 'refine_further' 