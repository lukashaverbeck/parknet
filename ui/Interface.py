import sys
sys.path.append(sys.path[0][:-3])

from flask import Flask, request, jsonify, render_template
from vehicle import Agent
from vehicle.Agent import Agent

app = Flask(__name__)
agent = Agent()


@app.route("/")
@app.route("/UI")
def home():
    return render_template("UI.html")


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

def open_interface(debug=False):
    ip_address = '127.0.0.1'
    port = '5000'
    app.run(debug=debug)


open_interface(True)