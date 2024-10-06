from flask import Flask, request, jsonify
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import json
import os

TAKEOFF_ALTITUDE = 10
CLOSE_ENOUGH_DIST = 1
STD_SPEED = 3

app = Flask(__name__)

base_coordinates_file = "/home/ralves-e/.Drone_info/base_coordinates.txt"
vehicle = connect('127.0.0.1:14550', wait_ready=True)

def load_base_coordinates():
	""" Load home coordinates from the file """
	if os.path.exists(base_coordinates_file):
		with open(base_coordinates_file, 'r') as file:
			return json.load(file)
	else:
		return None

def save_base_coordinates(latitude, longitude):
	""" Save home coordinates to the file """
	home_coords = {"latitude": latitude, "longitude": longitude}
	with open(base_coordinates_file, 'w') as file:
		json.dump(home_coords, file)

def set_mode(str):
	vehicle.mode = VehicleMode(str)
	while not vehicle.mode.name == str:
		time.sleep(1)

def arm_and_takeoff(altitude):
	""" Arms vehicle and fly to a target altitude """
	set_mode("GUIDED")
	vehicle.armed = True
	while not vehicle.armed:
		time.sleep(1)
	vehicle.simple_takeoff(altitude)
	while True:
		print(f"Current Altitude: {vehicle.location.global_relative_frame.alt}")
		if vehicle.location.global_relative_frame.alt >= altitude * 0.95:
			break
		time.sleep(1)

def my_goto(latitude, longitude, altitude, groundspeed):
	if not vehicle.location.global_relative_frame.alt > 1:
		arm_and_takeoff(altitude)
	target_location = LocationGlobalRelative(latitude, longitude, altitude)
	vehicle.simple_goto(target_location, groundspeed=groundspeed)
	while vehicle.mode.name == "GUIDED":
		current_location = vehicle.location.global_frame
		distance = get_distance_metres(current_location, target_location)
		altitude = vehicle.location.global_relative_frame.alt
		print(f"Current Altitude: {altitude}, Distance to target: {distance}")
		if altitude < 1:
			return jsonify({'status': 'Drone has hit the ground.'}), 200
		if distance < 1:
			break
		time.sleep(1)

def land_drone():
	set_mode("LAND")
	while vehicle.armed == True:
		time.sleep(1)

@app.route('/set_home', methods=['POST'])
def set_home():
	""" Set new home coordinates and save to file """
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']
	save_base_coordinates(latitude, longitude)
	return jsonify({'status': 'Home coordinates updated successfully'}), 200

@app.route('/delievery', methods=['POST'])
def delievery():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']

	# Load and print the saved home coordinates
	home_coords = load_base_coordinates()
	if home_coords:
		print(f"Original home location loaded: {home_coords}")
	else:
		home_coords = {"latitude": vehicle.location.global_frame.lat, "longitude": vehicle.location.global_frame.lon}
		save_base_coordinates(home_coords['latitude'], home_coords['longitude'])
		print(f"Home location saved: {home_coords}")
	my_goto(latitude, longitude, TAKEOFF_ALTITUDE, STD_SPEED)

	# Landing -- package release simulation
	land_drone()

	my_goto(home_coords['latitude'], home_coords['longitude'], TAKEOFF_ALTITUDE, STD_SPEED)

	land_drone()

	return jsonify({'status': 'Drone successfully delievered the package, came back and now is landing.'}), 200

def get_distance_metres(loc1, loc2):
	""" Returns the ground distance in meters between two location objects. """
	dlat = loc2.lat - loc1.lat
	dlong = loc2.lon - loc1.lon
	return ((dlat ** 2) + (dlong ** 2)) ** 0.5 * 111320

@app.route('/status', methods=['GET'])
def status():
	""" Return the current status of the drone """
	return jsonify({
		'mode': vehicle.mode.name,
		'armed': vehicle.armed,
		'altitude': vehicle.location.global_relative_frame.alt,
		'location': {
			'lat': vehicle.location.global_frame.lat,
			'lon': vehicle.location.global_frame.lon,
			'alt': vehicle.location.global_frame.alt
		}
	}), 200

if __name__ == '__main__':
	try:
		app.run(host='0.0.0.0', port=5000)
	except KeyboardInterrupt:
		vehicle.close()
