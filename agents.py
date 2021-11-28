from __future__ import annotations
from copy import copy

from mesa import Agent, Model

from enums import Directions, LightStatus

# from model import CarpoolModel

INTERSECTION_LENGTH = 50
TICKS_TO_CHANGE = 5


class Car(Agent):

    capacity = 5

    def __init__(self, unique_id, model: CarpoolModel, start, destination):
        super().__init__(unique_id, model)
        self.pos = start
        self.destination = destination
        self.direction = self.model.grid.get_cell_list_contents([self.pos])[0].direction
        self.route = []
        self.passengers = []
        self.drops = []
        self.pickup = None
        self.objective = None

        self.model.grid.place_agent(self, self.pos)

    def find_nearest_passenger(self):
        """
        Find the nearest passenger by using a BFS.
        :return:
        """
        potential_passenger, potential_route = None, []
        q = [(self.pos, [])]
        while q:
            curr_tile, curr_route = q.pop(0)

            adjacent_passenger = self.get_adjacent_passenger(curr_tile)
            if adjacent_passenger:
                potential_passenger, potential_route = adjacent_passenger, curr_route
                break

            possible_directions = self.get_possible_directions(curr_tile)
            for direction in possible_directions:
                displacement = Directions[direction].value
                next_row = curr_tile[0] + displacement[0]
                next_col = curr_tile[1] + displacement[1]
                next_pos = (next_row, next_col)
                next_route = copy(curr_route)
                next_route.append(direction)
                q.append((next_pos, next_route))

        return potential_passenger, potential_route

    def get_possible_directions(self, coords) -> list:
        """
        Obtain the possible directions that a car can go to
        :return: List of directions
        """
        directions = []
        cell = self.model.grid.get_cell_list_contents([coords])
        road = [road for road in cell if isinstance(road, Road)]
        intersection = [intersec for intersec in cell if isinstance(intersec, Intersection)]

        if road:
            directions.append(road[0].direction)

        elif intersection:
            print(intersection[0].directions_to_go)
            directions += intersection[0].directions_to_go

        print(directions)

        return directions

    def get_adjacent_passenger(self, coords) -> Passenger:
        """
        Obtain a passenger that is in an adjacent cell to the car.
        :return: Passenger to go
        """
        adjacent_passenger = None
        adjacent_agents = self.model.grid.get_neighbors(
            pos=coords, moore=False, include_center=False, radius=1
        )
        print(adjacent_agents)
        passengers = [
            agent
            for agent in adjacent_agents
            if isinstance(agent, Passenger) and agent.needs_ride()
        ]

        if passengers:
            adjacent_passenger = passengers[0]

        return adjacent_passenger

    def receive_passenger_confirmation(self, passenger, route):
        """Receive a confirmation from a passenger. This sets the pickup objective and the route"""
        self.pickup = passenger
        self.route = route
        # This will be changed later on so that the car can decide in the step
        self.objective = passenger

    def notify_passenger(self):
        """
        In this fragment of the turn, if the car does not have a pickup and if it has capacity,
        it will search for the nearest passenger.
        :return:
        """
        if not self.pickup and len(self.passengers) < self.capacity:
            passenger, route = self.find_nearest_passenger()
            passenger.receive_possible_ride(self, route)
            print(f"I am car {self.unique_id}. I will notify passenger {passenger.unique_id}")

    def confirm_car(self):
        """Turn fragment not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """Turn fragment not implemented for this agent"""
        pass

    def move_cars(self):
        if self.pickup and self.route:
            next_direction = self.route.pop(0)
            disp = Directions[next_direction].value
            x_new, y_new = self.pos[0] + disp[0], self.pos[1] + disp[1]
            self.model.grid.move_agent(self, (x_new, y_new))
            self.pos = (x_new, y_new)
            self.direction = next_direction

    def pick_drop_passengers(self):
        adjacent_agents = self.model.grid.get_neighbors(
            pos=self.pos, moore=False, include_center=False, radius=1
        )
        if self.objective in adjacent_agents:
            if self.objective.is_waiting:
                self.objective.is_waiting = False
                self.objective.is_traveling = True


class Passenger(Agent):
    def __init__(self, unique_id, model, start, destination):
        super().__init__(unique_id, model)
        self.pos = start
        self.destination = destination
        self.is_traveling = False
        self.has_arrived = False
        self.is_waiting = False
        self.possible_rides = {}
        self.model.grid.place_agent(self, self.pos)

    def needs_ride(self):
        return not (self.is_traveling or self.has_arrived or self.is_waiting)

    def receive_possible_ride(self, car: Car, route: list):
        self.possible_rides[car] = route

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """
        In this fragment of the turns, the passenger will evaluate all the proposals from the
        cars, and it will choose the car which has the shortest distance.
        :return:
        """
        if self.possible_rides:
            nearest_car = min(self.possible_rides.keys(), key=lambda x: len(self.possible_rides[x]))
            print(f"Sending a message to car {nearest_car.unique_id} for confirmation")
            nearest_car.receive_passenger_confirmation(self, self.possible_rides[nearest_car])
            self.is_waiting = True

    def tick_traffic_lights(self):
        pass

    def move_cars(self):
        pass

    def pick_drop_passengers(self):
        pass


class Intersection(Agent):
    def __init__(
        self,
        unique_id: int,
        model: Model,
        x: int,
        y: int,
        directions_to_go: list,
        directions_to_stop: list,
    ):

        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.directions_to_stop = directions_to_stop
        self.directions_to_go = directions_to_go
        self.traffic_lights = {
            direction: TrafficLight(self.model.next_id(), model, x, y, direction)
            for index, direction in enumerate(directions_to_stop)
        }
        self.traffic_lights[self.directions_to_stop[0]].toggle()
        self.active_light = 0
        self.ticks_to_light_change = TICKS_TO_CHANGE
        self.next_light = 0
        self.model.grid.place_agent(self, self.pos)

    def prepare_for_light_change(self):
        self.next_light = self.active_light + 1
        self.next_light %= len(self.directions_to_stop)
        self.traffic_lights[self.directions_to_stop[self.active_light]].warn_change()

    def change_traffic_light_status(self):
        self.traffic_lights[self.directions_to_stop[self.active_light]].toggle()
        self.traffic_lights[self.directions_to_stop[self.next_light]].toggle()
        self.active_light = self.next_light

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """Turn not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """
        In this turn, the intersection will determine which traffic light it should turn off
        depending on the current ticks.
        :return:
        """
        self.ticks_to_light_change -= 1

        if self.ticks_to_light_change == 1:
            self.prepare_for_light_change()

        elif self.ticks_to_light_change == 0:
            self.change_traffic_light_status()
            self.ticks_to_light_change = TICKS_TO_CHANGE

    def move_cars(self):
        pass

    def pick_drop_passengers(self):
        pass

    def get_active_direction(self):
        return self.directions_to_stop[self.active_light]


class TrafficLight(Agent):
    def __init__(self, unique_id: int, model: Model, x, y, direction):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.direction = direction
        self.status = LightStatus.RED.value

    def can_pass(self):
        return self.status == LightStatus.GREEN.value

    def warn_change(self):
        self.status = LightStatus.YELLOW.value

    def toggle(self):
        if self.status == LightStatus.YELLOW.value:
            self.status = LightStatus.RED.value

        elif self.status == LightStatus.RED.value:
            self.status = LightStatus.GREEN.value

    def __str__(self):
        return f"Direction: {self.direction}, Status: {self.status}\n"

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """Turn not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """Turn not implemented for this agent"""
        pass

    def move_cars(self):
        """Turn not implemented for this agent"""
        pass

    def pick_drop_passengers(self):
        """Turn not implemented for this agent"""
        pass


class Road(Agent):
    def __init__(self, unique_id: int, model: Model, x, y, direction):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.direction = direction
        self.model.grid.place_agent(self, self.pos)

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """Turn not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """Turn not implemented for this agent"""
        pass

    def move_cars(self):
        """Turn not implemented for this agent"""
        pass

    def pick_drop_passengers(self):
        """Turn not implemented for this agent"""
        pass


class Sidewalk(Agent):
    def __init__(self, unique_id: int, model: Model, x, y):
        super().__init__(unique_id, model)
        self.pos = (x, y)
        self.model.grid.place_agent(self, self.pos)

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """Turn not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """Turn not implemented for this agent"""
        pass

    def move_cars(self):
        """Turn not implemented for this agent"""
        pass

    def pick_drop_passengers(self):
        """Turn not implemented for this agent"""
        pass
