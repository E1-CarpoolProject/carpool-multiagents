from mesa import Agent, Model
from mesa.time import RandomActivation
import numpy as np

positions = [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3]]


class CarAgent(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        a = np.random.randint(len(positions))
        while True:
            b = np.random.randint(len(positions))
            if a != b:
                break
        self.x_pos = positions[a][0]
        self.y_pos = positions[a][1]
        self.y_destination = positions[b][1]
        self.x_destination = positions[b][0]
        self.x_next_stop = 0
        self.y_next_stop = 0
        self.occupancy = 1
        self.capacity = 5
        # REVISAR
        self.passengers = []

    def step(self):
        # The agent's step will go here.
        print ("Car " + str(self.unique_id) +".")

    def drive_unit(self):
        return True

    def update_route(self):
        return True

    def arrive_at_destination(self):
        return self.x_pos == self.x_destination and self.y_pos == self.y_destination

    def pick_up(self):
        if self.occupancy < self.capacity:
            self.occupancy += 1
            return True
        else:
            print("El coche está lleno :(")
            return False

class CarModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = CarAgent(i, self)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
