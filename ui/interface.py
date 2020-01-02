import sys
sys.path.append(sys.path[0][:-3])

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
agent = None
driver = None
sensor_manager = None
action_manager = None


class WebInterface:
    def __init__(self, agent_instance, driver_instance, sensor_manager_instance, action_manager_instance):
        global agent, driver, sensor_manager, action_manager
        agent = agent_instance
        driver = driver_instance
        sensor_manager = sensor_manager_instance
        action_manager = action_manager_instance

    def start(self, ip_address, debug=False):
        port = "5000"
        app.run(host=ip_address, port=port, debug=debug)
        print(f"Starting Webserver(Interface) at: {ip_address}")


@app.route("/")
@app.route("/UI")
def ui():
    return render_template("UI.html")


@app.route("/data-interval")
def data():
    data = [
        {
            "id": "velocity",
            "value": driver.velocity,
            "unit": "PWM"
        },
        {
            "id": "steering-angle",
            "value": driver.angle,
            "unit": "°"
        },
        {
            "id": "distance-front",
            "value": sensor_manager.front,
            "unit": "m"
        },
        {
            "id": "distance-right",
            "value": sensor_manager.right,
            "unit": "m"
        },
        {
            "id": "distance-back",
            "value": sensor_manager.rear,
            "unit": "m"
        },
    ]

    return jsonify(data)


@app.route("/start-recording", methods=["POST"])
def start_recording():
    driver.start_recording()
    return ""


@app.route("/stop-recording", methods=["POST"])
def stop_recording():
    driver.stop_recording()
    return ""


@app.route("/emergency-stop", methods=["POST"])
def emergency_stop():
    driver.stop_recording()
    driver.stop_driving()
    return ""


@app.route("/change-mode", methods=["POST"])
def change_mode():
    data = request.get_json(silent=True)

    if "mode" in data:
        action_manager.append(data["mode"])

    return ""

@app.route("/accelerate-forward", methods=["POST"])
def accelerate_forward():
    driver.accelerate(1)
    return ""

@app.route("/accelerate-backward", methods=["POST"])
def accelerate_backward():
    driver.accelerate(-1)
    return ""

@app.route("/steer-left", methods=["POST"])
def steer_left():
    driver.steer(-1)
    return ""

@app.route("/steer-right", methods=["POST"])
def steer_right():
    driver.steer(1)
    return ""
