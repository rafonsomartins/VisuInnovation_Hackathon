from flask import Flask
from dronekit import connect
import threading

BASE_ROUTE_PATH = './.Drone_info/.routes'
BASE_COORDINATES_FILE = "./.Drone_info/base_coordinates.txt"
LiDAR_FILE = "./.Drone_info/lidar_logs.txt"

app = Flask(__name__)

vehicle = connect('127.0.0.1:14550', wait_ready=True)

return_mission_event = threading.Event()

guest = {"is_return_confirm_allowed": False, "id": 0}
