import copy

from mesa import Agent, Model
from mesa.time import RandomActivation

from enums import Directions


class CarAgent(Agent):

    def __init__(self, unique_id, model, car_data, city_map, key):
        print(car_data)
        super().__init__(unique_id, model)
        self.pos = car_data["start"]
        self.destination = car_data["destination"]
        self.route = []
        self.passengers = []
        self.pickups = []
        self.waypoints = []
        self.potential_passenger = None
        self.capacity = 5
        self.city_map = city_map
        self.key = key

    def find_nearest_passenger(self):
        """
        Find the nearest passenger by using a BFS.
        :return:
        """
        potential_passenger, potential_route = None, []
        q = [(self.pos, [])]
        while q:
            curr_tile, curr_route = q.pop(0)
            adjacent_passenger = self.city_map.single.get_adjacent_passenger(curr_tile)
            if adjacent_passenger:
                potential_passenger, potential_route = adjacent_passenger, curr_route
                break

            possible_directions = self.city_map.single.get_possible_directions(curr_tile)
            for direction in possible_directions:
                displacement = Directions[direction].value
                next_row = curr_tile[0] + displacement[0]
                next_col = curr_tile[1] + displacement[1]
                next_pos = (next_row, next_col)
                next_route = copy.copy(curr_route)
                next_route.append(direction)
                q.append((next_pos, next_route))

        return potential_passenger, potential_route

    def step(self):
        passenger, route = self.find_nearest_passenger()
        print(f"\nI am car {self.key}, my position is {self.pos}")
        print(f"In this turn, I will go for passenger {passenger.key if passenger else 'None'}")
        print(f"The route is {route}\n")

    def drive_unit(self):
        return True

    def can_drop_passenger(self):
        pass


class CarModel(Model):

    def __init__(self, cars_data):
        super().__init__()
        self.car_map = {}
        self.schedule = RandomActivation(self)
        self.cars_data = cars_data
        self.city_map = None

    def make_agents(self):
        i = 0
        print("\nInitializing Cars")
        for key, data in self.cars_data.items():
            print(f"Key: {key}")
            a = CarAgent(i, self, data, self.city_map, key)
            self.schedule.add(a)
            self.car_map[key] = a
            i += 1

    def step(self):
        self.schedule.step()
