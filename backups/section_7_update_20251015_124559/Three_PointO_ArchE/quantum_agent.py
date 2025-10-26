# scalable_framework.py
from typing import Callable, Dict, List, Any, Tuple, Optional

import numpy as np

from .cfp_framework import (
    comparative_flux_density,
    comparative_entropy_ratio,
    flux_entropy_product,
    comparative_fluxual_processing,
    potential_function,
    system_flux,
    network_flux,
    calculate_integrated_flux,
    flux_potential_integral
)
from .quantum_utils import calculate_shannon_entropy


class ScalableAgent:
    """
    A scalable agent framework that incorporates Comparative Fluxual Processing (CFP)
    and dynamic operator selection for flexible and context-aware behavior.

    This agent model is designed to operate in complex environments, leveraging CFP
    to analyze system dynamics and adapt its behavior through dynamic operator selection.
    It supports multiple workflow modes and action registries for extensibility.

    Attributes:
        agent_id (str): Unique identifier for the agent.
        initial_state (np.ndarray): Initial state vector of the agent.
        operators (Dict[str, np.ndarray]): Dictionary of operators available to the agent,
                                         keyed by descriptive names (e.g., 'explore', 'exploit').
        action_registry (Dict[str, Callable]): Registry of actions the agent can perform,
                                              keyed by action names. Actions are functions.
        workflow_modes (Dict[str, List[str]]): Defines workflow modes as lists of action names.
        current_operator_key (str): Key for the operator currently in use.
        operator_selection_strategy (Callable[[ScalableAgent], str]): Strategy function
                                                                    to dynamically select the operator.
        state_history (List[np.ndarray]): History of agent states.
        flux_history (List[float]): History of flux values.

    Args:
        agent_id (str): Identifier for the agent.
        initial_state (np.ndarray): Initial state vector.
        operators (Dict[str, np.ndarray]): Operators dictionary.
        action_registry (Dict[str, Callable]): Action registry.
        workflow_modes (Dict[str, List[str]]): Workflow modes dictionary.
        operator_selection_strategy (Callable[[ScalableAgent], str]): Operator selection strategy function.
        initial_operator_key (str, optional): Initial operator key to use. Defaults to the first key in operators.

    Raises:
        ValueError: if operators dictionary is empty.
        ValueError: if initial_operator_key is not found in operators.
    """
    def __init__(
        self,
        agent_id: str,
        initial_state: np.ndarray,
        operators: Dict[str, np.ndarray],
        action_registry: Dict[str, Callable],
        workflow_modes: Dict[str, List[str]],
        operator_selection_strategy: Callable[['ScalableAgent'], str],
        initial_operator_key: Optional[str] = None,
    ):
        if not operators:
            raise ValueError("Operators dictionary cannot be empty.")
        if initial_operator_key is None:
            initial_operator_key = next(iter(operators)) # Default to first operator key if not specified
        if initial_operator_key not in operators:
            raise ValueError(f"Initial operator key '{initial_operator_key}' not found in operators.")


        self.agent_id = agent_id
        self.initial_state = initial_state
        self.current_state = initial_state.copy() # Ensure initial state is copied, not referenced
        self.operators = operators
        self.action_registry = action_registry
        self.workflow_modes = workflow_modes
        self.current_operator_key = initial_operator_key
        self.operator_selection_strategy = operator_selection_strategy
        self.state_history = [initial_state.copy()] # Initialize state history
        self.flux_history = [] # Initialize flux history


    def select_operator(self) -> str:
        """
        Selects the next operator to use based on the operator_selection_strategy.

        Returns:
            str: The key of the selected operator.
        """
        selected_operator_key = self.operator_selection_strategy(self) # Use strategy to select operator
        if selected_operator_key not in self.operators: # Validate selected key
            raise ValueError(f"Operator selection strategy returned invalid key: '{selected_operator_key}'")
        self.current_operator_key = selected_operator_key # Update current operator key
        return selected_operator_key


    def perform_action(self, action_name: str, *args: Any, **kwargs: Any) -> Any:
        """
        Performs an action from the action registry.

        Args:
            action_name (str): The name of the action to perform.
            *args: Positional arguments to pass to the action function.
            **kwargs: Keyword arguments to pass to the action function.

        Returns:
            Any: The result of the action execution.

        Raises:
            ValueError: if action_name is not found in the action_registry.
        """
        if action_name not in self.action_registry: # Check if action exists in registry
            raise ValueError(f"Action '{action_name}' not found in action registry.")
        action_function = self.action_registry[action_name] # Get action function from registry

        operator = self.operators[self.current_operator_key] # Get current operator
        return action_function(self, operator, *args, **kwargs) # Execute action with agent and operator context


    def update_state(self, next_state: np.ndarray):
        """
        Updates the agent's current state and records state transition information.

        Calculates flux density between the previous state and the next state,
        updates the current state, and appends state and flux to history.

        Args:
            next_state (np.ndarray): The new state vector to update to.

        Raises:
            ValueError: if next_state is not a numpy array.
            ValueError: if next_state has incompatible shape with current state.
        """
        if not isinstance(next_state, np.ndarray):
            raise ValueError("Next state must be a numpy array.")
        if next_state.shape != self.current_state.shape:
            raise ValueError("Next state shape is incompatible with current state.")


        flux = comparative_flux_density(self.current_state, next_state) # Calculate flux density
        self.flux_history.append(flux) # Append flux to history
        self.state_history.append(next_state.copy()) # Append new state to history
        self.current_state = next_state.copy() # Update current state


    def run_workflow(self, workflow_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Executes a predefined workflow consisting of a sequence of actions.

        Args:
            workflow_name (str): Name of the workflow to execute, must be defined in workflow_modes.
            *args: Positional arguments passed to each action in the workflow.
            **kwargs: Keyword arguments passed to each action in the workflow.

        Returns:
            List[Any]: List of results from each action performed in the workflow.

        Raises:
            ValueError: if workflow_name is not defined in workflow_modes.
        """
        if workflow_name not in self.workflow_modes: # Check if workflow exists
            raise ValueError(f"Workflow '{workflow_name}' not defined in workflow modes.")
        workflow = self.workflow_modes[workflow_name] # Get workflow action sequence
        workflow_results = [] # List to store results of each action

        for action_name in workflow: # Iterate through actions in workflow
            self.select_operator() # Select operator before each action
            action_result = self.perform_action(action_name, *args, **kwargs) # Perform action
            workflow_results.append(action_result) # Store action result

        return workflow_results # Return list of workflow results


    def get_state_trajectory(self, time_points: np.ndarray) -> np.ndarray:
        """
        Calculates and returns the state trajectory over given time points using the current operator.

        Uses the system_flux function to compute the trajectory based on the agent's current state
        and selected operator.

        Args:
            time_points (np.ndarray): Array of time points for trajectory calculation.

        Returns:
            np.ndarray: State trajectory array over the given time points.
        """
        operator = self.operators[self.current_operator_key] # Get current operator
        trajectory = system_flux(self.current_state, operator, time_points) # Calculate system flux trajectory
        return trajectory


    def calculate_network_flux(self, system_ids: List[Any], initial_states: Dict[Any, np.ndarray], time_points: np.ndarray) -> Dict[Any, np.ndarray]:
        """
        Calculates network flux for a set of systems using their initial states and predefined operators.

        Leverages the network_flux function to simulate the evolution of multiple systems in a network.

        Args:
            system_ids (List[Any]): List of system identifiers.
            initial_states (Dict[Any, np.ndarray]): Dictionary of initial states for each system.
            time_points (np.ndarray): Array of time points for network flux calculation.

        Returns:
            Dict[Any, np.ndarray]: Dictionary of state trajectories for each system in the network.
        """
        operators_subset = {sys_id: self.operators[self.current_operator_key] for sys_id in system_ids} # Use current agent operator for all systems - could be generalized
        network_trajectories = network_flux(initial_states, operators_subset, time_points) # Calculate network flux
        return network_trajectories


    def run_comparative_fluxual_processing(self, state_series_1: List[np.ndarray], state_series_2: List[np.ndarray]) -> Dict[str, float]:
        """
        Executes Comparative Fluxual Processing (CFP) on two state series.

        Delegates to the comparative_fluxual_processing function to analyze and compare
        the dynamics of two system state series.

        Args:
            state_series_1 (List[np.ndarray]): First state series for CFP.
            state_series_2 (List[np.ndarray]): Second state series for CFP.

        Returns:
            Dict[str, float]: CFP metrics dictionary (average flux, entropy ratio, flux-entropy product).
        """
        cfp_metrics = comparative_fluxual_processing(state_series_1, state_series_2) # Perform CFP
        return cfp_metrics


    def calculate_integrated_flux_over_trajectory(self, time_points: np.ndarray) -> np.ndarray:
        """
        Calculates the integrated flux over a generated state trajectory.

        First generates a state trajectory using get_state_trajectory, then calculates
        the integrated flux along this trajectory.

        Args:
            time_points (np.ndarray): Array of time points for trajectory and integration.

        Returns:
            np.ndarray: Array of integrated flux values over time points.
        """
        trajectory = self.get_state_trajectory(time_points) # Generate state trajectory
        integrated_flux_values = calculate_integrated_flux(trajectory, time_points) # Calculate integrated flux
        return integrated_flux_values


    def calculate_flux_potential_integral_over_trajectory(self, time_points: np.ndarray) -> float:
        """
        Calculates the flux-potential integral over a generated state trajectory.

        Generates a state trajectory and then computes the integral of the potential function
        along this trajectory.

        Args:
            time_points (np.ndarray): Array of time points for trajectory and integration.

        Returns:
            float: The value of the flux-potential integral.
        """
        trajectory = self.get_state_trajectory(time_points) # Generate state trajectory
        operator = self.operators[self.current_operator_key] # Get current operator
        integral_value = flux_potential_integral(self.current_state, operator, time_points) # Calculate flux-potential integral
        return integral_value


    @property
    def current_entropy(self) -> float:
        """
        Calculates and returns the Shannon entropy of the agent's current state.

        Returns:
            float: Shannon entropy of the current state.
        """
        return calculate_shannon_entropy(self.current_state) # Calculate Shannon entropy of current state


    @property
    def average_flux(self) -> float:
        """
        Calculates and returns the average flux density over the agent's history.

        Returns:
            float: Average flux density.
        """
        return np.mean(self.flux_history) if self.flux_history else 0.0 # Calculate average flux


if __name__ == '__main__':
    # Example operators
    operators_example = {
        'operator_A': np.array([[0.5, 0], [0, 0.5]]), # Example operator A: scaling down
        'operator_B': np.array([[0, -1], [1, 0]]), # Example operator B: rotation
        'operator_C':  np.array([[1.2, 0], [0, 1.2]]) # Example operator C: scaling up
    }


    def simple_operator_selection_strategy(agent: ScalableAgent) -> str:
        """
        A simple operator selection strategy that cycles through operators.
        """
        operator_keys = list(agent.operators.keys()) # Get list of operator keys
        current_index = operator_keys.index(agent.current_operator_key) # Find index of current operator
        next_index = (current_index + 1) % len(operator_keys) # Cycle to next index
        return operator_keys[next_index] # Return the next operator key


    # Example actions
    def explore_action(agent: ScalableAgent, operator: np.ndarray) -> np.ndarray:
        """Exploration action: Perturbs state randomly."""
        perturbation = np.random.normal(0, 0.1, size=agent.current_state.shape) # Small random perturbation
        return agent.current_state + perturbation


    def exploit_action(agent: ScalableAgent, operator: np.ndarray) -> np.ndarray:
        """Exploitation action: Applies potential function."""
        return potential_function(agent.current_state, operator) # Apply potential function


    def consolidate_action(agent: ScalableAgent, operator: np.ndarray) -> np.ndarray:
        """Consolidation action: Moves state towards origin."""
        return agent.current_state * 0.9 # Move state closer to zero/origin


    # Example action registry
    action_registry_example = {
        'explore': explore_action,
        'exploit': exploit_action,
        'consolidate': consolidate_action,
    }


    # Example workflow modes
    workflow_modes_example = {
        'mode_1': ['explore', 'exploit'], # Workflow mode 1: Explore then Exploit
        'mode_2': ['consolidate', 'exploit', 'explore'], # Workflow mode 2: Consolidate, Exploit, then Explore
        'mode_3': ['explore', 'consolidate'] # Workflow mode 3: Explore then Consolidate
    }


    # Initialize ScalableAgent
    initial_state_example = np.array([1.0, 1.0])
    agent = ScalableAgent(
        agent_id='agent_001',
        initial_state=initial_state_example,
        operators=operators_example,
        action_registry=action_registry_example,
        workflow_modes=workflow_modes_example,
        operator_selection_strategy=simple_operator_selection_strategy,
        initial_operator_key='operator_A' # Start with operator A
    )


    print(f"Initial Agent State: {agent.current_state}")
    print(f"Initial Operator Key: {agent.current_operator_key}")
    print(f"Initial Entropy: {agent.current_entropy:.4f}")


    # Run workflow mode_1
    print("\nRunning Workflow: mode_1")
    workflow_results_mode_1 = agent.run_workflow('mode_1')
    print(f"Workflow Results (mode_1): {[res.__class__.__name__ for res in workflow_results_mode_1]}") # Print result types
    print(f"Agent State After Workflow: {agent.current_state}")
    print(f"Current Operator Key: {agent.current_operator_key}")
    print(f"Current Entropy: {agent.current_entropy:.4f}")
    print(f"Average Flux: {agent.average_flux:.4f}")


    # Run workflow mode_2
    print("\nRunning Workflow: mode_2")
    workflow_results_mode_2 = agent.run_workflow('mode_2')
    print(f"Workflow Results (mode_2): {[res.__class__.__name__ for res in workflow_results_mode_2]}") # Print result types
    print(f"Agent State After Workflow: {agent.current_state}")
    print(f"Current Operator Key: {agent.current_operator_key}")
    print(f"Current Entropy: {agent.current_entropy:.4f}")
    print(f"Average Flux: {agent.average_flux:.4f}")


    # Example of getting state trajectory
    time_points_example = np.linspace(0, 10, 100)
    trajectory_example = agent.get_state_trajectory(time_points_example)
    print(f"\nState Trajectory Shape: {trajectory_example.shape}")
    print(f"Integrated Flux over Trajectory: {agent.calculate_integrated_flux_over_trajectory(time_points_example)[-1]:.4f}")
    print(f"Flux-Potential Integral over Trajectory: {agent.calculate_flux_potential_integral_over_trajectory(time_points_example):.4f}")


    # Example of Comparative Fluxual Processing
    agent_2 = ScalableAgent( # Create a second agent for comparison
        agent_id='agent_002',
        initial_state=initial_state_example * 0.8, # Slightly different initial state
        operators=operators_example,
        action_registry=action_registry_example,
        workflow_modes=workflow_modes_example,
        operator_selection_strategy=simple_operator_selection_strategy,
        initial_operator_key='operator_B' # Start with operator B
    )
    time_series_length = 5
    state_series_agent_1 = [agent.current_state] # Initialize state series for agent 1
    state_series_agent_2 = [agent_2.current_state] # Initialize state series for agent 2
    for _ in range(time_series_length - 1):
        agent.run_workflow('mode_1') # Evolve agent 1 state
        state_series_agent_1.append(agent.current_state.copy())
        agent_2.run_workflow('mode_2') # Evolve agent 2 state
        state_series_agent_2.append(agent_2.current_state.copy())


    cfp_metrics_agents = agent.run_comparative_fluxual_processing(state_series_agent_1, state_series_agent_2)
    print("\nComparative Fluxual Processing between Agent 001 and Agent 002:")
    print(f"CFP Metrics: {cfp_metrics_agents}") 