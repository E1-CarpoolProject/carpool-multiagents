import copy

from mesa import Agent, Model
from mesa.time import RandomActivation, BaseScheduler

from car import CarAgent
from enums import Directions
from intersection import IntersectionModel


def print_mat(matrix):
    for row in matrix:
        row_str = ""
        for item in row:
            if item == "00":
                item = "■"
            elif item == "LF":
                item = "←"
            elif item == "UP":
                item = "↑"
            elif item == "DW":
                item = "↓"
            elif item == "RH":
                item = "→"

            row_str += f"{item}  "
        print(row_str)


class RouterAgent(Agent):
    def __init__(self, unique_id: int, model: Model, environment_data):
        super().__init__(unique_id, model)

        self.environment = copy.deepcopy(environment_data)
        self.intersection_model = self.build_intersections()

    def build_intersections(self) -> (IntersectionModel, dict):
        """
        This function check on all the board which columns are intersections, and then for each
        intersection determines which directions are involved in it. Given that the streets are
        one way only, we have two directions involved in an intersection. After this, it initializes
        the intersection model and returns a dictionary of the intersection objects. The key is
        the number of the cell, starting at [0, 0] and counting leftwards and then downwards.
        :return: The dictionary of intersections.
        """
        intersections_input = {}
        n_rows = len(self.environment)
        n_cols = len(self.environment[0])

        for row_index in range(n_rows):
            for col_index in range(n_cols):
                if self.environment[row_index][col_index] == "IN":
                    intersection_index = n_rows * row_index + col_index
                    directions_to_go, directions_to_stop = self.find_intersection_directions(
                        row_index, col_index
                    )
                    intersections_input[intersection_index] = {
                        "x": row_index,
                        "y": col_index,
                        "directions_to_stop": directions_to_stop,
                        "directions_to_go": directions_to_go,
                    }

        intersection_model = IntersectionModel(intersections_input)
        return intersection_model

    def find_intersection_directions(self, row: int, col: int) -> (list, list):
        """
        Function that finds the directions involved in an intersection and returns a list of them
        :param row: The row index of the intersection
        :param col: The column index of the intersection
        :return: List of the directions involved in the intersection
        """
        print(f"Intersection: {row}, {col}")
        possible_directions = [str(direction).split(".")[-1] for direction in Directions]
        directions_to_stop = set()
        directions_to_go = set()

        for direction_name in possible_directions:
            displacement = Directions[direction_name].value
            test_row = row + displacement[0]
            test_col = col + displacement[1]

            try:
                coming_direction = self.environment[test_row][test_col]
                print(coming_direction, direction_name)
                if coming_direction == direction_name:
                    directions_to_go.add(direction_name)

                elif coming_direction in possible_directions:
                    directions_to_stop.add(coming_direction)

            except IndexError:
                continue

        return list(directions_to_go), list(directions_to_stop)

    def get_environment_state(self):
        env = copy.deepcopy(self.environment)
        for intersection in self.intersection_model.intersection_map.values():
            row, col = intersection.x, intersection.y
            active_direction = intersection.get_active_direction()
            env[row][col] = active_direction
        return env

    def get_closest_passenger(self, car: CarAgent):
        pass

    def step(self):
        self.intersection_model.step()
        print_mat(self.get_environment_state())


class RouterModel(Model):
    """A model with some number of agents."""

    def __init__(self, environment_data):
        super().__init__()
        self.schedule = BaseScheduler(self)
        a = RouterAgent(unique_id=0, model=self, environment_data=environment_data)
        self.schedule.add(a)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
