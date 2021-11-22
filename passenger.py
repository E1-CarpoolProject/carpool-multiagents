from mesa import Agent, Model
from mesa.time import RandomActivation


class PassengerAgent(Agent):

    def __init__(self, unique_id, model, passenger_data, passenger_key):
        print(passenger_data)
        super().__init__(unique_id, model)
        self.pos = passenger_data["start"]
        self.destination = passenger_data["destination"]
        self.is_traveling = False
        self.has_arrived = False
        self.is_waiting = False
        self.key = passenger_key

    def needs_ride(self):
        return not (self.is_traveling or self.has_arrived or self.is_waiting)

    def set_aside(self):
        self.is_waiting = True

    def step(self):
        pass


class PassengerModel(Model):

    def __init__(self, passenger_data):
        print("\nInitializing Passengers")
        super().__init__()
        self.passenger_map = {}
        i = 0
        self.schedule = RandomActivation(self)
        for key, data in passenger_data.items():
            print(f"Key: {key}")
            a = PassengerAgent(i, self, data, key)
            self.schedule.add(a)
            self.passenger_map[key] = a
            i += 1
        print()

    def step(self):
        self.schedule.step()