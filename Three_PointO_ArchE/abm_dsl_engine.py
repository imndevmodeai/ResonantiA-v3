"""abm_dsl_engine.py
Provides a minimal runtime compiler that converts a high-level JSON DSL
schema into a runnable Mesa model.  The goal is not to implement a full
behaviour-language but to supply enough scaffolding so that ArchE can treat
`model_type: "generic_dsl"` as a valid target for the ABM tool.

Schema (example):
{
  "world": {"type": "grid", "width": 20, "height": 20, "torus": false},
  "agents": [
      {"name": "Drone", "count": 5,
       "attrs": {"battery": 100},
       "behaviour": ["MoveRandom"]}
  ],
  "victory_condition": "all Drone.battery == 0"
}

Only two behaviour primitives are recognised for now:
 • "MoveRandom"  – agent moves to an empty Moore neighbour.
 • "MoveTowards(<Tag>)" – moves one step towards the closest agent of Tag.

Anything else is ignored (no-op).  The engine purposefully keeps the
implementation tiny; users can extend by adding new primitives.
"""

from __future__ import annotations

import uuid, logging, re, random
from typing import Dict, Any, List

# Re-use Mesa import check from the ABM tool
from .agent_based_modeling_tool import MESA_AVAILABLE

if MESA_AVAILABLE:
    from mesa import Model, Agent
    from mesa.space import MultiGrid
    from mesa.datacollection import DataCollector
else:
    # Dummy fall-backs so that type hints still work if Mesa missing
    Model = object  # type: ignore
    Agent = object  # type: ignore
    MultiGrid = object  # type: ignore
    DataCollector = object  # type: ignore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper – limited behaviour parser
# ---------------------------------------------------------------------------
_move_towards_re = re.compile(r"MoveTowards\((?P<tag>[^)]+)\)")

class DSLAgent(Agent):
    """Generic agent whose behaviour is driven by a list of behaviour strings."""
    def __init__(self, unique_id, model: "DSLModel", attrs: Dict[str, Any], behaviour: List[str]):
        super().__init__(model)
        self.unique_id = unique_id
        self.attrs = attrs.copy()  # shallow copy
        self._behaviour = behaviour or []

    # ---------------------------------------------------------------------
    # Behaviour helpers
    # ---------------------------------------------------------------------
    def _move_random(self):
        """Move to a random empty neighbouring cell (Moore neighbourhood)."""
        neighbours = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        random.shuffle(neighbours)
        for pos in neighbours:
            if self.model.grid.is_cell_empty(pos):
                self.model.grid.move_agent(self, pos)
                break

    def _move_towards(self, target_tag: str):
        candidates = [a for a in self.model.agents_by_tag.get(target_tag, []) if a is not self]
        if not candidates:
            self._move_random()
            return
        # choose nearest Manhattan distance
        tx, ty = None, None
        min_dist = None
        for tgt in candidates:
            if not hasattr(tgt, "pos") or tgt.pos is None:
                continue
            dist = abs(tgt.pos[0] - self.pos[0]) + abs(tgt.pos[1] - self.pos[1])
            if min_dist is None or dist < min_dist:
                min_dist = dist
                tx, ty = tgt.pos
        if tx is None:
            self._move_random()
            return
        x, y = self.pos
        dx = (tx - x)
        dy = (ty - y)
        step_x = x + (1 if dx > 0 else -1 if dx < 0 else 0)
        step_y = y + (1 if dy > 0 else -1 if dy < 0 else 0)
        new_pos = (step_x, step_y)
        if self.model.grid.is_cell_empty(new_pos):
            self.model.grid.move_agent(self, new_pos)
        else:
            self._move_random()

    # ---------------------------------------------------------------------
    # Standard Mesa API
    # ---------------------------------------------------------------------
    def step(self):
        if not MESA_AVAILABLE:
            return

        # --- Handle pH shifts first ---
        self.attrs['pH'] = 7.0
        h = self.model.hours_from_test()
        
        for instr in self._behaviour:
            if instr.startswith("pHShift"):
                m = re.match(r"pHShift\(([+-]?[0-9.]+),\s*window=\[\s*(-?[0-9.]+),\s*(-?[0-9.]+)\s*\]", instr)
                if m:
                    delta, start_hr, end_hr = float(m.group(1)), float(m.group(2)), float(m.group(3))
                    if start_hr <= h <= end_hr:
                        self.attrs['pH'] += delta

        # --- Process all other behaviours ---
        for instr in self._behaviour:
            if instr.startswith("pHShift"):
                continue

            if instr == "MoveRandom":
                self._move_random()
            else:
                m = _move_towards_re.fullmatch(instr)
                if m:
                    self._move_towards(m.group("tag"))
            # PK primitives ------------------------------------------------
            if instr.startswith("FirstOrderDecay"):
                m = re.match(r"FirstOrderDecay\((\w+),\s*t_half\s*=\s*(\d+)\)", instr)
                if m:
                    field, t_half = m.group(1), float(m.group(2))
                    if field in self.attrs and t_half > 0:
                        decay_factor = 0.5 ** (self.model.step_hours / t_half)
                        self.attrs[field] *= decay_factor
            elif instr.startswith("FirstOrderDecaypH"):
                m = re.match(r"FirstOrderDecaypH\((\w+),\s*t_half_ref=([\d.]+),\s*sensitivity=([\d.]+),\s*ref_pH=([\d.]+)\)", instr)
                if m:
                    field, t_half_ref, sensitivity, ref_pH = m.groups()
                    t_half_ref, sensitivity, ref_pH = float(t_half_ref), float(sensitivity), float(ref_pH)
                    current_pH = self.attrs.get("pH", ref_pH)
                    
                    import math
                    t_half_eff = t_half_ref * math.exp(sensitivity * (current_pH - ref_pH))
                    
                    if field in self.attrs and t_half_eff > 0:
                        decay_factor = 0.5 ** (self.model.step_hours / t_half_eff)
                        self.attrs[field] *= decay_factor
            elif instr.startswith("Metabolise"):
                m = re.match(r"Metabolise\((\w+),\s*(\w+),\s*([0-9.]+)\)", instr)
                if m:
                    src, dst, frac = m.group(1), m.group(2), float(m.group(3))
                    if src in self.attrs:
                        converted = self.attrs[src] * frac * 0.01
                        self.attrs[src] -= converted
                        self.attrs[dst] = self.attrs.get(dst, 0) + converted
            elif instr.startswith("ScheduleDose"):
                m = re.match(r"ScheduleDose\((\w+),\s*([0-9.]+),\s*at_hour\s*=\s*(-?[0-9.]+)\)", instr)
                if m:
                    field, amt, at_hr = m.group(1), float(m.group(2)), float(m.group(3))
                    if not hasattr(self, "_dose_history"):
                        self._dose_history = set()
                    key = (field, at_hr)
                    if key not in self._dose_history and abs(self.model.hours_from_test() - at_hr) < 1e-6:
                        self.attrs[field] = self.attrs.get(field, 0) + amt
                        self._dose_history.add(key)

class DSLModel(Model):
    def __init__(self, schema: Dict[str, Any], seed: int | None = None):
        super().__init__(seed=seed)
        self.run_id = uuid.uuid4().hex[:8]
        self.schema = schema

        world = schema.get("world", {})
        width = world.get("width", 20)
        height = world.get("height", 20)
        torus = bool(world.get("torus", False))
        # Even for non-spatial PK sims we still instantiate a tiny grid so that
        # the surrounding ABM tooling (which expects a grid attribute) keeps working.
        self.grid = MultiGrid(max(1, width), max(1, height), torus=torus)

        # Time axis helpers -------------------------------------------------
        self.step_hours = world.get("step_hours", 1)
        self.total_hours = world.get("hours", 24)
        self.total_steps = int(self.total_hours / self.step_hours)
        self._current_step = 0

        self.agents_by_tag: Dict[str, List[DSLAgent]] = {}
        self._create_agents()
        # Store total agents count for downstream reporting
        self.num_agents = len(self.agents)

        # minimal datacollector: counts per step
        self.datacollector = DataCollector({
            "Step": lambda m: m.schedule.steps if hasattr(m, "schedule") else 0,
            "AgentCount": lambda m: len(m.agents),
        })

        self.running = True

    # ------------------------------------------------------------------
    def _create_agents(self):
        for agent_def in self.schema.get("agents", []):
            tag = agent_def.get("name", "Agent")
            count = int(agent_def.get("count", 1))
            attrs = agent_def.get("attrs", {})
            behaviour = agent_def.get("behaviour", [])
            self.agents_by_tag.setdefault(tag, [])
            for i in range(count):
                a = DSLAgent(f"{tag}_{i}", self, attrs, behaviour)
                # place randomly
                while True:
                    pos = (self.random.randrange(self.grid.width), self.random.randrange(self.grid.height))
                    if self.grid.is_cell_empty(pos):
                        self.grid.place_agent(a, pos)
                        break
                self.agents_by_tag[tag].append(a)

    # ------------------------------------------------------------------
    def step(self):
        # Track progress for pharmacokinetic primitives
        self._current_step += 1
        # Iterate over a copy because agents may move within grid internals
        for agent in list(self.agents):
            agent.step()
        # datacollect
        self.datacollector.collect(self)
        # Stopping condition (optional)
        victory = self.schema.get("victory_condition")
        if victory is not None:
            # Very naive evaluation; DO NOT use eval on untrusted input in prod.
            try:
                # Expose tag groups as variables for simple conditions
                local_vars = {tag: group for tag, group in self.agents_by_tag.items()}
                if eval(victory, {}, local_vars):
                    self.running = False
            except Exception as e:
                logger.warning(f"Error evaluating victory condition '{victory}': {e}")

        # Snapshot concentrations from first Body agent (if any) for convenience
        body_list = self.agents_by_tag.get("Body")
        if body_list:
            self.last_body_attrs = body_list[0].attrs.copy()

    # ------------------------------------------------------------------
    def hours_from_test(self) -> float:
        """Return negative hours until test (0 == test time) using current step index."""
        remaining_steps = self.total_steps - self._current_step
        return -remaining_steps * self.step_hours

# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def create_model_from_schema(schema: Dict[str, Any], seed: int | None = None):
    """Return a Mesa Model generated from the provided DSL schema."""
    if not MESA_AVAILABLE:
        raise RuntimeError("Mesa library not available – cannot create DSL model.")
    if not isinstance(schema, dict):
        raise ValueError("Schema must be a dict.")
    model = DSLModel(schema, seed=seed)
    return model 