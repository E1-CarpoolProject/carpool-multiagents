import copy

from car import CarModel
from enums import Directions
from intersection import IntersectionModel
from passenger import PassengerModel
from router import RouterModel

PASSENGER_KEYS = {"1": "start", "2": "destination"}
CAR_KEYS = {"A": "start", "B": "destination"}


class Setup:
    def __init__(self, environment_data, agents_data):
        self.environment = copy.deepcopy(environment_data)
        self.agents = copy.deepcopy(agents_data)

    def make_simulation(self):
        intersection_data = self.build_intersections()
        cars_data, passengers_data = self.gather_agents_info()

        car_model = CarModel(cars_data)
        passenger_model = PassengerModel(passengers_data)
        intersection_model = IntersectionModel(intersection_data)
        router_model = RouterModel(
            self.environment, self.agents, intersection_model, car_model, passenger_model
        )
        car_model.city_map = router_model
        car_model.make_agents()
        router_model.single.make_agents_map()
        car_model.step()

        return router_model

    def build_intersections(self) -> (IntersectionModel, dict):
        """
        This function check on all the board which columns are intersections, and then for each
        intersection determines which directions are involved in it. Given that the streets are
        one way only, we have two directions involved in an intersection. After this, it initializes
        the intersection model and returns a dictionary of the intersection objects. The key is
        the number of the cell, starting at [0, 0] and counting leftwards and then downwards.
        :return: The dictionary of intersections.
        """
        intersections_data = {}
        n_rows = len(self.environment)
        n_cols = len(self.environment[0])

        for row_index in range(n_rows):
            for col_index in range(n_cols):
                if self.environment[row_index][col_index] == "IN":
                    intersection_index = n_cols * row_index + col_index
                    directions_to_go, directions_to_stop = self.find_intersection_directions(
                        row_index, col_index
                    )
                    intersections_data[intersection_index] = {
                        "x": row_index,
                        "y": col_index,
                        "directions_to_stop": directions_to_stop,
                        "directions_to_go": directions_to_go,
                    }

        return intersections_data

    def find_intersection_directions(self, row: int, col: int) -> (list, list):
        """
        Function that finds the directions involved in an intersection and returns a list of them
        :param row: The row index of the intersection
        :param col: The column index of the intersection
        :return: List of the directions involved in the intersection
        """
        possible_directions = [str(direction).split(".")[-1] for direction in Directions]
        directions_to_stop = set()
        directions_to_go = set()

        for direction_name in possible_directions:
            displacement = Directions[direction_name].value
            test_row = row + displacement[0]
            test_col = col + displacement[1]

            try:
                coming_direction = self.environment[test_row][test_col]
                if coming_direction == direction_name:
                    directions_to_go.add(direction_name)

                elif coming_direction in possible_directions:
                    directions_to_stop.add(coming_direction)

            except IndexError:
                continue

        return list(directions_to_go), list(directions_to_stop)

    def gather_agents_info(self):
        cars_data, passengers_data = {}, {}
        n_rows = len(self.environment)
        n_cols = len(self.environment[0])

        for row_index in range(n_rows):
            for col_index in range(n_cols):
                cell = self.agents[row_index][col_index]
                if cell != "00":
                    is_passenger = ord("A") <= ord(cell[0]) <= ord("Z")
                    data_dict = passengers_data if is_passenger else cars_data
                    keys = PASSENGER_KEYS if is_passenger else CAR_KEYS
                    previous_data = data_dict.get(cell[0])

                    if previous_data:
                        previous_data[keys[cell[1]]] = (row_index, col_index)

                    else:
                        data_dict[cell[0]] = {keys[cell[1]]: (row_index, col_index)}

        return cars_data, passengers_data
