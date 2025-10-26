import numpy as np, uuid, logging
from typing import Type
from .agent_based_modeling_tool import MESA_AVAILABLE

if MESA_AVAILABLE:
    from mesa import Model, Agent
    from mesa.space import MultiGrid
    from mesa.datacollection import DataCollector
else:
    Model = object; Agent = object; MultiGrid = object; DataCollector = object; RandomActivation = None
    logging.getLogger(__name__).warning("Mesa not available – combat ABM will only work when Mesa is installed.")

logger = logging.getLogger(__name__)

class GorillaAgent(Agent):
    def __init__(self, unique_id, model, health: int = 100):
        super().__init__(model)
        self.unique_id = unique_id
        self.health = health

    def step(self):
        # If no humans alive model ends elsewhere
        if self.health <= 0:
            return
        # find adjacent humans and attack one
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        humans = [a for a in neighbors if isinstance(a, HumanVillagerAgent) and a.alive]
        if humans:
            victim = self.random.choice(humans)
            victim.take_damage(1.0)  # lethal single hit
        else:
            # move toward nearest human if any exist
            human_positions = [(agent, agent.pos) for agent in self.model.humans if agent.alive]
            if human_positions:
                # find nearest by Manhattan distance
                nearest, pos = min(human_positions, key=lambda hp: abs(hp[1][0]-self.pos[0]) + abs(hp[1][1]-self.pos[1]))
                self.move_towards(pos)

    def move_towards(self, target_pos):
        x, y = self.pos
        tx, ty = target_pos
        dx = np.sign(tx - x)
        dy = np.sign(ty - y)
        new_pos = (int(x + dx), int(y + dy))
        if self.model.grid.is_cell_empty(new_pos):
            self.model.grid.move_agent(self, new_pos)

class HumanVillagerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.alive = True

    def take_damage(self, dmg: float):
        self.alive = False  # one hit kill for simplicity

    def step(self):
        if not self.alive:
            return
        # move randomly towards gorilla if not adjacent
        gorilla = self.model.gorilla
        gx, gy = gorilla.pos
        x, y = self.pos
        dist = abs(gx - x) + abs(gy - y)
        if dist == 1:
            # adjacent – engage
            self.model.humans_engaging.add(self)
        else:
            dx = np.sign(gx - x)
            dy = np.sign(gy - y)
            candidate_positions = [(x+dx, y), (x, y+dy), (x+dx, y+dy)]
            self.random.shuffle(candidate_positions)
            for new_pos in candidate_positions:
                if self.model.grid.out_of_bounds(new_pos):
                    continue
                if self.model.grid.is_cell_empty(new_pos):
                    self.model.grid.move_agent(self, new_pos)
                    break

class GorillaCombatModel(Model):
    def __init__(self, width: int, height: int, num_humans: int, seed: int = None):
        super().__init__(seed=seed)
        self.run_id = uuid.uuid4().hex[:8]
        self.grid = MultiGrid(width, height, torus=False)
        self._step = 0  # manual step counter
        # create gorilla in center
        gx, gy = width // 2, height // 2
        self.gorilla = GorillaAgent("gorilla", self)
        self.grid.place_agent(self.gorilla, (gx, gy))
        # create human agents randomly around
        self.humans = []
        for i in range(num_humans):
            agent = HumanVillagerAgent(i, self)
            placed = False
            while not placed:
                pos = (self.random.randrange(width), self.random.randrange(height))
                if self.grid.is_cell_empty(pos):
                    self.grid.place_agent(agent, pos)
                    placed = True
            self.humans.append(agent)
        self.humans_engaging = set()
        self.datacollector = DataCollector({
            "Step": lambda m: m._step,
            "AliveHumans": lambda m: sum(1 for h in m.humans if h.alive),
            "GorillaHealth": lambda m: m.gorilla.health
        })

    def step(self):
        # Clear engagement set
        self.humans_engaging = set()
        # Advance humans then gorilla
        for h in list(self.humans):
            h.step()
        self.gorilla.step()
        # After all moves, resolve group grapple damage
        k = len(self.humans_engaging)
        if k >= 4:  # need at least 4 to inflict damage
            dmg = k * 2  # linear synergy
            self.gorilla.health -= dmg
        # Remove dead humans from grid
        for h in self.humans:
            if not h.alive and h.pos is not None:
                self.grid.remove_agent(h)
                h.pos = None
        # Increment step counter and collect data
        self._step += 1
        self.datacollector.collect(self)
        # Check termination
        if self.gorilla.health <= 0 or all(not h.alive for h in self.humans):
            self.running = False

    # Helper methods so ABMTool can query counts
    def count_active_agents(self):
        return sum(1 for h in self.humans if h.alive)

    def count_inactive_agents(self):
        return len(self.humans) - self.count_active_agents() 