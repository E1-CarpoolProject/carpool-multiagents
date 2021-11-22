from car import CarModel
from passenger import PassengerModel
from traffic_light import TrafficLight
from environment import ENVIRONMENT, AGENTS
from setup_simulation import Setup


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
    print()


if __name__ == "__main__":
    # Inicializar el ambiente
    simulation_builder = Setup(ENVIRONMENT, AGENTS)
    router_model = simulation_builder.make_simulation()
    cars, passengers = simulation_builder.gather_agents_info()

    for i in range(10):
        print(f"\nNEW TICK {i+1}")
        router_model.step()
        mat = router_model.schedule.agents[0].get_environment_state()
        print_mat(mat)
