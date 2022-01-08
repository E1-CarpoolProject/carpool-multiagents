"""
Simulation that uses a Flask server. It sends the state of the vehicles, passengers, and traffic
lights at every tick of the system via an HTTP response-request. Designed to interact with the 3D
Unity visualization of the model.
"""
import json
import os

from flask import Flask, jsonify

from model import CarpoolModel
from environment import ENVIRONMENT

app = Flask(__name__, static_url_path="")
model = CarpoolModel(
    environment=ENVIRONMENT,
    passenger_limit=0,
    passenger_inst_limit=10,
    passenger_delay=1,
    car_limit=100,
    car_inst_limit=25,
    car_delay=2,
)
port = int(os.getenv("PORT", 8585))


@app.route("/prueba1")
def prueba_uno():
    global model
    model = CarpoolModel(
        environment=ENVIRONMENT,
        passenger_limit=0,
        passenger_inst_limit=0,
        passenger_delay=1,
        car_limit=100,
        car_inst_limit=25,
        car_delay=2,
    )
    return jsonify([{"message": "Prueba 1"}])


@app.route("/prueba2")
def prueba_dos():
    global model
    model = CarpoolModel(
        environment=ENVIRONMENT,
        passenger_limit=10,
        passenger_inst_limit=10,
        passenger_delay=1,
        car_limit=5,
        car_inst_limit=5,
        car_delay=2,
    )
    return jsonify([{"message": "Prueba 2"}])


@app.route("/prueba3")
def prueba_tres():
    global model
    model = CarpoolModel(
        environment=ENVIRONMENT,
        passenger_limit=85,
        passenger_inst_limit=86,
        passenger_delay=1,
        car_limit=15,
        car_inst_limit=16,
        car_delay=2,
    )
    return jsonify([{"message": "Prueba 3"}])


@app.route("/new_cars", methods=["GET"])
def new_cars():
    model.instantiate_agents()
    cars_data = model.get_new_car_data()
    return json.dumps(cars_data)


@app.route("/traffic_lights", methods=["GET"])
def traffic_lights():
    traffic_data = model.get_traffic_lights_data()
    return json.dumps(traffic_data)


@app.route("/directions", methods=["GET"])
def direction():
    model.step()
    direction_data = model.get_cars_data()
    return json.dumps(direction_data)


@app.route("/passengers", methods=["GET"])
def passengers():
    passenger_data = model.get_passenger_data()
    return json.dumps(passenger_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
