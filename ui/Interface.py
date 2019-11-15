import sys
sys.path.append(sys.path[0][:-3])

from flask import Flask, request, jsonify, render_template
from vehicle.Agent import Agent

app = Flask(__name__)
agent = Agent()


@app.route("/")
@app.route("/UI")
def home():
    return render_template("UI.html")


# TODO get the agent's real data
@app.route("/data-internal")
def data():
    driver = agent.driver()
    sensors = driver.get_sensor_manager()

    data = [
        {
            "id": "velocity",
            "value": driver.get_velocity(),
            "unit": "m/s"
        },
        {
            "id": "steering-angle",
            "value": driver.get_angle(),
            "unit": "°"
        },
        {
            "id": "distance-front",
            "value": sensors.get_distance(0),
            "unit": "m"
        },
        {
            "id": "distance-right",
            "value": sensors.get_distance(1),
            "unit": "m"
        },
        {
            "id": "distance-back",
            "value": sensors.get_distance(2),
            "unit": "m"
        },
    ]

    return jsonify(data)

@app.route("/change-mode", methods=["POST"])
def change_mode():
    data = request.get_json(silent=True)

    if "mode" in data:
        agent.driver().change_mode(data["mode"])

    return ""

@app.route("/start-recording", methods=["POST"])
def start_recording():
    agent.driver().start_recording()

    return ""

@app.route("/stop-recording", methods=["POST"])
def stop_recording():
    agent.driver().stop_recording()

    return ""

@app.route("/emergency-stop", methods=["POST"])
def emergency_stop():
    agent.driver().stop_recording()
    agent.driver().accelerate(0.0)
    agent.driver().stop_driving()

    return ""

def open_interface(debug=False):
    ip_address = "192.168.2.116"
    port = "5000"
    app.run(host=ip_address, port=port, debug=debug)


open_interface(True)
