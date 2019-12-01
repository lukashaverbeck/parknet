from flask import Flask, request, jsonify, render_template
from vehicle.Agent import Agent

app = Flask(__name__)
agent = Agent()


@app.route("/")
@app.route("/UI")
def ui():
    return render_template("UI.html")


def open_interface(debug=False):
    ip_address = "192.168.2.116"
    port = "5000"
    app.run(host=ip_address, port=port, debug=debug)


# TODO get the agent's real data
@app.route("/data-interval")
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
    agent.driver().stop_driving()
    return ""


@app.route("/change-mode", methods=["POST"])
def change_mode():
    data = request.get_json(silent=True)

    if "mode" in data:
        agent.driver().change_mode(data["mode"])

    return ""

@app.route("/accelerate-forward", methods=["POST"])
def accelerate_forward():
    agent.driver().accelerate(0.05)
    return ""

@app.route("/accelerate-backward", methods=["POST"])
def accelerate_backward():
    agent.driver().accelerate(-0.05)
    return ""

@app.route("/steer-left", methods=["POST"])
def steer_left():
    agent.driver().steer(-1)
    return ""

@app.route("/steer-right", methods=["POST"])
def steer_right():
    agent.driver().steer(1)
    return ""


open_interface(True)