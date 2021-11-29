from typing import Type, Union

from mesa import Model
from mesa.space import MultiGrid
from mesa.time import StagedActivation

from enums import Directions, RawDirections
from agents import Passenger, Car, Road, Intersection, Sidewalk


class CarpoolModel(Model):
    def __init__(self, environment):
        super().__init__()
        self.width = len(environment[0])
        self.height = len(environment)
        self.grid = MultiGrid(self.width, self.height, torus=False)

        self.schedule = StagedActivation(
            self,
            [
                "notify_passenger",
                "confirm_car",
                "tick_traffic_lights",
                "move_cars",
                "pick_drop_passengers",
            ],
        )
        self.passenger_limit = 0
        self.passenger_count = 0
        self.passenger_creation_delay = 1
        self.passenger_tick = self.passenger_creation_delay
        self.car_limit = 200
        self.car_count = 0
        self.car_creation_delay = 1
        self.car_tick = self.car_creation_delay

        intersections, roads, sidewalks = parse_environment(environment)

        for intersection in intersections:
            a = Intersection(self.next_id(), self, **intersection)
            self.schedule.add(a)

        for road in roads:
            a = Road(self.next_id(), self, **road)
            self.schedule.add(a)

        for sidewalk in sidewalks:
            a = Sidewalk(self.next_id(), self, **sidewalk)
            self.schedule.add(a)

        self.kill_list = []

    def step(self):
        """
        In each turn, first verify it is possible to instantiate a new agent. Then, execute the
        step in each of them. As the schedule is StagedActivation, the turn of each agent will be in
        several middle steps
        :return:
        """
        self.passenger_tick -= 1
        self.car_tick -= 1

        if not self.passenger_tick and self.passenger_count < self.passenger_limit:
            self.create_agent(Passenger)
            self.passenger_tick = self.passenger_creation_delay
            self.passenger_count += 1

        if not self.car_tick and self.car_count < self.car_limit:
            self.create_agent(Car)
            self.car_tick = self.car_creation_delay
            self.car_count += 1

        self.schedule.step()

        for agent in self.kill_list:
            self.grid.remove_agent(agent)
            self.schedule.remove(agent)
        self.kill_list = []

    def create_agent(self, agent_class: Union[Type[Passenger], Type[Car]]):
        """
        Instanciate an agent of the specified class, and add it to the schedule
        :param agent_class: The agent class to be created, either Passenger or Car
        :return: None
        """
        lookup_class = Sidewalk if agent_class == Passenger else Road
        start_pos = self.find_rand_cell(lookup_class)
        dest_pos = self.find_rand_cell(lookup_class, start_pos)
        a = agent_class(self.next_id(), self, start_pos, dest_pos)
        self.schedule.add(a)

    def find_rand_cell(
        self, lookup_class: Union[Type[Sidewalk], Type[Road]], exclude_cells=None
    ) -> (int, int):
        """
        Obtain a random cell that can be used to instantiate either a Car or a Passenger. In
        order to do this, there must be exactly one agent of type Sidewalk or Road depending on
        the objective.
        :param lookup_class: The class to be looked for (Sidewalk or Road)
        :param exclude_cells: The cells that should be excluded for the search.
        :return: The cell that can be used to instantiate
        """
        pos_x, pos_y = None, None
        found_useful_cell = False
        if exclude_cells is None:
            exclude_cells = []

        while not found_useful_cell:
            pos_x = self.random.randint(0, self.width - 1)
            pos_y = self.random.randint(0, self.height - 1)
            cell = self.grid.get_cell_list_contents([(pos_x, pos_y)])
            if (
                cell
                and len(cell) == 1
                and isinstance(cell[0], lookup_class)
                and not (pos_x, pos_y) in exclude_cells
            ):
                found_useful_cell = True

        return pos_x, pos_y


def parse_environment(environment: list) -> (list, list, list):
    """
    This function check on all the board which columns are intersections, and then for each
    intersection determines which directions are involved in it. Given that the streets are
    one way only, we have two directions involved in an intersection. After this, it initializes
    the intersection model and returns a dictionary of the intersection objects. The key is
    the number of the cell, starting at [0, 0] and counting leftwards and then downwards.
    :return: The dictionary of intersections.
    """
    intersections_data = []
    road_data = []
    sidewalk_data = []
    n_rows = len(environment)
    n_cols = len(environment[0])

    for row_index in range(n_rows):
        for col_index in range(n_cols):
            cell = environment[row_index][col_index]
            data = {"x": col_index, "y": n_rows - row_index - 1}

            if cell == "IN":
                directions_to_go, directions_to_stop = find_intersection_directions(
                    row_index, col_index, environment
                )
                data["directions_to_go"] = directions_to_go
                data["directions_to_stop"] = directions_to_stop
                intersections_data.append(data)

            elif cell in [direction.name for direction in Directions]:
                data["direction"] = cell
                road_data.append(data)

            elif cell == "SW":
                sidewalk_data.append(data)

    return intersections_data, road_data, sidewalk_data


def find_intersection_directions(row: int, col: int, environment: list) -> (list, list):
    """
    Function that finds the directions involved in an intersection and returns a list of them
    :param environment:
    :param row: The row index of the intersection
    :param col: The column index of the intersection
    :return: List of the directions involved in the intersection
    """
    possible_directions = [direction.name for direction in RawDirections]
    directions_to_stop = set()
    directions_to_go = set()

    for direction_name in possible_directions:
        displacement = RawDirections[direction_name].value
        test_row = row + displacement[0]
        test_col = col + displacement[1]

        try:
            coming_direction = environment[test_row][test_col]
            if coming_direction == direction_name:
                directions_to_go.add(direction_name)

            elif coming_direction in possible_directions:
                directions_to_stop.add(coming_direction)

        except IndexError:
            continue

    return list(directions_to_go), list(directions_to_stop)


def agent_portrayal(agent):
    """
    Determine how an agent is displayed in mesa's server grid.
    :param agent:
    :return:
    """
    portrayal = {}

    if isinstance(agent, Car):
        portrayal["Shape"] = f"shapes/car_{agent.direction}.png"
        portrayal["scale"] = "1"
        portrayal["Layer"] = "3"
        portrayal["text"] = f"Car {agent.unique_id}"
        portrayal["text_color"] = "#AA08F8"

    elif isinstance(agent, Intersection):
        portrayal["Shape"] = "arrowHead"
        portrayal["scale"] = 0.5
        portrayal["heading_x"] = Directions[agent.get_active_direction()].value[0]
        portrayal["heading_y"] = Directions[agent.get_active_direction()].value[1]
        portrayal["Layer"] = "1"
        portrayal["Color"] = "gray"

    elif isinstance(agent, Sidewalk):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "lightgray"
        portrayal["Filled"] = "False"
        portrayal["w"] = 0.7
        portrayal["h"] = 0.7
        portrayal["Layer"] = "1"
        portrayal["text"] = agent.text
        portrayal["text_color"] = "black"

    elif isinstance(agent, Road):
        portrayal["Shape"] = "arrowHead"
        portrayal["scale"] = 0.5
        portrayal["heading_x"] = Directions[agent.direction].value[0]
        portrayal["heading_y"] = Directions[agent.direction].value[1]
        portrayal["Layer"] = "1"
        portrayal["Color"] = "lightgray"
        portrayal["text"] = agent.text
        portrayal["text_color"] = "black"

    elif isinstance(agent, Passenger):
        if not agent.is_traveling:
            portrayal["Shape"] = f"shapes/passenger_{'final' if agent.has_arrived else 'waiting'}.png"
            portrayal["scale"] = "1"
            portrayal["Layer"] = "3"
            portrayal["text"] = f"{agent.unique_id}"
            portrayal["text_color"] = "white"

    return portrayal
