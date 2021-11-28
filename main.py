from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

from environment import ENVIRONMENT
from model import agent_portrayal, CarpoolModel

if __name__ == "__main__":
    height = len(ENVIRONMENT)
    width = len(ENVIRONMENT[0])
    model_params = {
        "environment": ENVIRONMENT
    }
    grid = CanvasGrid(agent_portrayal, width, height, 900, 900)
    server = ModularServer(CarpoolModel, [grid], "CarpoolModel", model_params)
    server.port = 8521
    server.launch()
