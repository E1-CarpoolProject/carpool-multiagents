from traffic_light import TrafficLight
from mesa import Agent, Model
from mesa.time import BaseScheduler

INTERSECTION_LENGTH = 50
TICKS_TO_CHANGE = 2


class IntersectionAgent(Agent):
    """ An agent with fixed initial wealth."""

    def __init__(self, unique_id, model, intersection_data):
        """
        Initialize an intersection
        :param unique_id:
        :param model:
        :param intersection_data:
        {
            "x": num,
            "y": num,
            "directions": ["up", "down", ...]
        }
        """
        super().__init__(unique_id, model)
        self.x_mid = intersection_data["x"]
        self.y_mid = intersection_data["y"]
        self.traffic_lights = [
            TrafficLight(index, direction)
            for index, direction in enumerate(intersection_data["directions"])
        ]
        self.traffic_lights[0].toggle()
        self.active_light = 0
        self.ticks_to_light_change = TICKS_TO_CHANGE
        self.next_light = 0

    def prepare_for_light_change(self):
        self.next_light = self.active_light + 1
        self.next_light %= len(self.traffic_lights)
        self.traffic_lights[self.active_light].warn_change()

    def change_traffic_light_status(self):
        self.traffic_lights[self.active_light].toggle()
        self.traffic_lights[self.next_light].toggle()
        self.active_light = self.next_light

    def points_turn(self, direction):
        if direction == 1:
            self.x_prev = self.x_pos + 1
            self.y_prev = self.y_pos - 1
        elif direction == 2:
            self.x_prev = self.x_pos - 1
            self.y_prev = self.y_pos + 1
        elif direction == 3:
            self.x_prev = self.x_pos - 1
            self.y_prev = self.y_pos - 1
        elif direction == 4:
            self.x_prev = self.x_pos + 1
            self.y_prev = self.y_pos + 1

    def step(self):
        self.ticks_to_light_change -= 1

        if self.ticks_to_light_change == 1:
            self.prepare_for_light_change()

        elif self.ticks_to_light_change == 0:
            self.change_traffic_light_status()
            self.ticks_to_light_change = TICKS_TO_CHANGE

        status = f"""
        Intersection
        x: {self.x_mid}, y: {self.y_mid}
        Traffic lights status:"""
        status += "\n"
        for light in self.traffic_lights:
            status += "\t\t" + str(light)
        status += "\n"
        print(status)


class IntersectionModel(Model):
    """A model with some number of agents."""

    def __init__(self, intersection_data):
        super().__init__()
        self.schedule = BaseScheduler(self)
        for i, data in enumerate(intersection_data):
            a = IntersectionAgent(unique_id=i, model=self, intersection_data=data)
            self.schedule.add(a)

    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()

