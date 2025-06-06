# ResonantiA Protocol v3.0 - agent_based_modeling_tool.py
# Implements Agent-Based Modeling (ABM) capabilities using Mesa (if available).
# Includes enhanced temporal analysis of results and mandatory IAR output.

import os
import json
import logging
import numpy as np
import pandas as pd
import time
import uuid # For unique filenames/run IDs
from typing import Dict, Any, List, Optional, Union, Tuple, Callable, Type # Expanded type hints
# Use relative imports for configuration
try:
    from . import config
except ImportError:
    # Fallback config if running standalone or package structure differs
    class FallbackConfig: OUTPUT_DIR = 'outputs'; ABM_VISUALIZATION_ENABLED = True; ABM_DEFAULT_ANALYSIS_TYPE='basic'; MODEL_SAVE_DIR='outputs/models' # Added model save dir
    config = FallbackConfig(); logging.warning("config.py not found for abm tool, using fallback configuration.")

# --- Import ScalableAgent ---
try:
    from .scalable_framework import ScalableAgent
    SCALABLE_AGENT_AVAILABLE = True
except ImportError:
    ScalableAgent = None
    SCALABLE_AGENT_AVAILABLE = False
    logging.getLogger(__name__).warning("scalable_framework.py not found. The 'scalable_agent' model type will not be available.")


# --- Import Mesa and Visualization Libraries (Set flag based on success) ---
MESA_AVAILABLE = False
VISUALIZATION_LIBS_AVAILABLE = False
SCIPY_AVAILABLE = False # For advanced pattern analysis
try:
    import mesa
    from mesa import Agent, Model
    # from mesa.scheduler import RandomActivation, SimultaneousActivation, StagedActivation # Removed these unused imports
    from mesa.space import MultiGrid, NetworkGrid
    from mesa.datacollection import DataCollector
    MESA_AVAILABLE = True
    logger_abm_imp = logging.getLogger(__name__)
    logger_abm_imp.info("Mesa library loaded successfully for ABM.")
    try:
        import matplotlib.pyplot as plt
        # import networkx as nx # Import if network models/analysis are used
        VISUALIZATION_LIBS_AVAILABLE = True
        logger_abm_imp.info("Matplotlib library loaded successfully for ABM visualization.")
    except ImportError:
        plt = None; nx = None
        logger_abm_imp.warning("Matplotlib/NetworkX not found. ABM visualization will be disabled.")
    try:
        from scipy import ndimage # For pattern detection example
        SCIPY_AVAILABLE = True
        logger_abm_imp.info("SciPy library loaded successfully for ABM analysis.")
    except ImportError:
        ndimage = None
        logger_abm_imp.warning("SciPy not found. Advanced ABM pattern analysis will be disabled.")

except ImportError as e_mesa:
    # Define dummy classes if Mesa is not installed
    mesa = None; Agent = object; Model = object
    # RandomActivation = object; SimultaneousActivation = object; StagedActivation = object # Removed dummy objects
    MultiGrid = object; NetworkGrid = object; DataCollector = object; plt = None; nx = None; ndimage = None
    logging.getLogger(__name__).warning(f"Mesa library import failed: {e_mesa}. ABM Tool will run in SIMULATION MODE.")
except Exception as e_mesa_other:
    mesa = None; Agent = object; Model = object
    # RandomActivation = object; SimultaneousActivation = object; StagedActivation = object # Removed dummy objects
    MultiGrid = object; NetworkGrid = object; DataCollector = object; plt = None; nx = None; ndimage = None
    logging.getLogger(__name__).error(f"Unexpected error importing Mesa/visualization libs: {e_mesa_other}. ABM Tool simulating.")


logger = logging.getLogger(__name__) # Logger for this module

# --- IAR Helper Function ---
# (Reused for consistency)
def _create_reflection(status: str, summary: str, confidence: Optional[float], alignment: Optional[str], issues: Optional[List[str]], preview: Any) -> Dict[str, Any]:
    """Helper function to create the standardized IAR reflection dictionary."""
    if confidence is not None: confidence = max(0.0, min(1.0, confidence))
    issues_list = issues if issues else None
    try:
        preview_str = str(preview) if preview is not None else None
        if preview_str and len(preview_str) > 150: preview_str = preview_str[:150] + "..."
    except Exception: preview_str = "[Preview Error]"
    return {"status": status, "summary": summary, "confidence": confidence, "alignment_check": alignment if alignment else "N/A", "potential_issues": issues_list, "raw_output_preview": preview_str}

# --- Default Agent and Model Implementations ---
# (Provide basic examples that can be overridden or extended)
class BasicGridAgent(Agent if MESA_AVAILABLE else object):
    """ A simple agent for grid-based models with a binary state. """
    def __init__(self, unique_id, model, state=0, **kwargs):
        if not MESA_AVAILABLE: # Simulation mode init
            self.unique_id = unique_id; self.model = model; self.pos = None
            self.state = state; self.next_state = state; self.params = kwargs
            return
        # Mesa init
        super().__init__(unique_id, model)
        self.state = int(state) # Ensure state is integer
        self.next_state = self.state
        self.params = kwargs # Store any extra parameters

    def step(self):
        """ Defines agent behavior within a simulation step. """
        if not MESA_AVAILABLE or not hasattr(self.model, 'grid') or self.model.grid is None or self.pos is None:
            # Handle simulation mode or cases where grid/pos is not set
            self.next_state = self.state
            return
        try:
            # Example logic: Activate if enough neighbors are active
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
            active_neighbors = sum(1 for a in neighbors if hasattr(a, 'state') and a.state > 0)
            # Use activation_threshold from the model if available, else default
            threshold = getattr(self.model, 'activation_threshold', 2)

            # Determine next state based on logic
            if self.state == 0 and active_neighbors >= threshold:
                self.next_state = 1
            elif self.state == 1 and active_neighbors < threshold -1 : # Example deactivation
                self.next_state = 0
            else:
                self.next_state = self.state # Maintain current state otherwise

        except Exception as e_agent_step:
            logger.error(f"Error in agent {self.unique_id} step at pos {self.pos}: {e_agent_step}", exc_info=True)
            self.next_state = self.state # Default to current state on error

    def advance(self):
        """ Updates the agent's state based on the calculated next_state. """
        # Check if next_state was calculated and differs from current state
        if hasattr(self, 'next_state') and self.state != self.next_state:
            self.state = self.next_state

class ScalableAgentModel(Model if MESA_AVAILABLE else object):
    """
    A Mesa model designed to run a simulation with multiple ScalableAgents.
    """
    def __init__(self, num_agents=10, agent_params: dict = None, **model_params):
        if not MESA_AVAILABLE or not SCALABLE_AGENT_AVAILABLE:
            self.run_id = uuid.uuid4().hex[:8]
            logger.warning(f"SIMULATING ScalableAgentModel (Run ID: {self.run_id}) as Mesa or ScalableAgent is not available.")
            return

        super().__init__()
        self.run_id = uuid.uuid4().hex[:8]
        self.num_agents = num_agents
        agent_params = agent_params or {}

        # Create agents
        for i in range(self.num_agents):
            # Create a unique initial state and operators for each agent
            # This is a placeholder; real scenarios would have more complex setup
            initial_state = agent_params.get('initial_state', np.random.rand(2))
            operators = agent_params.get('operators', {'default': np.eye(2)})
            
            agent = ScalableAgent(
                agent_id=f"scalable_{i}",
                initial_state=initial_state,
                operators=operators,
                action_registry=agent_params.get('action_registry', {}),
                workflow_modes=agent_params.get('workflow_modes', {}),
                operator_selection_strategy=agent_params.get('operator_selection_strategy', lambda a: next(iter(a.operators)))
            )
            self.schedule.add(agent)

        self.datacollector = DataCollector(
            agent_reporters={"State": "current_state", "Entropy": "current_entropy"}
        )

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)

class BasicGridModel(Model if MESA_AVAILABLE else object):
    """ A simple grid-based model using BasicGridAgent. """
    def __init__(self, width=10, height=10, density=0.5, activation_threshold=2, agent_class: Type[Agent] = BasicGridAgent, scheduler_type='random', torus=True, seed=None, **model_params):
        self._step_count = 0
        self.run_id = uuid.uuid4().hex[:8] # Assign a unique ID for this model run
        self._scheduler_type = scheduler_type.lower() # Store for use in step()

        if not MESA_AVAILABLE: # Simulation mode init
            self.random = np.random.RandomState(seed if seed is not None else int(time.time()))
            self.width = width; self.height = height; self.density = density; self.activation_threshold = activation_threshold; self.num_agents = 0
            self.agent_class = agent_class; self.custom_agent_params = model_params.get('agent_params', {})
            self.model_params = model_params; self.grid = None; 
            self.agents_sim = [] # Use a list for simulated agents
            self._create_agents_sim()
            self.num_agents = len(self.agents_sim)
            logger.info(f"Initialized SIMULATED BasicGridModel (Run ID: {self.run_id})")
            return
        
        # Mesa init
        super().__init__(seed=seed) # Pass seed to Mesa's base Model for reproducibility
        self.width = int(width); self.height = int(height); self.density = float(density); self.activation_threshold = int(activation_threshold)
        self.num_agents = 0 # Will be updated after agent creation
        self.agent_class = agent_class if issubclass(agent_class, Agent) else BasicGridAgent
        self.custom_agent_params = model_params.pop('agent_params', {}) # Extract agent params
        self.model_params = model_params # Store remaining model-level params

        # Setup grid
        self.grid = MultiGrid(self.width, self.height, torus=torus)
        
        # Note: In Mesa 3.0+, explicit scheduler instantiation (RandomActivation, etc.)
        # is replaced by AgentSet methods. The Model base class provides `self.agents` (an AgentSet).
        # We store the intended scheduler_type to be used by the step() method.
        if self._scheduler_type not in ['random', 'simultaneous', 'staged']:
            logger.warning(f"Unknown scheduler_type '{scheduler_type}'. Defaulting to 'random' behavior in step().")
            self._scheduler_type = 'random'

        # Setup data collection
        model_reporters = {
            "Active": lambda m: self.count_active_agents(),
            "Inactive": lambda m: self.count_inactive_agents()
        }
        agent_reporters = {"State": "state"}
        self.datacollector = DataCollector(model_reporters=model_reporters, agent_reporters=agent_reporters)

        # Create agents and place them. Agents are automatically added to self.agents (AgentSet)
        self._create_agents_mesa() 
        self.num_agents = len(self.agents) # self.agents is the AgentSet from Mesa's Model base class

        self.running = True
        self.datacollector.collect(self)
        logger.info(f"Initialized Mesa BasicGridModel (Run ID: {self.run_id}) with {self.num_agents} agents using '{self._scheduler_type}' activation style.")

    def _create_agents_mesa(self):
        """ Helper method to create agents for Mesa model. Agents are added to self.agents AgentSet. """
        agent_id_counter = 0 # unique_id is now auto-assigned by Mesa Model when adding to AgentSet
        initial_active_count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.random.random() < self.density:
                    initial_state = 1 if self.random.random() < 0.1 else 0
                    if initial_state == 1: initial_active_count += 1
                    # Create agent instance. Pass self (the model) for auto-assignment of unique_id.
                    agent = self.agent_class(self, state=initial_state, **self.custom_agent_params) 
                    # No need to explicitly call self.schedule.add(agent) or assign unique_id from counter
                    # The Model base class handles adding the agent to self.agents.
                    self.grid.place_agent(agent, (x, y))
        # num_agents will be len(self.agents) after this method, set in __init__
        logger.info(f"Created agents for Mesa model. Initial active: {initial_active_count}. Total agents in AgentSet: {len(self.agents)}")

    def _create_agents_sim(self):
        """ Helper method to create agents for simulation mode. """
        agent_id_counter = 0; initial_active_count = 0
        self.agents_sim = [] # Ensure it's a list for simulation
        for x in range(self.width):
            for y in range(self.height):
                if self.random.random() < self.density:
                        initial_state = 1 if self.random.random() < 0.1 else 0
                        if initial_state == 1: initial_active_count += 1
                        # For simulation, manually assign unique_id and store in a list
                        agent = self.agent_class(agent_id_counter, self, state=initial_state, **self.custom_agent_params); 
                        agent.unique_id = agent_id_counter # Explicit for sim
                        agent_id_counter += 1
                        agent.pos = (x, y); self.agents_sim.append(agent)
        logger.info(f"Created {len(self.agents_sim)} agents for SIMULATED model. Initial active: {initial_active_count}")

    def step(self):
        """ Advances the model by one step. """
        self._step_count += 1 # Mesa 3.0+ Model.steps auto-increments, but this can be model's internal counter
        if MESA_AVAILABLE:
            # Use AgentSet activation methods based on the stored scheduler type
            if self._scheduler_type == 'random':
                self.agents.shuffle_do("step") # Executes step() and then advance() for each agent in random order
                # In Mesa 3.0, shuffle_do typically handles both step and advance logic if agents define them.
                # If BasicGridAgent only has `step` to determine `next_state` and `advance` to apply it, this is fine.
                # For more complex agents that might have separate advance logic called by SimultaneousActivation, 
                # ensure shuffle_do covers it or adjust agent/model logic.
                # The default Agent.step() in Mesa 3.0 is a placeholder. Our BasicGridAgent.step() calculates next_state.
                # Our BasicGridAgent.advance() applies next_state. So, we need both.
                # However, `shuffle_do` calls the method passed to it. If we need sequential step then advance, it's more complex.
                # Let's assume for `BasicGridAgent`, `step` computes next_state and `advance` applies it.
                # Mesa's `shuffle_do("step")` calls `agent.step()`. Then `shuffle_do("advance")` would call `agent.advance()`.
                # For RandomActivation, the typical pattern is: each agent steps, then each agent advances.
                # It seems `shuffle_do` is for a single method call per agent. 
                # If RandomActivation implies step then advance for *each agent individually* before the next agent steps, 
                # then shuffle_do("step") might be enough if BasicGridAgent.step() calls self.advance() internally at the end.
                # Our current BasicGridAgent does not do that. So we need two passes for RandomActivation style.
                
                # According to Mesa 3.0 migration for RandomActivation:
                # Replace self.schedule.step() with self.agents.shuffle_do("step")
                # This implies shuffle_do("step") should be enough if the agent's step method does all its work for the turn.
                # Let's assume BasicGridAgent.step calculates next_state, and BasicGridAgent.advance applies it.
                # For random activation, usually all agents compute their next state, then all agents apply it.
                # So, it would be: self.agents.shuffle_do("step") and then self.agents.shuffle_do("advance")
                self.agents.do("step") # All agents determine their next_state
                self.agents.do("advance") # All agents apply their next_state (order for advance may not matter for BasicGridAgent)
                                        # Using `do` instead of `shuffle_do` for advance as order might not be critical for advance phase here.

            elif self._scheduler_type == 'simultaneous':
                # All agents compute their next state based on the *current* state of others
                self.agents.do("step") 
                # Then all agents apply their new state simultaneously
                self.agents.do("advance")
            elif self._scheduler_type == 'staged':
                # Assuming stage_list is defined, e.g., ["step", "advance"] or custom stages
                # For BasicGridAgent, the stages are effectively "step" (calculate) and "advance" (apply)
                stage_list = ["step", "advance"] # Default for BasicGridAgent
                # One could pass stage_list as a model parameter if models have more complex staging
                for stage_method_name in stage_list:
                    self.agents.do(stage_method_name)
            else: # Fallback, should have been defaulted in __init__
                logger.warning(f"Undefined scheduler type '{self._scheduler_type}' in step(), defaulting to random-like activation.")
                self.agents.do("step")
                self.agents.do("advance")

            self.datacollector.collect(self)
        else: # Simulate step for non-Mesa mode (simulation)
            # Simulation logic for self.agents_sim
            next_states = {}
            for agent in self.agents_sim: 
                active_neighbors_sim = 0
                if hasattr(agent, 'pos') and agent.pos is not None:
                    for dx in [-1, 0, 1]:
                            for dy in [-1, 0, 1]:
                                if dx == 0 and dy == 0: continue
                                nx, ny = agent.pos[0] + dx, agent.pos[1] + dy
                                neighbor = next((a for a in self.agents_sim if hasattr(a,'pos') and a.pos == (nx, ny)), None)
                                if neighbor and hasattr(neighbor, 'state') and neighbor.state > 0: active_neighbors_sim += 1
                current_state = getattr(agent, 'state', 0)
                # Using agent.params.get for activation_threshold if it was passed via agent_params to BasicGridAgent
                # Otherwise, using model's activation_threshold for simulation consistency
                sim_activation_threshold = agent.params.get('activation_threshold', self.activation_threshold)

                if current_state == 0 and active_neighbors_sim >= sim_activation_threshold: 
                    next_states[agent.unique_id] = 1
                # Example deactivation for simulation, matching BasicGridAgent logic roughly
                elif current_state == 1 and active_neighbors_sim < sim_activation_threshold -1: 
                    next_states[agent.unique_id] = 0
                else: 
                    next_states[agent.unique_id] = current_state
            
            for agent in self.agents_sim:
                if agent.unique_id in next_states:
                    setattr(agent, 'state', next_states[agent.unique_id])
            logger.debug(f"Simulated step {self._step_count} completed.")

    # Helper methods for data collection reporters
    def count_active_agents(self):
        """ Counts agents with state > 0. """
        return sum(1 for agent in self.agents if hasattr(agent, 'state') and agent.state > 0) if MESA_AVAILABLE else sum(1 for agent in self.agents_sim if hasattr(agent, 'state') and agent.state > 0)
    def count_inactive_agents(self):
        """ Counts agents with state <= 0. """
        return sum(1 for agent in self.agents if hasattr(agent, 'state') and agent.state <= 0) if MESA_AVAILABLE else sum(1 for agent in self.agents_sim if hasattr(agent, 'state') and agent.state <= 0)

    def get_agent_states(self) -> np.ndarray:
        """ Returns a 2D NumPy array representing the state of each agent on the grid. """
        states = np.full((self.width, self.height), -1.0)
        agent_list_to_iterate = self.agents if MESA_AVAILABLE else self.agents_sim
        if not agent_list_to_iterate: return states

        for agent in agent_list_to_iterate:
            # Check if agent has position and state attributes
            if hasattr(agent, 'pos') and agent.pos is not None and hasattr(agent, 'state'):
                try:
                    x, y = agent.pos
                    # Ensure position is within grid bounds before assignment
                    if 0 <= x < self.width and 0 <= y < self.height:
                            states[int(x), int(y)] = float(agent.state) # Use float for potential non-integer states
                    else:
                            logger.warning(f"Agent {getattr(agent,'unique_id','N/A')} has out-of-bounds position {agent.pos}. Skipping state assignment.")
                except (TypeError, IndexError) as pos_err:
                    logger.warning(f"Agent {getattr(agent,'unique_id','N/A')} position error during state retrieval: {pos_err}")
            # else: logger.debug(f"Agent {getattr(agent,'unique_id','N/A')} missing pos or state attribute.") # Optional debug
        return states

# --- ABM Tool Class (Handles Operations & IAR) ---
class ABMTool:
    """
    [IAR Enabled] Provides interface for creating, running, and analyzing
    Agent-Based Models using Mesa (if available) or simulation. Includes temporal analysis. (v3.0)
    """
    def __init__(self):
        self.is_available = MESA_AVAILABLE # Flag indicating if Mesa library loaded
        logger.info(f"ABM Tool (v3.0) initialized (Mesa Available: {self.is_available})")

    def create_model(self, model_type: str = "basic", agent_class: Optional[Type[Agent]] = None, **kwargs) -> Dict[str, Any]:
        """
        Creates an ABM model instance based on specified type and parameters.
        Returns a dictionary containing the model instance and reflection.
        """
        model_type = model_type.lower()
        logger.info(f"Attempting to create ABM model of type: '{model_type}'")
        # IAR setup
        reflection = _create_reflection("Failure", f"Model creation failed for type '{model_type}'.", 0.0, "N/A", ["Initialization error."], None)
        model = None
        
        try:
            if model_type == "basic":
                # For BasicGridModel, we expect grid dimensions and density
                width = kwargs.get('width', 10)
                height = kwargs.get('height', 10)
                density = kwargs.get('density', 0.5)
                model = BasicGridModel(width=width, height=height, density=density, agent_class=agent_class or BasicGridAgent, **kwargs)

            elif model_type == "scalable_agent":
                if not SCALABLE_AGENT_AVAILABLE:
                    raise ImportError("ScalableAgent framework is not available. Cannot create 'scalable_agent' model.")
                
                num_agents = kwargs.get('num_agents', 10)
                agent_params = kwargs.get('agent_params', {}) # Pass complex agent params here
                model = ScalableAgentModel(num_agents=num_agents, agent_params=agent_params, **kwargs)

            # ... (potential for other model types like "network")
            else:
                raise ValueError(f"Unknown model_type '{model_type}'. Supported types: 'basic', 'scalable_agent'.")

            if model:
                reflection = _create_reflection(
                    "Success", f"Successfully created ABM model '{model_type}' (Run ID: {getattr(model, 'run_id', 'N/A')}).",
                    0.95, "Model instantiated as per specification.", None,
                    f"Model: {model.__class__.__name__}, Agents: {getattr(model, 'num_agents', 'N/A')}"
                )
        except Exception as e_create:
            logger.error(f"Error creating ABM model '{model_type}': {e_create}", exc_info=True)
            reflection = _create_reflection("Failure", f"Model creation failed: {e_create}", 0.0, "N/A", [f"Model creation error: {e_create}"], None)

        return {
            "model": model, "type": model_type,
            "dimensions": [getattr(model,'width',None), getattr(model,'height',None)] if hasattr(model,'grid') and isinstance(model.grid, MultiGrid) else None,
            "agent_count": getattr(model,'num_agents',0),
            "params": {**getattr(model,'model_params',{}), "scheduler": getattr(model, 'scheduler_type', 'random'), "seed": getattr(model, 'seed', None), "torus": getattr(model, 'torus', True)},
            "agent_params_used": getattr(model,'custom_agent_params',{}),
            "reflection": reflection
        }

    def run_simulation(self, model: Any, steps: int = 100, visualize: bool = False, **kwargs) -> Dict[str, Any]:
        """
        [IAR Enabled] Runs the simulation for a given model instance for a number of steps.

        Args:
            model: The initialized Mesa Model instance (or simulated config dict).
            steps (int): The number of steps to run the simulation.
            visualize (bool): If True, attempt to generate and save a visualization.
            **kwargs: Additional arguments (currently unused, for future expansion).

        Returns:
            Dict containing simulation results (data, final state), optional visualization path, and IAR reflection.
        """
        # --- Initialize Results & Reflection ---
        primary_result = {"error": None, "simulation_steps_run": 0, "note": ""}
        reflection_status = "Failure"; reflection_summary = "Simulation initialization failed."; reflection_confidence = 0.0; reflection_alignment = "N/A"; reflection_issues = []; reflection_preview = None

        # --- Simulation Mode ---
        if not self.is_available:
            # Check if input is a simulated model config
            if isinstance(model, dict) and model.get("simulated"):
                primary_result["note"] = "SIMULATED results - Mesa library not available"
                logger.warning(f"Simulating ABM run for {steps} steps (Mesa unavailable).")
                sim_result = self._simulate_model_run(steps, visualize, model.get("width", 10), model.get("height", 10))
                primary_result.update(sim_result)
                primary_result["error"] = sim_result.get("error")
                if primary_result["error"]: reflection_issues = [primary_result["error"]]
                else: reflection_status = "Success"; reflection_summary = f"Simulated ABM run for {steps} steps completed."; reflection_confidence = 0.6; reflection_alignment = "Aligned with simulation goal (simulated)."; reflection_issues = ["Results are simulated."]; reflection_preview = {"steps": steps, "final_active": primary_result.get("active_count")}
                return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
            else:
                # Input is not a valid simulated model dict
                primary_result["error"] = "Mesa not available and input 'model' is not a valid simulated model configuration dictionary."
                reflection_issues = ["Mesa unavailable.", "Invalid input model type for simulation."]
                reflection_summary = "Input validation failed: Invalid model for simulation."
                return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

        # --- Actual Mesa Simulation ---
        if not isinstance(model, Model):
            primary_result["error"] = f"Input 'model' is not a valid Mesa Model instance (got {type(model)})."
            reflection_issues = ["Invalid input model type."]
            reflection_summary = "Input validation failed: Invalid model type."
            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

        try:
            start_time = time.time()
            model_run_id = getattr(model, 'run_id', 'unknown_run')
            logger.info(f"Running Mesa ABM simulation (Run ID: {model_run_id}) for {steps} steps...")
            # Ensure model is set to run
            model.running = True
            # Simulation loop
            for i in range(steps):
                if not model.running:
                    logger.info(f"Model stopped running at step {i} (model.running is False).")
                    break
                model.step() # Execute one step of the simulation
            # Record actual steps run (might be less than requested if model stopped early)
            final_step_count = getattr(getattr(model, 'schedule', None), 'steps', i + 1 if 'i' in locals() else steps) # Get steps from scheduler if possible
            run_duration = time.time() - start_time
            logger.info(f"Simulation loop finished after {final_step_count} steps in {run_duration:.2f} seconds.")

            primary_result["simulation_steps_run"] = final_step_count
            primary_result["simulation_duration_sec"] = round(run_duration, 2)
            primary_result["model_run_id"] = model_run_id # Include run ID in results

            # --- Collect Data ---
            model_data, agent_data = [], []
            model_data_df, agent_data_df = None, None # Store DataFrames if needed later
            if hasattr(model, 'datacollector') and model.datacollector:
                logger.debug("Attempting to retrieve data from Mesa DataCollector...")
                try:
                    model_data_df = model.datacollector.get_model_vars_dataframe()
                    if model_data_df is not None and not model_data_df.empty:
                        # Convert DataFrame to list of dicts for JSON serialization
                        model_data = model_data_df.reset_index().to_dict(orient='records')
                        logger.debug(f"Retrieved model data with {len(model_data)} steps.")
                    else: logger.debug("Model data is empty.")

                    agent_data_df = model.datacollector.get_agent_vars_dataframe()
                    if agent_data_df is not None and not agent_data_df.empty:
                        # Get agent data only for the *last* completed step
                        last_step_actual = model_data_df.index.max() if model_data_df is not None else final_step_count
                        if last_step_actual in agent_data_df.index.get_level_values('Step'):
                            last_step_agent_data = agent_data_df.xs(last_step_actual, level="Step")
                            agent_data = last_step_agent_data.reset_index().to_dict(orient='records')
                            logger.debug(f"Retrieved agent data for {len(agent_data)} agents at final step {last_step_actual}.")
                        else: logger.debug(f"No agent data found for final step {last_step_actual}.")
                    else: logger.debug("Agent data is empty.")
                except Exception as dc_error:
                    logger.warning(f"Could not process data from datacollector: {dc_error}", exc_info=True)
                    reflection_issues.append(f"DataCollector processing error: {dc_error}")
            else: logger.debug("Model has no datacollector attribute.")
            primary_result["model_data"] = model_data # Store collected model time series
            primary_result["agent_data_last_step"] = agent_data # Store agent states at final step

            # --- Get Final Grid State ---
            try:
                if hasattr(model, 'get_agent_states') and callable(model.get_agent_states):
                    final_states_array = model.get_agent_states()
                    primary_result["final_state_grid"] = final_states_array.tolist() # Convert numpy array for JSON
                    # Calculate final counts directly from model methods if available
                    if hasattr(model, 'count_active_agents'): primary_result["active_count"] = model.count_active_agents()
                    if hasattr(model, 'count_inactive_agents'): primary_result["inactive_count"] = model.count_inactive_agents()
                    logger.debug("Retrieved final agent state grid.")
                else: logger.warning("Model does not have a 'get_agent_states' method.")
            except Exception as state_error:
                logger.warning(f"Could not get final agent states: {state_error}", exc_info=True)
                reflection_issues.append(f"Error retrieving final state grid: {state_error}")

            # --- Generate Visualization (Optional) ---
            primary_result["visualization_path"] = None
            if visualize and VISUALIZATION_LIBS_AVAILABLE and getattr(config, 'ABM_VISUALIZATION_ENABLED', False):
                logger.info("Attempting to generate visualization...")
                # Pass dataframes if available for potentially richer plots
                viz_path = self._generate_visualization(model, final_step_count, primary_result, model_data_df, agent_data_df)
                if viz_path:
                    primary_result["visualization_path"] = viz_path
                else:
                    # Add note about failure to results and reflection
                    viz_error_msg = "Visualization generation failed (check logs)."
                    primary_result["visualization_error"] = viz_error_msg
                    reflection_issues.append(viz_error_msg)
            elif visualize:
                no_viz_reason = "Visualization disabled in config" if not getattr(config, 'ABM_VISUALIZATION_ENABLED', False) else "Matplotlib/NetworkX not available"
                logger.warning(f"Skipping visualization generation: {no_viz_reason}.")
                reflection_issues.append(f"Visualization skipped: {no_viz_reason}.")

            # --- IAR Success ---
            reflection_status = "Success"
            reflection_summary = f"ABM simulation (Run ID: {model_run_id}) completed {final_step_count} steps."
            # Confidence might depend on whether the simulation reached the requested steps or stopped early
            reflection_confidence = 0.9 if final_step_count == steps else 0.7
            reflection_alignment = "Aligned with simulation goal."
            # Issues list populated by warnings above
            reflection_preview = {
                "steps_run": final_step_count,
                "final_active": primary_result.get("active_count"),
                "viz_path": primary_result.get("visualization_path") }

        except Exception as e_run:
            # Catch errors during the simulation loop or data collection
            logger.error(f"Error running ABM simulation: {e_run}", exc_info=True)
            primary_result["error"] = str(e_run)
            reflection_issues = [f"Simulation runtime error: {e_run}"]
            reflection_summary = f"Simulation failed: {e_run}"

        # --- Finalize Reflection ---
        if primary_result["error"]:
            reflection_status = "Failure"
            if reflection_summary == "Simulation initialization failed.": # Update summary if error happened later
                reflection_summary = f"ABM simulation failed: {primary_result['error']}"
            reflection_confidence = 0.1

        return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    def _generate_visualization(self, model: Model, final_step_count: int, results_dict: Dict[str, Any], model_df: Optional[pd.DataFrame], agent_df: Optional[pd.DataFrame]) -> Optional[str]:
        """
        Internal helper to generate visualization PNG using Matplotlib.
        Uses data directly from results_dict or passed DataFrames.
        """
        if not VISUALIZATION_LIBS_AVAILABLE or plt is None: return None # Ensure library is available
        try:
            # Create output directory if it doesn't exist
            viz_dir = getattr(config, 'OUTPUT_DIR', 'outputs')
            os.makedirs(viz_dir, exist_ok=True)

            # Generate filename
            model_name_part = getattr(model, '__class__', type(model)).__name__ # Get model class name
            run_id = results_dict.get('model_run_id', uuid.uuid4().hex[:8]) # Use run ID if available
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            viz_filename = f"abm_sim_{model_name_part}_{run_id}_{timestamp}_step{final_step_count}.png"
            viz_path = os.path.join(viz_dir, viz_filename)

            # Create figure with subplots
            fig, axes = plt.subplots(1, 2, figsize=(16, 7)) # Adjust layout as needed
            fig.suptitle(f"ABM Simulation: {model_name_part} (Run: {run_id})", fontsize=14)

            # --- Plot 1: Final Grid State ---
            grid_list = results_dict.get("final_state_grid")
            ax1 = axes[0]
            if grid_list and isinstance(grid_list, list):
                try:
                    grid_array = np.array(grid_list)
                    if grid_array.ndim == 2:
                        im = ax1.imshow(grid_array.T, cmap='viridis', origin='lower', interpolation='nearest', aspect='auto') # Transpose for typical (x,y) mapping
                        ax1.set_title(f"Final Grid State (Step {final_step_count})")
                        ax1.set_xlabel("X Coordinate")
                        ax1.set_ylabel("Y Coordinate")
                        # Add colorbar, customize ticks if state values are discrete/few
                        unique_states = np.unique(grid_array)
                        cbar_ticks = unique_states if len(unique_states) < 10 and np.all(np.mod(unique_states, 1) == 0) else None
                        fig.colorbar(im, ax=ax1, label='Agent State', ticks=cbar_ticks)
                    else: ax1.text(0.5, 0.5, f'Grid data not 2D\n(Shape: {grid_array.shape})', ha='center', va='center', transform=ax1.transAxes); ax1.set_title("Final Grid State")
                except Exception as e_grid_plot: ax1.text(0.5, 0.5, f'Error plotting grid:\n{e_grid_plot}', ha='center', va='center', transform=ax1.transAxes); ax1.set_title("Final Grid State")
            else: ax1.text(0.5, 0.5, 'Final Grid State Data N/A', ha='center', va='center', transform=ax1.transAxes); ax1.set_title("Final Grid State")

            # --- Plot 2: Time Series Data (Model Variables) ---
            ax2 = axes[1]
            if model_df is not None and not model_df.empty:
                try:
                    # Plot all columns from the model dataframe against the index (Step)
                    model_df.plot(ax=ax2, grid=True)
                    ax2.set_title("Model Variables Over Time")
                    ax2.set_xlabel("Step")
                    ax2.set_ylabel("Count / Value")
                    ax2.legend(loc='best')
                except Exception as e_ts_plot: ax2.text(0.5, 0.5, f'Error plotting time series:\n{e_ts_plot}', ha='center', va='center', transform=ax2.transAxes); ax2.set_title("Model Variables Over Time")
            else: # Fallback to list if DataFrame wasn't available/processed
                model_data_list = results_dict.get("model_data")
                if model_data_list and isinstance(model_data_list, list):
                    try:
                            df_fallback = pd.DataFrame(model_data_list)
                            if 'Step' in df_fallback.columns: df_fallback = df_fallback.set_index('Step')
                            if not df_fallback.empty:
                                df_fallback.plot(ax=ax2, grid=True)
                                ax2.set_title("Model Variables Over Time"); ax2.set_xlabel("Step"); ax2.set_ylabel("Count / Value"); ax2.legend(loc='best')
                            else: raise ValueError("Fallback DataFrame is empty.")
                    except Exception as e_ts_plot_fb: ax2.text(0.5, 0.5, f'Error plotting fallback time series:\n{e_ts_plot_fb}', ha='center', va='center', transform=ax2.transAxes); ax2.set_title("Model Variables Over Time")
                else: ax2.text(0.5, 0.5, 'Model Time Series Data N/A', ha='center', va='center', transform=ax2.transAxes); ax2.set_title("Model Variables Over Time")

            # --- Finalize Plot ---
            plt.tight_layout(rect=[0, 0.03, 1, 0.95]) # Adjust layout to prevent title overlap
            plt.savefig(viz_path)
            plt.close(fig) # Close figure to free memory
            logger.info(f"ABM Visualization saved successfully to: {viz_path}")
            return viz_path
        except Exception as viz_error:
            logger.error(f"Error generating ABM visualization: {viz_error}", exc_info=True)
            # Clean up partial file if save failed mid-way? Maybe not necessary.
            if 'viz_path' in locals() and os.path.exists(viz_path):
                try: os.remove(viz_path)
                except Exception: pass
            return None

    def analyze_results(self, results: Dict[str, Any], analysis_type: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """
        [IAR Enabled] Analyzes results from an ABM simulation run.
        Includes enhanced temporal analysis (convergence, oscillation) and spatial patterns.

        Args:
            results (Dict[str, Any]): The dictionary returned by run_simulation.
            analysis_type (str, optional): Type of analysis ('basic', 'pattern', 'network').
                                        Defaults to config.ABM_DEFAULT_ANALYSIS_TYPE.
            **kwargs: Additional parameters for specific analysis types.

        Returns:
            Dict containing analysis results nested under 'analysis' key, and IAR reflection.
        """
        analysis_type_used = analysis_type or getattr(config, 'ABM_DEFAULT_ANALYSIS_TYPE', 'basic')
        # --- Initialize Results & Reflection ---
        primary_result = {"analysis_type": analysis_type_used, "analysis": {}, "error": None, "note": ""}
        reflection_status = "Failure"; reflection_summary = f"Analysis init failed for type '{analysis_type_used}'."; reflection_confidence = 0.0; reflection_alignment = "N/A"; reflection_issues = []; reflection_preview = None

        # --- Simulation Mode ---
        is_simulated_input = "SIMULATED" in results.get("note", "")
        if not self.is_available and is_simulated_input:
            primary_result["note"] = f"SIMULATED {analysis_type_used} analysis - Mesa library not available"
            logger.warning(f"Simulating ABM result analysis '{analysis_type_used}' (Mesa unavailable).")
            sim_analysis = self._simulate_result_analysis(analysis_type_used, results) # Pass results for context
            primary_result["analysis"] = sim_analysis.get("analysis", {})
            primary_result["error"] = sim_analysis.get("error")
            if primary_result["error"]: reflection_issues = [primary_result["error"]]
            else: reflection_status = "Success"; reflection_summary = f"Simulated analysis '{analysis_type_used}' completed."; reflection_confidence = 0.6; reflection_alignment = "Aligned with analysis goal (simulated)."; reflection_issues = ["Analysis is simulated."]; reflection_preview = primary_result["analysis"]
            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}
        elif not self.is_available and not is_simulated_input:
            # If Mesa isn't available but input isn't marked simulated, proceed cautiously
            logger.warning("Mesa not available, attempting basic analysis on potentially real results dictionary structure.")
            # Fall through to actual analysis logic, which might partially work if keys match

        # --- Actual Analysis ---
        try:
            logger.info(f"Analyzing ABM results using '{analysis_type_used}' analysis...")
            analysis_output: Dict[str, Any] = {} # Store specific analysis metrics here
            error_msg = results.get("error") # Propagate error from simulation run if present
            if error_msg: logger.warning(f"Analyzing results from a simulation run that reported an error: {error_msg}")

            # --- Analysis Type Dispatcher ---
            if analysis_type_used == "basic":
                # Perform basic temporal and spatial analysis
                analysis_output["time_series"] = self._analyze_time_series(results)
                analysis_output["spatial"] = self._analyze_spatial(results)
                # Check for errors reported by sub-analyzers
                ts_error = analysis_output["time_series"].get("error")
                sp_error = analysis_output["spatial"].get("error")
                if ts_error or sp_error: error_msg = f"Time Series Error: {ts_error}; Spatial Error: {sp_error}"

            elif analysis_type_used == "pattern":
                # Perform pattern detection using SciPy (if available)
                if not SCIPY_AVAILABLE: error_msg = "SciPy library required for 'pattern' analysis but not available."
                else: analysis_output["detected_patterns"] = self._detect_patterns(results)
                pattern_error = next((p.get("error") for p in analysis_output.get("detected_patterns",[]) if isinstance(p,dict) and p.get("error")), None)
                if pattern_error: error_msg = f"Pattern detection error: {pattern_error}"

            # --- Add other analysis types here ---
            # elif analysis_type_used == "network":
            #     if not nx: error_msg = "NetworkX library required for 'network' analysis but not available."
            #     else:
            #         # Requires model to have a graph attribute or agent data suitable for graph construction
            #         # analysis_output["network_metrics"] = self._analyze_network(results) ...
            #         error_msg = "Network analysis not implemented."

            else:
                error_msg = f"Unknown analysis type specified: {analysis_type_used}"

            # Store results and potential errors
            primary_result["analysis"] = analysis_output
            primary_result["error"] = error_msg # Update error status

            # --- Generate Final IAR Reflection ---
            if primary_result["error"]:
                reflection_status = "Failure"; reflection_summary = f"ABM analysis '{analysis_type_used}' failed: {primary_result['error']}"; reflection_confidence = 0.1; reflection_issues = [primary_result["error"]]
                reflection_alignment = "Failed to meet analysis goal."
            else:
                reflection_status = "Success"; reflection_summary = f"ABM analysis '{analysis_type_used}' completed successfully."; reflection_confidence = 0.85; reflection_alignment = "Aligned with analyzing simulation results."; reflection_issues = None; reflection_preview = analysis_output
                if not self.is_available: reflection_issues = ["Analysis performed without Mesa library validation."] # Add note if Mesa missing

            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

        except Exception as e_analyze:
            # Catch unexpected errors during analysis orchestration
            logger.error(f"Unexpected error analyzing ABM results: {e_analyze}", exc_info=True)
            primary_result["error"] = str(e_analyze)
            reflection_issues = [f"Unexpected analysis error: {e_analyze}"]
            reflection_summary = f"Analysis failed: {e_analyze}"
            return {**primary_result, "reflection": _create_reflection("Failure", reflection_summary, 0.0, "N/A", reflection_issues, None)}

    # --- Internal Helper Methods for Analysis ---
    def _analyze_time_series(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes model-level time series data for temporal patterns."""
        ts_analysis: Dict[str, Any] = {"error": None}
        model_data_list = results.get("model_data")
        active_count = results.get("active_count") # Final count from simulation result
        inactive_count = results.get("inactive_count")
        total_agents = self._get_total_agents(results)

        if not model_data_list or not isinstance(model_data_list, list):
            ts_analysis["error"] = "Model time series data ('model_data' list) not found or invalid."
            return ts_analysis

        try:
            # Extract 'Active' agent count time series (assuming it was collected)
            active_series = [step_data.get('Active') for step_data in model_data_list if isinstance(step_data, dict) and 'Active' in step_data]
            if not active_series or any(x is None for x in active_series):
                ts_analysis["error"] = "'Active' agent count not found in model_data steps."
                return ts_analysis

            active_series_numeric = [float(x) for x in active_series] # Convert to float
            num_steps = len(active_series_numeric)
            ts_analysis["num_steps"] = num_steps
            ts_analysis["final_active"] = active_count if active_count is not None else active_series_numeric[-1]
            ts_analysis["final_inactive"] = inactive_count if inactive_count is not None else (total_agents - ts_analysis["final_active"] if total_agents is not None and ts_analysis["final_active"] is not None else None)
            ts_analysis["max_active"] = float(max(active_series_numeric)) if active_series_numeric else None
            ts_analysis["min_active"] = float(min(active_series_numeric)) if active_series_numeric else None
            ts_analysis["avg_active"] = float(sum(active_series_numeric) / num_steps) if num_steps > 0 else None

            # Temporal Pattern Detection
            ts_analysis["convergence_step"] = self._detect_convergence(active_series_numeric) # Returns step index or -1
            ts_analysis["oscillating"] = bool(self._detect_oscillation(active_series_numeric)) # Returns boolean

            logger.debug(f"Time series analysis complete. Convergence: {ts_analysis['convergence_step']}, Oscillation: {ts_analysis['oscillating']}")

        except Exception as e_ts:
            logger.error(f"Error during time series analysis: {e_ts}", exc_info=True)
            ts_analysis["error"] = f"Time series analysis failed: {e_ts}"

        return ts_analysis

    def _analyze_spatial(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyzes the final spatial grid state for patterns."""
        sp_analysis: Dict[str, Any] = {"error": None}
        final_state_grid_list = results.get("final_state_grid")

        if not final_state_grid_list or not isinstance(final_state_grid_list, list):
            sp_analysis["error"] = "Final state grid ('final_state_grid' list) not found or invalid."
            return sp_analysis

        try:
            grid = np.array(final_state_grid_list)
            if grid.ndim != 2:
                sp_analysis["error"] = f"Final state grid data is not 2-dimensional (shape: {grid.shape})."
                return sp_analysis

            sp_analysis["grid_dimensions"] = list(grid.shape)
            sp_analysis["active_cell_count"] = int(np.sum(grid > 0.5)) # Example: count cells with state > 0.5
            sp_analysis["active_ratio"] = float(np.mean(grid > 0.5)) if grid.size > 0 else 0.0

            # Calculate spatial metrics (examples)
            sp_analysis["clustering_coefficient"] = self._calculate_clustering(grid) # Avg local similarity
            sp_analysis["spatial_entropy"] = self._calculate_entropy(grid) # Shannon entropy of grid states

            logger.debug(f"Spatial analysis complete. Clustering: {sp_analysis['clustering_coefficient']:.4f}, Entropy: {sp_analysis['spatial_entropy']:.4f}")

        except Exception as e_sp:
            logger.error(f"Error during spatial analysis: {e_sp}", exc_info=True)
            sp_analysis["error"] = f"Spatial analysis failed: {e_sp}"

        return sp_analysis

    def _detect_patterns(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detects spatial patterns like clusters using SciPy (if available)."""
        patterns: List[Dict[str, Any]] = []
        if not SCIPY_AVAILABLE or ndimage is None:
            patterns.append({"note": "SciPy library not available, cannot perform pattern detection."})
            return patterns

        final_state_grid_list = results.get("final_state_grid")
        if not final_state_grid_list or not isinstance(final_state_grid_list, list):
            patterns.append({"error": "Final state grid not found for pattern detection."})
            return patterns

        try:
            grid = np.array(final_state_grid_list)
            if grid.ndim != 2:
                patterns.append({"error": f"Pattern detection requires 2D grid, got shape {grid.shape}."})
                return patterns

            # Example: Detect clusters of "active" cells (state > 0.5)
            threshold = 0.5 # Define what constitutes an "active" cell for clustering
            active_cells = (grid > threshold).astype(int)
            # Define connectivity structure (e.g., 8-connectivity for 2D)
            structure = ndimage.generate_binary_structure(2, 2)
            # Label connected components (clusters)
            labeled_clusters, num_features = ndimage.label(active_cells, structure=structure)

            if num_features > 0:
                logger.info(f"Detected {num_features} active spatial clusters.")
                cluster_indices = range(1, num_features + 1) # Indices used by ndimage functions
                # Calculate properties for each cluster
                cluster_sizes = ndimage.sum_labels(active_cells, labeled_clusters, index=cluster_indices)
                centroids = ndimage.center_of_mass(active_cells, labeled_clusters, index=cluster_indices) # Returns list of (row, col) tuples
                # Calculate average state value within each cluster using original grid
                avg_values = ndimage.mean(grid, labeled_clusters, index=cluster_indices)

                for i in range(num_features):
                    centroid_coords = centroids[i] if isinstance(centroids, list) else centroids # Handle single cluster case
                    patterns.append({
                        "type": "active_cluster",
                        "id": int(cluster_indices[i]),
                        "size": int(cluster_sizes[i]),
                        "centroid_row": float(centroid_coords[0]), # row index
                        "centroid_col": float(centroid_coords[1]), # column index
                        "average_state_in_cluster": float(avg_values[i])
                    })
            else:
                logger.info("No active spatial clusters detected.")
                patterns.append({"note": "No significant active clusters found."})

        except Exception as e_pattern:
            logger.error(f"Error during pattern detection: {e_pattern}", exc_info=True)
            patterns.append({"error": f"Pattern detection failed: {e_pattern}"})

        return patterns

    def convert_to_state_vector(self, abm_result: Dict[str, Any], representation_type: str = "final_state", **kwargs) -> Dict[str, Any]:
        """
        [IAR Enabled] Converts ABM simulation results into a normalized state vector
        suitable for comparison (e.g., using CFP).

        Args:
            abm_result (Dict[str, Any]): The dictionary returned by run_simulation or analyze_results.
            representation_type (str): Method for conversion ('final_state', 'time_series', 'metrics').
            **kwargs: Additional parameters (e.g., num_ts_steps for time_series).

        Returns:
            Dict containing 'state_vector' (list), 'dimensions', 'representation_type', and IAR reflection.
        """
        # --- Initialize Results & Reflection ---
        primary_result = {"state_vector": None, "representation_type": representation_type, "dimensions": 0, "error": None}
        reflection_status = "Failure"; reflection_summary = f"State conversion init failed for type '{representation_type}'."; reflection_confidence = 0.0; reflection_alignment = "N/A"; reflection_issues = []; reflection_preview = None

        # Check if input result itself indicates an error
        input_error = abm_result.get("error")
        if input_error:
            primary_result["error"] = f"Input ABM result contains error: {input_error}"
            reflection_issues = [primary_result["error"]]
            reflection_summary = f"Input ABM result invalid: {input_error}"
            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

        logger.info(f"Converting ABM results to state vector using representation: '{representation_type}'")
        state_vector = np.array([])
        error_msg = None
        try:
            if representation_type == "final_state":
                # Use the flattened final grid state
                final_grid_list = abm_result.get("final_state_grid")
                if final_grid_list and isinstance(final_grid_list, list):
                    state_vector = np.array(final_grid_list).flatten()
                    if state_vector.size == 0: error_msg = "Final state grid is empty."
                else: error_msg = "Final state grid ('final_state_grid') not available or invalid in ABM results."
            elif representation_type == "time_series":
                # Use the last N steps of key model variables (e.g., 'Active' count)
                model_data_list = abm_result.get("model_data")
                num_ts_steps = int(kwargs.get('num_ts_steps', 10)) # Number of recent steps to use
                variable_to_use = kwargs.get('variable', 'Active') # Which variable to use
                if model_data_list and isinstance(model_data_list, list) and len(model_data_list) > 0:
                    try:
                        series = [step_data.get(variable_to_use) for step_data in model_data_list if isinstance(step_data, dict) and variable_to_use in step_data]
                        if not series or any(x is None for x in series): error_msg = f"Time series variable '{variable_to_use}' not found or contains None values."
                        else:
                            series_numeric = np.array(series, dtype=float)
                            # Take last num_ts_steps, pad if shorter
                            if len(series_numeric) >= num_ts_steps: state_vector = series_numeric[-num_ts_steps:]
                            else: padding = np.zeros(num_ts_steps - len(series_numeric)); state_vector = np.concatenate((padding, series_numeric))
                    except Exception as ts_parse_err: error_msg = f"Could not parse '{variable_to_use}' time series: {ts_parse_err}"
                else: error_msg = "Model time series data ('model_data') not available or empty."
            elif representation_type == "metrics":
                # Use summary metrics calculated by analyze_results (requires analysis to be run first)
                analysis_data = abm_result.get("analysis", {}).get("analysis") # Get nested analysis dict
                if analysis_data and isinstance(analysis_data, dict):
                    metrics = []
                    # Extract metrics from time series and spatial analysis (handle potential errors)
                    ts_analysis = analysis_data.get("time_series", {})
                    sp_analysis = analysis_data.get("spatial", {})
                    metrics.append(float(ts_analysis.get("final_active", 0) or 0))
                    metrics.append(float(ts_analysis.get("convergence_step", -1) or -1)) # Use -1 if not converged
                    metrics.append(1.0 if ts_analysis.get("oscillating", False) else 0.0)
                    metrics.append(float(sp_analysis.get("clustering_coefficient", 0) or 0))
                    metrics.append(float(sp_analysis.get("spatial_entropy", 0) or 0))
                    metrics.append(float(sp_analysis.get("active_ratio", 0) or 0))
                    state_vector = np.array(metrics)
                else: error_msg = "'analysis' results subsection not found or invalid in ABM results. Run 'analyze_results' first for 'metrics' conversion."
            else:
                error_msg = f"Unknown representation type for ABM state conversion: {representation_type}"

            # --- Final Processing & Normalization ---
            if error_msg:
                primary_result["error"] = error_msg
                state_vector = np.array([0.0, 0.0]) # Default error state vector
            elif state_vector.size == 0:
                logger.warning(f"Resulting state vector for type '{representation_type}' is empty. Using default error state.")
                state_vector = np.array([0.0, 0.0]) # Handle empty vector case

            # Normalize the final state vector (L2 norm)
            norm = np.linalg.norm(state_vector)
            if norm > 1e-15:
                state_vector_normalized = state_vector / norm
            else:
                logger.warning(f"State vector for type '{representation_type}' has zero norm. Not normalizing.")
                state_vector_normalized = state_vector # Avoid division by zero

            state_vector_list = state_vector_normalized.tolist()
            dimensions = len(state_vector_list)
            primary_result.update({"state_vector": state_vector_list, "dimensions": dimensions})

            # --- Generate IAR Reflection ---
            if primary_result["error"]:
                reflection_status = "Failure"; reflection_summary = f"State conversion failed: {primary_result['error']}"; reflection_confidence = 0.1; reflection_issues = [primary_result["error"]]
                reflection_alignment = "Failed to convert state."
            else:
                reflection_status = "Success"; reflection_summary = f"ABM results successfully converted to state vector (type: {representation_type}, dim: {dimensions})."; reflection_confidence = 0.9; reflection_alignment = "Aligned with preparing data for comparison/CFP."; reflection_issues = None; reflection_preview = state_vector_list

            return {**primary_result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

        except Exception as e_conv:
            # Catch unexpected errors during conversion process
            logger.error(f"Unexpected error converting ABM results to state vector: {e_conv}", exc_info=True)
            primary_result["error"] = f"Unexpected conversion failure: {e_conv}"
            reflection_issues = [f"Unexpected conversion error: {e_conv}"]
            reflection_summary = f"Conversion failed: {e_conv}"
            # Ensure default state vector is set on critical error
            if primary_result.get("state_vector") is None: primary_result["state_vector"] = [0.0, 0.0]; primary_result["dimensions"] = 2
            return {**primary_result, "reflection": _create_reflection("Failure", reflection_summary, 0.0, "N/A", reflection_issues, None)}

    # --- Internal Simulation Methods ---
    # (These simulate outcomes when Mesa is unavailable)
    def _simulate_model_creation(self, model_type, agent_class=None, **kwargs):
        """Simulates model creation when Mesa is not available."""
        logger.info(f"Simulating creation of {model_type} model")
        width=kwargs.get('width',10); height=kwargs.get('height',10); density=kwargs.get('density',0.5)
        model_params=kwargs.get('model_params',{}); agent_params=kwargs.get('agent_params',{})        
        # Return a dictionary representing the simulated model's configuration
        sim_model_config = {
            "simulated": True, "type": model_type, "width": width, "height": height, "density": density,
            "params": {**model_params, "simulated": True}, "agent_params": agent_params,
            "agent_class_name": getattr(agent_class or BasicGridAgent, '__name__', 'UnknownAgent'),
            "run_id": uuid.uuid4().hex[:8] # Give simulation a run ID
        }
        return {
            "model": sim_model_config, "type": model_type,
            "dimensions": [width, height], "initial_density": density,
            "agent_count": int(width * height * density),
            "params": {**model_params, "simulated": True},
            "agent_params_used": agent_params, "error": None
        }

    def _simulate_model_run(self, steps, visualize, width=10, height=10):
        """Simulates running the model when Mesa is not available."""
        logger.info(f"Simulating ABM run for {steps} steps ({width}x{height} grid)")
        np.random.seed(int(time.time()) % 1000 + 2) # Seed for some variability
        active_series = []; inactive_series = []; total_agents = width * height;
        current_active = total_agents * np.random.uniform(0.05, 0.15) # Random initial active
        for i in range(steps):
            # Simple random walk simulation for active count
            equilibrium = total_agents * np.random.uniform(0.4, 0.6); # Fluctuate equilibrium
            drift = (equilibrium - current_active) * np.random.uniform(0.02, 0.08);
            noise = np.random.normal(0, total_agents * 0.03);
            change = drift + noise
            current_active = max(0, min(total_agents, current_active + change))
            active_series.append(current_active); inactive_series.append(total_agents - current_active)

        # Simulate final grid state based on final active ratio
        grid = np.zeros((width, height));
        active_ratio_final = active_series[-1] / total_agents if total_agents > 0 else 0
        grid[np.random.rand(width, height) < active_ratio_final] = 1 # Randomly assign active state

        results = {
            "model_data": [{"Step": i, "Active": active_series[i], "Inactive": inactive_series[i]} for i in range(steps)],
            "agent_data_last_step": {"note": "Agent data not generated in simulation"},
            "final_state_grid": grid.tolist(),
            "active_count": int(round(active_series[-1])),
            "inactive_count": int(round(inactive_series[-1])),
            "simulation_steps_run": steps,
            "error": None
        }
        if visualize:
            results["visualization_path"] = "simulated_visualization_not_generated.png"
            results["visualization_error"] = "Visualization skipped in simulation mode."
        return results

    def _simulate_result_analysis(self, analysis_type, results=None):
        """Simulates analysis of ABM results when libraries are unavailable."""
        logger.info(f"Simulating '{analysis_type}' analysis of ABM results")
        analysis: Dict[str, Any] = {"analysis_type": analysis_type, "error": None}
        np.random.seed(int(time.time()) % 1000 + 3) # Seed for variability

        if analysis_type == "basic":
            # Simulate plausible metrics
            final_active = results.get('active_count', 55.0 + np.random.rand()*10) if results else 55.0 + np.random.rand()*10
            total_agents = results.get('agent_count', 100) if results else 100
            analysis["time_series"] = {
                "final_active": float(final_active),
                "final_inactive": float(total_agents - final_active if total_agents else 45.0 - np.random.rand()*10),
                "max_active": float(final_active * np.random.uniform(1.1, 1.5)),
                "avg_active": float(final_active * np.random.uniform(0.8, 1.1)),
                "convergence_step": int(results.get('simulation_steps_run', 50) * np.random.uniform(0.6, 0.9)) if results else int(30 + np.random.rand()*20),
                "oscillating": bool(np.random.choice([True, False], p=[0.3, 0.7]))
            }
            analysis["spatial"] = {
                "grid_dimensions": results.get('dimensions', [10,10]) if results else [10,10],
                "clustering_coefficient": float(np.random.uniform(0.5, 0.8)),
                "spatial_entropy": float(np.random.uniform(0.6, 0.95)),
                "active_ratio": float(final_active / total_agents if total_agents else 0.55 + np.random.rand()*0.1)
            }
        elif analysis_type == "pattern":
            num_clusters = np.random.randint(0, 4)
            patterns = []
            for i in range(num_clusters):
                patterns.append({
                    "type": "active_cluster (simulated)", "id": i+1,
                    "size": int(10 + np.random.rand()*15),
                    "centroid_row": float(np.random.uniform(2, 8)), # Assuming 10x10 grid roughly
                    "centroid_col": float(np.random.uniform(2, 8)),
                    "average_state_in_cluster": float(np.random.uniform(0.8, 1.0))
                })
            if not patterns: patterns.append({"note": "No significant clusters found (simulated)."})
            analysis["detected_patterns"] = patterns
        # Add simulation for other analysis types (e.g., network) if needed
        else:
            analysis["error"] = f"Unknown or unimplemented simulated analysis type: {analysis_type}"

        return {"analysis": analysis, "error": analysis.get("error")}

    def _get_total_agents(self, results: Dict[str, Any]) -> Optional[int]:
        """Helper to get total agent count from results, if available."""
        active_count = results.get("active_count")
        inactive_count = results.get("inactive_count")
        if active_count is not None and inactive_count is not None:
            return int(active_count + inactive_count)
        # Fallback: Try to infer from grid dimensions if available
        final_grid = results.get("final_state_grid")
        if isinstance(final_grid, list) and final_grid:
            try: return np.array(final_grid).size # Approx if not all cells have agents
            except: pass
        # Fallback: Try agent_data_last_step
        agent_data = results.get("agent_data_last_step")
        if isinstance(agent_data, list): return len(agent_data)
        # Fallback: from original model params (if passed through)
        # This requires model object or its params to be in results, which is not standard for run_simulation output alone.
        return None

    def _detect_convergence(self, series: List[float], window: int = 10, threshold: float = 0.01) -> int:
        """Detects if a time series has converged. Returns step index or -1."""
        if len(series) < window * 2: return -1 # Not enough data
        # Check if the standard deviation of the last `window` points is below threshold
        # And if the mean of the last `window` is close to the mean of the `window` before it
        try:
            last_segment = np.array(series[-window:])
            prev_segment = np.array(series[-window*2:-window])
            if last_segment.std() < threshold and np.abs(last_segment.mean() - prev_segment.mean()) < threshold:
                return len(series) - window # Approximate step of convergence start
        except Exception: pass # Handle empty segments or other errors
        return -1

    def _detect_oscillation(self, series: List[float], window: int = 10, threshold_std_dev: float = 0.1, threshold_peaks: int = 3) -> bool:
        """Detects if a time series is oscillating. Returns boolean."""
        if len(series) < window * 2: return False # Not enough data
        try:
            # Check if there are enough peaks/troughs in the recent segment
            # And if the standard deviation is above a certain level (not flat)
            segment = np.array(series[-window*2:]) # Analyze a larger recent window for oscillation
            if segment.std() < threshold_std_dev: return bool(False) # Likely flat
            # Simple peak detection (could use SciPy find_peaks for more robustness)
            peaks = sum(1 for i in range(1, len(segment)-1) if segment[i-1] < segment[i] > segment[i+1])
            troughs = sum(1 for i in range(1, len(segment)-1) if segment[i-1] > segment[i] < segment[i+1])
            if peaks >= threshold_peaks or troughs >= threshold_peaks: return bool(True)
        except Exception: pass
        return bool(False)

    def _calculate_clustering(self, grid: np.ndarray, threshold: float = 0.5) -> float:
        """Calculates a simple spatial clustering coefficient (average local similarity)."""
        if grid.size == 0: return 0.0
        active_grid = (grid > threshold).astype(int)
        rows, cols = active_grid.shape
        total_similarity = 0; count = 0
        for r in range(rows): # Iterate over each cell
            for c in range(cols):
                cell_state = active_grid[r, c]
                # Get 8-Moore neighbors
                local_sum = 0; num_neighbors = 0
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        if dr == 0 and dc == 0: continue
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            num_neighbors += 1
                            if active_grid[nr, nc] == cell_state: local_sum +=1 # Count neighbors with same state
                if num_neighbors > 0: total_similarity += (local_sum / num_neighbors); count +=1
        return total_similarity / count if count > 0 else 0.0

    def _calculate_entropy(self, grid: np.ndarray) -> float:
        """Calculates Shannon entropy of the grid states (assumes discrete states)."""
        if grid.size == 0: return 0.0
        _, counts = np.unique(grid, return_counts=True)
        probabilities = counts / grid.size
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-12)) # Add epsilon to avoid log(0)
        return float(entropy)


# --- Main Wrapper Function (Handles Operations & IAR) ---
def perform_abm(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    [IAR Enabled] Main wrapper function for dispatching ABM operations.
    Instantiates ABMTool and calls the appropriate method based on 'operation'.

    Args:
        inputs (Dict[str, Any]): Dictionary containing:
            operation (str): The ABM operation ('create_model', 'run_simulation',
                            'analyze_results', 'convert_to_state'). Required.
            **kwargs: Other inputs specific to the operation (e.g., model, steps,
                    results, analysis_type, representation_type).

    Returns:
        Dict[str, Any]: Dictionary containing results and the IAR reflection.
    """
    operation = inputs.get("operation")
    # Pass all other inputs as kwargs to the tool methods
    kwargs = {k: v for k, v in inputs.items() if k != 'operation'}

    # Initialize result dict and default reflection
    result = {"libs_available": MESA_AVAILABLE, "error": None}
    reflection_status = "Failure"; reflection_summary = f"ABM op '{operation}' init failed."; reflection_confidence = 0.0; reflection_alignment = "N/A"; reflection_issues = ["Initialization error."]; reflection_preview = None

    if not operation:
        result["error"] = "Missing 'operation' input for perform_abm."
        reflection_issues = [result["error"]]
        reflection_summary = "Input validation failed: Missing operation."
        return {**result, "reflection": _create_reflection(reflection_status, reflection_summary, reflection_confidence, reflection_alignment, reflection_issues, reflection_preview)}

    try:
        tool = ABMTool() # Instantiate the tool
        op_result: Dict[str, Any] = {} # Store result from the specific tool method

        # --- Dispatch to appropriate tool method ---
        if operation == "create_model":
            op_result = tool.create_model(**kwargs)
        elif operation == "run_simulation":
            model_input = kwargs.get('model')
            created_model_internally = False
            if model_input is None:
                # Attempt to create model implicitly
                logger.info(f"No pre-existing model provided for run_simulation. Attempting to create one with type: {kwargs.get('model_type', 'N/A')}")
                # Prepare kwargs for model creation from the general kwargs
                # Keys for create_model: model_type, agent_class, width, height, density, model_params, agent_params, seed, scheduler, torus
                creation_args = {
                    k: v for k, v in kwargs.items() 
                    if k in ['model_type', 'agent_class', 'width', 'height', 'density', 'model_params', 'agent_params', 'seed', 'scheduler', 'torus']
                }
                # model_type is essential for create_model, ensure it's present or default
                if 'model_type' not in creation_args and 'model_type' in kwargs: # Ensure model_type from original inputs is used
                    creation_args['model_type'] = kwargs['model_type']
                elif 'model_type' not in creation_args: # Default if not specified anywhere
                     creation_args['model_type'] = 'basic' # or some other sensible default

                create_result = tool.create_model(**creation_args)
                model_input = create_result.get('model') # Get the model instance
                
                if create_result.get("error") or not model_input:
                    op_result = create_result # Propagate error from creation
                    op_result["error"] = op_result.get("error", "Implicit model creation failed.")
                    # Ensure a reflection is present if create_model failed to provide one (should not happen with IAR)
                    if "reflection" not in op_result:
                         op_result["reflection"] = _create_reflection("Failure", op_result["error"], 0.0, "N/A", [op_result["error"]], None)
                else:
                    logger.info(f"Implicitly created model (Run ID: {getattr(model_input, 'run_id', 'N/A')}) for simulation.")
                    created_model_internally = True # Flag that model was created here
            
            if model_input and not op_result.get("error"): # If model exists (either passed or created) and no prior error
                # Prepare kwargs for run_simulation
                # Keys for run_simulation: model, steps, visualize
                run_args = {'model': model_input}
                if 'steps' in kwargs: run_args['steps'] = kwargs['steps']
                if 'visualize' in kwargs: run_args['visualize'] = kwargs['visualize']
                
                op_result = tool.run_simulation(**run_args)
                if created_model_internally and op_result.get("model_run_id") is None and hasattr(model_input, "run_id"):
                    # Ensure the run_id from the internally created model is in the output if run_simulation didn't set one
                    op_result["model_run_id"] = model_input.run_id
            elif not model_input and not op_result.get("error"): # Should be caught by create_result.get("error") check
                 op_result = {"error": "Missing 'model' input for run_simulation and implicit creation failed silently."}


        elif operation == "analyze_results":
            results_input = kwargs.get('results')
            if results_input is None: op_result = {"error": "Missing 'results' input for analyze_results."}
            else: op_result = tool.analyze_results(**kwargs) # Pass all kwargs including results
        elif operation == "convert_to_state":
            abm_result_input = kwargs.get('abm_result') 
            if abm_result_input is None: op_result = {"error": "Missing 'abm_result' input for convert_to_state."}
            else: op_result = tool.convert_to_state_vector(**kwargs) 
        elif operation == "generate_visualization":
            # This operation expects the full result dictionary from a 'run_simulation' operation
            # as input, plus an 'output_filename'
            simulation_results_input = kwargs.get('simulation_results')
            output_filename = kwargs.get('output_filename')

            if simulation_results_input is None or not isinstance(simulation_results_input, dict):
                op_result = {"error": "Missing or invalid 'simulation_results' dictionary input for generate_visualization."}
            elif output_filename is None or not isinstance(output_filename, str):
                op_result = {"error": "Missing or invalid 'output_filename' string input for generate_visualization."}
            else:
                # The _generate_visualization method needs: model (or its name/ID for filename), 
                # final_step_count, results_dict (which is simulation_results_input), 
                # model_df (optional), agent_df (optional)
                # We may not have the live model object here, or dataframes, if just passing results around.
                # Let's adapt _generate_visualization or how we call it.
                # For now, assume _generate_visualization can work with what's in simulation_results_input.
                
                # Simplification: _generate_visualization needs a model-like object for name, and results_dict.
                # We will pass a simple object for model_name_part and the results dict.
                class MinimalModelInfo:
                    def __init__(self, name, run_id):
                        self.__class__ = type(name, (object,), {})
                        self.run_id = run_id

                model_run_id_for_viz = simulation_results_input.get('model_run_id', 'sim_viz')
                model_name_for_viz = simulation_results_input.get('type', 'UnknownModel') # type from create_model
                if not model_name_for_viz and simulation_results_input.get('model') and isinstance(simulation_results_input.get('model'), dict):
                    model_name_for_viz = simulation_results_input.get('model',{}).get('type', 'UnknownModel') # from create_model if model is dict
                
                minimal_model = MinimalModelInfo(name=model_name_for_viz, run_id=model_run_id_for_viz)
                final_steps = simulation_results_input.get('simulation_steps_run', 0)
                
                # _generate_visualization expects model_df and agent_df. If not present in simulation_results, pass None.
                # This might happen if these were not collected or if only a subset of results are passed.
                model_df_input = None
                if 'model_data' in simulation_results_input and isinstance(simulation_results_input['model_data'], list):
                    try: model_df_input = pd.DataFrame(simulation_results_input['model_data']).set_index('Step')
                    except: model_df_input = None # Silently handle if conversion fails
                
                # agent_df is not typically part of run_simulation output directly, only agent_data_last_step
                # so it will be None here.

                viz_path = tool._generate_visualization(
                    model=minimal_model, # Pass the minimal info object
                    final_step_count=final_steps,
                    results_dict=simulation_results_input, # This contains final_state_grid, etc.
                    model_df=model_df_input, 
                    agent_df=None # Agent DataFrame for all steps not usually passed, only last step data
                )
                if viz_path:
                    op_result = {"visualization_path": viz_path, "error": None}
                else:
                    op_result = {"error": "Visualization generation failed (see logs).", "visualization_path": None}

                # This operation must also return a full IAR reflection
                vis_status = "Success" if op_result.get("visualization_path") else "Failure"
                vis_summary = f"Visualization generated at {op_result.get('visualization_path')}" if vis_status == "Success" else op_result.get("error", "Visualization failed")
                vis_confidence = 0.9 if vis_status == "Success" else 0.2
                vis_issues = [op_result["error"]] if op_result.get("error") else None
                op_result["reflection"] = _create_reflection(vis_status, vis_summary, vis_confidence, "Aligned with visualizing results.", vis_issues, op_result.get("visualization_path"))

        else:
            op_result = {"error": f"Unknown ABM operation specified: {operation}"}

        # --- Process Result and Extract Reflection ---
        # Merge the operation's result dictionary into the main result
        result.update(op_result)
        # Extract the reflection dictionary generated by the tool method (it should always exist)
        internal_reflection = result.pop("reflection", None) if isinstance(result, dict) else None

        # If reflection is missing (indicates error in tool method), create a default one
        if internal_reflection is None:
            logger.error(f"Internal reflection missing from ABM operation '{operation}' result! This indicates a protocol violation in the tool implementation.")
            internal_reflection = _create_reflection("Failure", "Internal reflection missing from tool.", 0.0, "N/A", ["Tool implementation error: Missing IAR."], op_result)
            result["error"] = result.get("error", "Internal reflection missing.") # Ensure error is noted

        # --- Final Return ---
        # The final result includes primary output keys and the 'reflection' dictionary
        result["reflection"] = internal_reflection
        return result

    except Exception as e_wrapper:
        # Catch unexpected errors in the wrapper/dispatch logic
        logger.error(f"Critical error in perform_abm wrapper for operation '{operation}': {e_wrapper}", exc_info=True)
        result["error"] = str(e_wrapper)
        reflection_issues = [f"Critical failure in ABM wrapper: {e_wrapper}"]
        result["reflection"] = _create_reflection("Failure", f"Critical failure in wrapper: {e_wrapper}", 0.0, "N/A", reflection_issues, None)
        return result

# --- END OF FILE Three_PointO_ArchE/agent_based_modeling_tool.py --- 