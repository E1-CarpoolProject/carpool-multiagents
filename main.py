"""
Simulation that uses the Mesa server for the visualization of the model.
"""
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

from environment import ENVIRONMENT
from model import agent_portrayal, CarpoolModel

if __name__ == "__main__":
    height = len(ENVIRONMENT)
    width = len(ENVIRONMENT[0])
    model_params = {
        "environment": ENVIRONMENT,
        "passenger_limit": UserSettableParameter("slider", "Total passenger limit", 20, 0, 300),
        "passenger_inst_limit": UserSettableParameter(
            "slider", "Limit of passenger per " "instantiaton batch", 1, 1, 300
        ),
        "passenger_delay": UserSettableParameter(
            "slider", "Delay between passenger instantiation " "batch", 1, 0, 10
        ),
        "car_limit": UserSettableParameter("slider", "Total car limit", 10, 0, 300),
        "car_inst_limit": UserSettableParameter(
            "slider", "Limit of car per instantiation batch", 1, 1, 300
        ),
        "car_delay": UserSettableParameter(
            "slider", "Delay between car instantitation batch", 1, 0, 20
        ),
    }
    grid = CanvasGrid(agent_portrayal, width, height, 900, 900)
    server = ModularServer(CarpoolModel, [grid], "CarpoolModel", model_params)
    server.port = 8521
    server.launch()
