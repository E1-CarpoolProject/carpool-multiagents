from car import CarModel
from passenger import PassengerModel
from traffic_light import TrafficLight
from router import RouterModel
from environment import ENVIRONMENT


if __name__ == "__main__":

	# Inicializar el ambiente
	router = RouterModel(ENVIRONMENT)
	for i in range(10):
		print(f"NEW TICK {i}")
		router.step()


	# inicializa 5 pasajeros
	passenger_model = PassengerModel(5)
	passenger_model.step()

	# inicializa 5 coches
	car_model = CarModel(5)
	car_model.step()

	# # para recorrer la lista de agentes
	# for agent in passenger_model.schedule.agents:
	# 	print(agent.needs_ride())