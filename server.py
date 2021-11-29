import json
import os

from flask import Flask, jsonify

from model import CarpoolModel
from environment import ENVIRONMENT

app = Flask(__name__, static_url_path="")
model = CarpoolModel(
    environment=ENVIRONMENT,
    passenger_limit=20,
    passenger_inst_limit=1,
    passenger_delay=1,
    car_limit=5,
    car_inst_limit=1,
    car_delay=2,
)
port = int(os.getenv("PORT", 8585))


@app.route("/")
def root():
    return jsonify([{"message": "Hello World from IBM Cloud!"}])


@app.route("/new_cars", methods=["GET"])
def new_cars():
    model.step()
    cars_data = model.get_new_car_data()
    return json.dumps(cars_data)


@app.route("/traffic_lights", methods=["GET"])
def traffic_lights():
    traffic_data = model.get_traffic_lights_data()
    return json.dumps(traffic_data)


@app.route("/direction", methods=["GET"])
def direction():
    direction_data = model.get_cars_data()
    return json.dumps(direction_data)


@app.route("/passengers", methods=["GET"])
def passengers():
    passenger_data = model.get_passenger_data()
    print(model.schedule.steps)
    return json.dumps(passenger_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
