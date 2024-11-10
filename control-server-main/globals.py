from flask import Flask
from dronekit import connect
import threading

BASE_ROUTE_PATH = './.Drone_info/.routes'
BASE_COORDINATES_FILE = "./.Drone_info/base_coordinates.txt"

app = Flask(__name__)

vehicle = connect('127.0.0.1:14550', wait_ready=True)

return_mission_event = threading.Event()
is_return_confirm_allowed = False
