import numpy as np, uuid, logging
from typing import Type
from .agent_based_modeling_tool import MESA_AVAILABLE

if MESA_AVAILABLE:
    from mesa import Model, Agent
    from mesa.space import MultiGrid
    from mesa.datacollection import DataCollector
    from mesa.time import SimultaneousActivation
else:
    Model = object; Agent = object; MultiGrid = object; DataCollector = object; RandomActivation = None
    logging.getLogger(__name__).warning("Mesa not available – combat ABM will only work when Mesa is installed.")

logger = logging.getLogger(__name__)

class GorillaAgent(Agent):
    """A gorilla agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health = 1500
        self.attack_power = 100
        self.damage_to_deal = 0

    def step(self):
        # Phase 1: Decide who to attack and how much damage to deal
        self.damage_to_deal = 0
        humans = self.model.get_agents_by_type(HumanAgent)
        if humans:
            target = self.random.choice(humans)
            self.damage_to_deal = self.attack_power

    def advance(self):
        # Phase 2: Deal the damage
        humans = self.model.get_agents_by_type(HumanAgent)
        if humans:
            target = self.random.choice(humans) # Re-finding target for simplicity
            target.health -= self.damage_to_deal

class HumanAgent(Agent):
    """A human agent."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.health = 100
        self.attack_power = 4
        self.alive = True
        self.damage_to_deal = 0

    def step(self):
        # Phase 1: All living humans contribute to damaging the gorilla
        self.damage_to_deal = 0
        if self.alive:
            self.damage_to_deal = self.attack_power

    def advance(self):
        # Phase 2: Damage is applied to the gorilla
        if self.model.gorilla:
            self.model.gorilla.health -= self.damage_to_deal
        if self.health <= 0:
            self.alive = False


class GorillaCombatModel(Model):
    """A model for the gorilla vs. humans combat scenario."""
    def __init__(self, width, height, num_humans, seed=None):
        super().__init__(seed=seed)
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)
        self.running = True
        
        self.gorilla = GorillaAgent("gorilla", self)
        self.grid.place_agent(self.gorilla, (width // 2, height // 2))
        self.schedule.add(self.gorilla)

        self.humans = []
        for i in range(num_humans):
            human = HumanAgent(f"human_{i}", self)
            self.humans.append(human)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(human, (x, y))
            self.schedule.add(human)

        self.datacollector = DataCollector(
            model_reporters={"GorillaHealth": lambda m: m.gorilla.health,
                             "AliveHumans": lambda m: sum(1 for h in m.humans if h.alive)}
        )

    def get_agents_by_type(self, agent_type):
        return [agent for agent in self.schedule.agents if isinstance(agent, agent_type) and getattr(agent, 'alive', True)]

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

        alive_humans = sum(1 for h in self.humans if h.alive)
        if self.gorilla.health <= 0 or alive_humans == 0:
            self.running = False 