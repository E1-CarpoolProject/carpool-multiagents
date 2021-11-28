import copy

from mesa import Agent, Model
from mesa.time import RandomActivation, BaseScheduler

from car import CarModel
from passenger import PassengerModel
from enums import Directions
from intersection import IntersectionModel


class RouterAgent(Agent):

    def __init__(
        self,
        unique_id: int,
        model: Model,
        environment_data,
        agents_data,
        intersection_model,
        car_model: CarModel,
        passenger_model: PassengerModel,
    ):
        super().__init__(unique_id, model)
        self.environment = copy.deepcopy(environment_data)
        self.intersection_model = intersection_model
        self.car_model = car_model
        self.passenger_model = passenger_model
        self.agents = []

    def make_agents_map(self):
        for _ in range(len(self.environment)):
            self.agents.append(["0"] * len(self.environment[0]))

        for key, car in self.car_model.car_map.items():
            self.agents[car.pos[0]][car.pos[1]] = key

        for key, passenger in self.passenger_model.passenger_map.items():
            self.agents[passenger.pos[0]][passenger.pos[1]] = key

    def move_car_position(self, previous, new):
        """
        Update the car position by one unit in the map.
        :param previous:
        :param new:
        :return:
        """
        car = self.agents[previous[0]][previous[1]]
        self.agents[previous[0]][previous[1]] = "00"
        self.agents[new[0]][new[1]] = car

    def get_adjacent_passenger(self, pos):
        """
        Obtain the passenger that is adjacent to the car in case there is one
        :param pos:
        :return:
        """
        passenger = None
        for direction in Directions:
            displacement = direction.value
            trial_row = pos[0] + displacement[0]
            trial_col = pos[1] + displacement[1]

            try:
                agent = self.agents[trial_row][trial_col]
                is_passenger = ord("A") <= ord(agent) <= ord("Z")

                if is_passenger:
                    potential_passenger = self.passenger_model.passenger_map[agent]
                    if potential_passenger.needs_ride():
                        passenger = potential_passenger
                        break

            except IndexError:
                continue

        return passenger

    def get_possible_directions(self, pos):
        """
        Obtain the possible directions that a car can move to from a give position
        :param pos:
        :return:
        """
        n_cols = len(self.environment[0])
        directions = []

        row, col = pos
        direction = self.environment[row][col]

        if direction == "IN":
            intersection_index = n_cols * row + col
            directions_to_go = self.intersection_model.intersection_map[
                intersection_index].directions_to_go
            for direction in directions_to_go:
                directions.append(direction)

        else:
            directions.append(direction)

        return directions

    def get_environment_state(self):
        env = copy.deepcopy(self.environment)
        for intersection in self.intersection_model.intersection_map.values():
            row, col = intersection.x, intersection.y
            active_direction = intersection.get_active_direction()
            env[row][col] = active_direction
        return env

    def step(self):
        self.intersection_model.step()


class RouterModel(Model):
    """A model with some number of agents."""

    def __init__(
        self, environment_data, agents_data, intersection_model, car_model, passenger_model
    ):
        super().__init__()
        self.schedule = BaseScheduler(self)
        a = RouterAgent(
            0, self, environment_data, agents_data, intersection_model, car_model, passenger_model
        )
        self.schedule.add(a)
        self.single = a

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
