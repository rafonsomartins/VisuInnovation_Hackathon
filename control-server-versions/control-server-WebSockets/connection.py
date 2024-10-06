from flask import Flask
from flask_socketio import SocketIO
from dronekit import connect

app = Flask(__name__)
socketio = SocketIO(app)
vehicle = connect('127.0.0.1:14550', wait_ready=True)