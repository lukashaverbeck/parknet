# TODO echte Daten ermitteln
# momentan werden die Daten zufällig generiert oder sind manuell gesetzt
# siehe get_data()

from flask import Flask, jsonify, render_template
import random
import webbrowser

app = Flask(__name__)


def open_interface(debug=False):
    """ runs the web interface and opens it in the browser

    Args:
        debug (bool, optional): Boolean whether to start the app in debug mode
    """
    
    ip_address = '127.0.0.1'
    port = '5000'
    webbrowser.open('http://' + ip_address + ':' + port)
    app.run(debug=debug)


@app.route("/")
@app.route("/Home")
def home():
    return render_template("Interface.html")


@app.route("/data")
def interface():
    return jsonify(get_data());


# TODO echte Daten ermitteln
def get_data():
    data = {
        'formation' : {
            'agents' : [
                { 'id' : 1, 'length' : 100 },
                { 'id' : 2, 'length' : 113 },
                { 'id' : 3, 'length' : 102 },
                { 'id' : 4, 'length' : 120 }
            ],
            'longest' : 188,
            'gap' : 13
        },
        'driver' : {
            'angle' : 0,
            'velocity' : 18,
            'mode' : 0,
            'is_recording' : False
        },
        'sensors' : {
            'front' : 80,
            'right' : 23,
            'back' : 13
        }
    }

    data['driver']['angle'] += random.randint(-2,2);
    data['driver']['velocity'] += random.randint(-2,2);

    if data['driver']['angle'] > 60:
        data['driver']['angle'] = 60

    if data['driver']['angle'] < -60:
        data['driver']['angle'] = -60

    if data['driver']['velocity'] > 20:
        data['driver']['velocity'] = 20

    if data['driver']['velocity'] < -10:
        data['driver']['velocity'] = -10

    data['sensors']['front'] += random.randint(-2,2);
    data['sensors']['right'] += random.randint(-2,2);
    data['sensors']['back'] += random.randint(-2,2);

    return data

open_interface()