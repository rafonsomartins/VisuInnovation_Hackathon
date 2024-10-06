from flask import Flask, request, jsonify
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

app = Flask(__name__)

vehicle = connect('127.0.0.1:14550', wait_ready=True)

@app.route('/move_drone', methods=['POST'])
def move_drone():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']

	# Ensure the vehicle is in GUIDED mode and armed
	if vehicle.mode.name != "GUIDED":
		vehicle.mode = VehicleMode("GUIDED")
		while not vehicle.mode.name == "GUIDED":
			time.sleep(1)

	vehicle.armed = True
	while not vehicle.armed:
		time.sleep(1)

	# Takeoff to 10 meters
	vehicle.simple_takeoff(10)
	while True:
		print(f"Current Altitude: {vehicle.location.global_relative_frame.alt}")
		if vehicle.location.global_relative_frame.alt >= 9.5:
			break
		time.sleep(1)

	# Create target location and send the drone there
	target_location = LocationGlobalRelative(latitude, longitude, 10)
	vehicle.simple_goto(target_location)

	while vehicle.mode.name == "GUIDED":
		current_location = vehicle.location.global_frame
		distance = get_distance_metres(current_location, target_location)
		altitude = vehicle.location.global_relative_frame.alt
		print(f"Current Altitude: {altitude}, Distance to target: {distance}")

		# Check if the drone is too low or has hit the ground
		if altitude < 1:
			return jsonify({'status': 'Drone has hit the ground.'}), 200

		if distance < 1:  # Close to target location
			break
		time.sleep(1)

	# Initiate landing
	vehicle.mode = VehicleMode("LAND")
	while vehicle.armed:
		time.sleep(1)

	if vehicle.mode.name != "GUIDED":
		vehicle.mode = VehicleMode("GUIDED")
		while not vehicle.mode.name == "GUIDED":
			time.sleep(1)

	vehicle.armed = True
	while not vehicle.armed:
		time.sleep(1)

	vehicle.simple_takeoff(10)
	while True:
		print(f"Current Altitude: {vehicle.location.global_relative_frame.alt}")
		if vehicle.location.global_relative_frame.alt >= 9.5:
			break
		time.sleep(1)

	# Optional: Return to launch
	vehicle.mode = VehicleMode("RTL")

	return jsonify({'status': 'Drone successfully reached the destination and is landing.'}), 200

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
