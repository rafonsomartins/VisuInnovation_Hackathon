from dronekit import VehicleMode, LocationGlobalRelative
import time
from utils import load_base_coordinates, get_distance_metres
from connection import vehicle, socketio

TAKEOFF_ALTITUDE = 10
CLOSE_ENOUGH_DIST = 1
STD_SPEED = 8

def set_mode(str):
	vehicle.mode = VehicleMode(str)
	while not vehicle.mode.name == str:
		time.sleep(1)

def arm_and_takeoff(altitude):
	set_mode("GUIDED")
	vehicle.armed = True
	while not vehicle.armed:
		time.sleep(1)
	vehicle.simple_takeoff(altitude)
	while True:
		if vehicle.location.global_relative_frame.alt >= altitude * 0.95:
			break
		time.sleep(1)

def my_goto(latitude, longitude, altitude, groundspeed):
	arm_and_takeoff(altitude)
	target_location = LocationGlobalRelative(latitude, longitude, altitude)
	vehicle.simple_goto(target_location, groundspeed=groundspeed)

	socketio.emit('status', {'message': f'Drone flying at {vehicle.location.global_frame.alt} meters of altitude'})
	while vehicle.mode.name == "GUIDED":
		current_location = vehicle.location.global_frame
		distance = get_distance_metres(current_location, target_location)
		if distance < 1:
			break
		time.sleep(1)

def land_drone():
	set_mode("LAND")
	while vehicle.armed:
		time.sleep(1)

def delivery(latitude, longitude):
	home_coords = load_base_coordinates()
	socketio.emit('status', {'message': 'Mission started'})
	my_goto(latitude, longitude, TAKEOFF_ALTITUDE, STD_SPEED)
	socketio.emit('status', {'message': f"Drone got to destination. Starting delivery."})
	land_drone()
	socketio.emit('status', {'message': f"Package delivered at 'latitude': {latitude}, 'longitude': {longitude}.\nDrone will now return to base."})
	my_goto(home_coords['latitude'], home_coords['longitude'], TAKEOFF_ALTITUDE, STD_SPEED)
	land_drone()
	socketio.emit('status', {'message': 'Landed at base'})
