from edge import Edge
from intersection import IntersectionModel

from mesa import Agent, Model
from mesa.time import RandomActivation, BaseScheduler


class RouterAgent(Agent):

    def __init__(self, unique_id: int, model: Model, environment_data):
        super().__init__(unique_id, model)

        intersections_data = environment_data["intersections_data"]
        model = IntersectionModel(intersections_data)
        self.nodes = model.schedule.agents
        self.intersection_model = model

        self.edges = []
        for _ in range(len(self.nodes)):
            self.edges.append([0] * len(self.nodes))

        roads_data = environment_data["roads_data"]
        for road in roads_data:
            edge = Edge(length=1, direction=road["direction"])
            source, destination = road["source"], road["destination"]
            self.edges[source][destination] = edge

        print(self.edges)

    def step(self):
        self.intersection_model.step()


class RouterModel(Model):
    """A model with some number of agents."""

    def __init__(self, environmental_data):
        super().__init__()
        self.schedule = BaseScheduler(self)
        a = RouterAgent(unique_id=0, model=self, environment_data=environmental_data)
        self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()



