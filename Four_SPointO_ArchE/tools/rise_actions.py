from mesa.datacollection import DataCollector

class BasicAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(model)
        self.unique_id = unique_id
        self.state = self.random.randint(0, 1)

    def step(self):
        pass
