from mesa import Agent, Model
from mesa.time import RandomActivation
import numpy as np

positions = [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3]]


class PassengerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        #posiciones de origen y destino random
        a = np.random.randint(len(positions))
        while True:
            b = np.random.randint(len(positions))
            if a != b:
                break
        self.x_pos = positions[a][0]
        self.y_pos = positions[a][1]
        self.y_destination = positions[b][1]
        self.x_destination = positions[b][0]
        self.is_traveling = False
        self.has_arrived = False

    def imprimirPos(self):
        if self.is_traveling:
            print("estoy viajando")
        elif self.has_arrived:
            print("ya llegue")
        else:
            print("estoy esperando ride")
    def needs_ride(self):
        return not self.is_traveling or not self.has_arrived

    def arrived_destination(self):
        return self.has_arrived

    def step(self):
        # The agent's step will go here.
        print ("pasajero número " + str(self.unique_id))
        print( "Mi posicion de origen es: "+str(self.x_pos)+", "+ str(self.y_pos)+ ". ")
        print( "Mi posicion de destino es: "+str(self.x_destination)+", "+ str(self.y_destination)+ ". ")
        self.imprimirPos()

class PassengerModel(Model):
    """A model with some number of agents."""
    def __init__(self, N):
        self.num_agents = N
        self.schedule = RandomActivation(self)
        # Create agents
        for i in range(self.num_agents):
            a = PassengerAgent(i, self)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()