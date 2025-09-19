import logging
import time
import random
import re
from typing import Dict, Any, List, Optional

# --- Optional Imports for Mesa ---
try:
    import mesa
    MESA_AVAILABLE = True
except ImportError:
    MESA_AVAILABLE = False
    # Create dummy classes for type hinting and structure
    class MesaAgent:
        def __init__(self, unique_id, model): pass
        def step(self): pass
    class MesaModel:
        def __init__(self): self.running = True
        def step(self): pass
    mesa = type("MesaModuleMock", (), {"Agent": MesaAgent, "Model": MesaModel})()

logger = logging.getLogger(__name__)

# --- Core DSL Engine Components ---

class DSLAgent(mesa.Agent):
    """A dynamically configured agent based on the DSL schema."""
    def __init__(self, unique_id, model, name, attrs, behaviour):
        super().__init__(unique_id, model)
        self.name = name
        self.attrs = attrs
        self._behaviour = behaviour

    def step(self):
        """Executes the agent's behavior for one time step."""
        for instr in self._behaviour:
            # This is a simple parser for behavior primitives
            match = re.match(r"(\w+)\((.*)\)", instr)
            if match:
                func_name, args_str = match.groups()
                args = [a.strip() for a in args_str.split(',')]
                
                # Simplified behavior execution
                if func_name == "MoveRandom" and hasattr(self.model.grid, 'move_agent'):
                    self.model.grid.move_agent(self, self.random.choice(self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)))
                elif func_name == "FirstOrderDecay":
                    attr, t_half = args[0], float(args[1])
                    if self.attrs.get(attr, 0) > 0:
                        self.attrs[attr] *= (0.5 ** (1 / t_half))

class DSLModel(mesa.Model):
    """A dynamically created Mesa model from a DSL schema."""
    def __init__(self, schema):
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        world_cfg = schema["world"]
        self.grid = mesa.space.MultiGrid(world_cfg["width"], world_cfg["height"], world_cfg["torus"])
        
        for agent_cfg in schema["agents"]:
            for i in range(agent_cfg["count"]):
                agent = DSLAgent(self.next_id(), self, agent_cfg["name"], agent_cfg["attrs"].copy(), agent_cfg["behaviour"])
                self.schedule.add(agent)
                x, y = self.random.randrange(self.grid.width), self.random.randrange(self.grid.height)
                self.grid.place_agent(agent, (x, y))

    def step(self):
        self.schedule.step()

# --- Main Tool Function ---

def _create_reflection(status: str, message: str, **kwargs) -> Dict[str, Any]:
    """Creates a standardized IAR reflection dictionary."""
    reflection = {"status": status, "message": message}
    reflection.update(kwargs)
    return reflection

def create_model_from_schema(schema: Dict[str, Any]) -> Optional[DSLModel]:
    """Parses the DSL schema and creates a Mesa model instance."""
    if not MESA_AVAILABLE:
        logger.warning("Mesa library not available. Model creation is simulated.")
        return None
    return DSLModel(schema)

def run_simulation(model: Optional[DSLModel], steps: int) -> Dict[str, Any]:
    """Runs the simulation for a given number of steps."""
    if not model or not MESA_AVAILABLE:
        return {"log": "Simulated run: Model executed for 100 steps.", "final_agent_count": 5}

    for i in range(steps):
        model.step()
    
    return {
        "log": f"Real run: Model executed for {steps} steps.",
        "final_agent_count": model.schedule.get_agent_count()
    }

def perform_abm(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for all Agent-Based Modeling operations."""
    start_time = time.time()
    operation = inputs.get("operation")
    
    try:
        if operation == "create_and_run":
            schema = inputs["schema"]
            steps = inputs.get("steps", 100)
            
            model = create_model_from_schema(schema)
            sim_results = run_simulation(model, steps)
            
            simulated = not MESA_AVAILABLE
            message = "ABM simulation completed."
            if simulated:
                message += " (Run was simulated due to missing Mesa library)."

            return {
                "result": sim_results,
                "reflection": _create_reflection(
                    "success", message, 
                    confidence=0.5 if simulated else 0.9,
                    execution_time=time.time() - start_time
                )
            }
        else:
            raise ValueError(f"Unsupported ABM operation: {operation}")

    except Exception as e:
        logger.error(f"ABM tool failed on operation '{operation}': {e}", exc_info=True)
        return {
            "error": str(e),
            "reflection": _create_reflection(
                "failure", str(e), execution_time=time.time() - start_time
            )
        }
