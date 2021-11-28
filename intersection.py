from traffic_light import TrafficLight
from mesa import Agent, Model
from mesa.time import BaseScheduler

INTERSECTION_LENGTH = 50
TICKS_TO_CHANGE = 2


class IntersectionAgent(Agent):

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
        print(intersection_data)
        self.x = intersection_data["x"]
        self.y = intersection_data["y"]
        self.directions_to_stop = intersection_data["directions_to_stop"]
        self.directions_to_go = intersection_data["directions_to_go"]
        self.traffic_lights = {
            direction: TrafficLight(index, direction)
            for index, direction in enumerate(intersection_data["directions_to_stop"])
        }
        self.traffic_lights[self.directions_to_stop[0]].toggle()
        self.active_light = 0
        self.ticks_to_light_change = TICKS_TO_CHANGE
        self.next_light = 0

    def prepare_for_light_change(self):
        self.next_light = self.active_light + 1
        self.next_light %= len(self.directions_to_stop)
        self.traffic_lights[self.directions_to_stop[self.active_light]].warn_change()

    def change_traffic_light_status(self):
        self.traffic_lights[self.directions_to_stop[self.active_light]].toggle()
        self.traffic_lights[self.directions_to_stop[self.next_light]].toggle()
        self.active_light = self.next_light

    def step(self):
        self.ticks_to_light_change -= 1

        if self.ticks_to_light_change == 1:
            self.prepare_for_light_change()

        elif self.ticks_to_light_change == 0:
            self.change_traffic_light_status()
            self.ticks_to_light_change = TICKS_TO_CHANGE

    def get_active_direction(self):
        return self.directions_to_stop[self.active_light]


class IntersectionModel(Model):

    def __init__(self, intersection_input):
        super().__init__()
        self.schedule = BaseScheduler(self)
        self.intersection_map = {}
        print("\nInitializing intersections")
        for key, data in intersection_input.items():
            print(f"Key: {key}")
            a = IntersectionAgent(unique_id=key, model=self, intersection_data=data)
            self.schedule.add(a)
            self.intersection_map[key] = a
        print()


    def step(self):
        self.schedule.step()
