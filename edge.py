
class Edge:

	def __init__(self, length, direction):
		self.length = length
		self.direction = direction
		self.traffic = 0

	def add_car(self):
		self.traffic += 1