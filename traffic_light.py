from enums import LightStatus


class TrafficLight:

    def __init__(self, tid, direction):
        self.tid = tid
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
