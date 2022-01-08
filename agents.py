"""
Contains the implementation of all the agents of the system.
"""
from __future__ import annotations
from copy import copy
from typing import List, Set, Optional

from mesa import Agent, Model

from enums import Directions, LightStatus

TICKS_TO_CHANGE = 2


class Car(Agent):
    capacity = 5
    movements = 0
    moving_cars = 0

    def __init__(self, unique_id, model: Model, start: (int, int), destination: (int, int)):
        """
        Initialize a Car agent with a specified start and final position
        :param unique_id: int
        :param model: CarpoolModel
        :param start: (x, y) tuple
        :param destination:  (x, y) tuple
        """
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
        self.real_movement = None
        Car.moving_cars += 1
        road_destination = self.model.grid.get_cell_list_contents([self.destination])
        road = [agent for agent in road_destination if isinstance(agent, Road)][0]
        road.text = f"{self.unique_id}"

    def find_optimal_routes(self, passengers: List[Passenger]) -> List[str]:
        """
        Find the optimal routes to a set of points by using a BFS. Note that a single search is
        used to find all the objectives, reducing the complexity. Objectives must be passengers
        to be dropped.
        :param passengers: List of passengers to be dropped
        :return: List of tuples (Passenger, ["UP", "DW", "LF"])
        """
        routes = []
        q = [(self.pos, [])]
        visited = set()
        while q:
            curr_tile, curr_route = q.pop(0)

            for passenger in passengers:
                for direction in Directions:
                    disp = direction.value
                    trial_cell = curr_tile[0] + disp[0], curr_tile[1] + disp[1]

                    if passenger.is_traveling:
                        if trial_cell == passenger.destination:
                            routes.append((passenger, curr_route))

                    elif passenger.is_waiting:
                        if trial_cell == passenger.pos:
                            routes.append((passenger, curr_route))
                            passengers.remove(passenger)

            if not passengers:
                break

            next_tiles = self.next_direction(curr_tile, curr_route, visited)
            q += next_tiles

        return routes

    def shortest_route_home(self) -> List[str]:
        """
        Find the optimal route to the destination from the current position.
        :return: List of directions in the route
        """
        q = [(self.pos, [])]
        visited = set()
        route = None
        while q:
            curr_tile, curr_route = q.pop(0)

            if curr_tile == self.destination:
                route = curr_route
                break

            next_tiles = self.next_direction(curr_tile, curr_route, visited)
            q += next_tiles

        return route

    def receive_passenger_confirmation(self, passenger: Passenger, route: List[str]):
        """Receive a confirmation from a passenger. This sets the pickup objective and the route"""
        self.pickup = (passenger, route)

    def apply_movement(self, next_direction: str):
        """Apply a direction movement"""
        disp = Directions[next_direction].value
        x_new, y_new = self.pos[0] + disp[0], self.pos[1] + disp[1]
        return x_new, y_new

    def notify_passenger(self):
        """
        TURN PART 1
        In this fragment of the turn, if the car does not have a pickup and if it has capacity,
        it will search for the nearest passenger.
        :return:
        """
        if not self.pickup and len(self.passengers) < self.capacity:
            passenger, route = self.find_nearest_passenger()
            if passenger:
                passenger.receive_possible_ride(self, route)

    def find_nearest_passenger(self) -> Optional[(Passenger, List[str])]:
        """
        Find the nearest passenger by using a BFS.
        :return: Return the passenger and the list of movements to reach it
        """
        potential_passenger, potential_route = None, []
        q = [(self.pos, [])]
        visited = set()
        while q:
            curr_tile, curr_route = q.pop(0)

            adjacent_passenger = self.get_adjacent_passenger(curr_tile)
            if adjacent_passenger:
                potential_passenger, potential_route = adjacent_passenger, curr_route
                break

            next_tiles = self.next_direction(curr_tile, curr_route, visited)
            q += next_tiles

        return potential_passenger, potential_route

    def get_adjacent_passenger(self, coords: (int, int)) -> Optional[Passenger]:
        """
        Utility function. Obtain a passenger that is in an adjacent cell to the specified position,
        if any.
        :return: Passenger adjacent to the position.
        """
        adjacent_passenger = None
        adjacent_agents = self.model.grid.get_neighbors(
            pos=coords, moore=False, include_center=False, radius=1
        )
        passengers = [
            agent
            for agent in adjacent_agents
            if isinstance(agent, Passenger) and agent.needs_ride()
        ]

        if passengers:
            adjacent_passenger = passengers[0]

        return adjacent_passenger

    def confirm_car(self):
        """TURN PART 2 Turn fragment not implemented for this agent"""
        pass

    def tick_traffic_lights(self):
        """TURN PART 3 Turn fragment not implemented for this agent"""
        pass

    def move_cars(self):
        """
        Logic that controls the direction of the movement and if it is possible to move given the
        status of the traffic lights. This is the most complex method since it handles the whole
        movement logic, including long term, temporary, and immediate decisions.
        """
        if not self.objective:
            interest_points = copy(self.drops)
            if self.pickup:
                interest_points.append(self.pickup[0])

            routes = self.find_optimal_routes(interest_points)
            if routes:
                optimal = min(routes, key=lambda x: len(x[1]))
                self.route = optimal[1]
                self.objective = optimal[0]

        if not self.route:
            if isinstance(self.objective, Passenger):
                return

            elif Passenger.passengers_without_ride > 0:
                cell = self.model.grid.get_cell_list_contents([self.pos])
                cars = [agent for agent in cell if isinstance(agent, Car)]
                intersection = [agent for agent in cell if isinstance(agent, Intersection)]
                road = [agent for agent in cell if isinstance(agent, Road)]

                if cars:
                    for car in cars:
                        if car.pos != car.destination:
                            self.real_movement = "NA"
                            return

                elif intersection:
                    if intersection[0].get_active_direction() == self.direction:
                        direction_to_go = self.random.choice(intersection[0].directions_to_go)
                        x, y = self.apply_movement(direction_to_go)
                        self.model.grid.move_agent(self, (x, y))
                        self.real_movement = "NA"
                        return

                elif road:
                    x, y = self.apply_movement(road[0].direction)
                    self.model.grid.move_agent(self, (x, y))
                    self.real_movement = road[0].direction
                    return

            elif self.pos == self.destination:
                self.model.kill_list.append(self)
                Car.moving_cars -= 1
                self.real_movement = "PA"
                return

            else:
                self.route = self.shortest_route_home()
                self.objective = self

        next_direction = self.route.pop(0)
        x_new, y_new = self.apply_movement(next_direction)

        cell = self.model.grid.get_cell_list_contents([(x_new, y_new)])
        intersection = [agent for agent in cell if isinstance(agent, Intersection)]
        cars = [agent for agent in cell if isinstance(agent, Car)]

        if intersection:
            if intersection[0].get_active_direction() != self.direction:
                self.route.insert(0, next_direction)
                self.real_movement = "NA"
                return

        elif cars:
            for car in cars:
                if car.pos != car.destination:
                    self.route.insert(0, next_direction)
                    self.real_movement = "NA"
                    return

        self.model.grid.move_agent(self, (x_new, y_new))
        self.pos = (x_new, y_new)
        self.direction = next_direction
        self.real_movement = self.direction
        Car.movements += 1

        for i in range(len(self.passengers)):
            self.model.grid.move_agent(self.passengers[i], self.pos)
            self.passengers[i].pos = self.pos

    def pick_drop_passengers(self):
        """
        TURN PART 5
        Determine if it is possible to pickup or drop the objective depending on the Passenger´s
        state.
        :return:
        """
        adjacent_agents = self.model.grid.get_neighbors(
            pos=self.pos, moore=False, include_center=False, radius=1
        )
        if isinstance(self.objective, Passenger):
            if self.objective.is_waiting and self.objective in adjacent_agents:
                self.objective.is_waiting = False
                self.objective.is_traveling = True
                self.drops.append(self.objective)
                self.passengers.append(self.objective)
                self.pickup = None
                self.objective = None

            elif self.objective.is_traveling:
                for direction in Directions:
                    displacement = direction.value
                    trial_x = self.pos[0] + displacement[0]
                    trial_y = self.pos[1] + displacement[1]
                    if self.objective.destination == (trial_x, trial_y):
                        self.objective.is_traveling = False
                        self.objective.has_arrived = True
                        self.passengers.remove(self.objective)
                        self.drops.remove(self.objective)
                        self.objective.drop()
                        self.objective = None
                        break

    def get_possible_directions(self, coords: (int, int)) -> List[str]:
        """
        Utility function. Obtain the possible directions that a car can go to from a specified
        position.
        :return: List of directions
        """
        directions = []
        cell = self.model.grid.get_cell_list_contents([coords])
        road = [road for road in cell if isinstance(road, Road)]
        intersection = [intersec for intersec in cell if isinstance(intersec, Intersection)]

        if road:
            directions.append(road[0].direction)

        elif intersection:
            directions += intersection[0].directions_to_go

        return directions

    def next_direction(
        self, curr_tile: (int, int), curr_route: List[str], visited: Set[(int, int)]
    ) -> List[((int, int), List[str])]:
        """
        Utility Function. Find the next possible directions given the current position, checking
        that the resulting tiles have not been visited before. This is a utility function used to
        avoid repetition in the BFS.
        :param curr_tile: The current tile in the search
        :param curr_route: The current route in the search
        :param visited: The set of visited nodes
        :return: List of tuples that include the position and route of the next tiles that should be
        checked.
        """
        directions = []
        possible_directions = self.get_possible_directions(curr_tile)
        for direction in possible_directions:
            displacement = Directions[direction].value
            next_row = curr_tile[0] + displacement[0]
            next_col = curr_tile[1] + displacement[1]
            next_pos = (next_row, next_col)

            if next_pos not in visited:
                next_route = copy(curr_route)
                next_route.append(direction)
                directions.append((next_pos, next_route))
                visited.add(next_pos)

        return directions


class Passenger(Agent):
    passengers_without_ride = 0

    def __init__(self, unique_id, model, start, destination):
        super().__init__(unique_id, model)
        self.pos = start
        self.destination = destination
        self.is_traveling = False
        self.has_arrived = False
        self.is_waiting = False
        self.possible_rides = {}
        self.model.grid.place_agent(self, self.pos)
        Passenger.passengers_without_ride += 1
        sw_destination = self.model.grid.get_cell_list_contents([self.destination])
        sidewalk = [agent for agent in sw_destination if isinstance(agent, Sidewalk)][0]
        sidewalk.text = f"{self.unique_id}"

    def needs_ride(self):
        return not (self.is_traveling or self.has_arrived or self.is_waiting)

    def receive_possible_ride(self, car: Car, route: list):
        self.possible_rides[car] = route

    def drop(self):
        self.model.grid.move_agent(self, self.destination)
        self.pos = self.destination

    def notify_passenger(self):
        """Turn not implemented for this agent"""
        pass

    def confirm_car(self):
        """
        In this fragment of the turns, the passenger will evaluate all the proposals from the
        cars, and it will choose the car which has the shortest distance.
        :return:
        """
        if self.possible_rides and self.needs_ride():
            nearest_car = min(self.possible_rides.keys(), key=lambda x: len(self.possible_rides[x]))
            self.is_waiting = True
            Passenger.passengers_without_ride -= 1
            nearest_car.receive_passenger_confirmation(self, self.possible_rides[nearest_car])

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
        self.id = f"{str(x).zfill(2)}{str(y).zfill(2)}{self.direction}"

    def can_pass(self):
        return self.status == LightStatus.GREEN.value

    def warn_change(self):
        self.status = LightStatus.YELLOW.value

    def toggle(self):
        if self.status == LightStatus.YELLOW.value:
            self.status = LightStatus.RED.value

        elif self.status == LightStatus.RED.value:
            self.status = LightStatus.GREEN.value

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
        self.text = ""

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
        self.text = ""

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
