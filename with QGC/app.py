from flask import request, jsonify
from drone_control import my_goto
from missions import delivery, mission, populate_lidar
from drone_utils import save_base_coordinates, parse_waypoints, create_grid_within_polygon
from connection import app, vehicle
import os

@app.route('/test_failsafe', methods=['GET'])
def low_battery():
	vehicle.parameters['FS_THR_ENABLE'] = 1 
	vehicle.parameters['BATT_LOW_VOLT'] = 10.0
	vehicle.parameters['GPS_TYPE'] = 0 
	my_goto(-35.362387, 149.16839383, 10, 10)
	return jsonify({'status': 'Mission ended'}), 200

@app.route('/set_home', methods=['POST'])
def set_home():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']
	save_base_coordinates(latitude, longitude)
	return jsonify({'status': 'Home coordinates updated successfully'}), 200

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

@app.route('/import_mission', methods=['POST'])
def import_mission():
	# Check if the post request has the file part
	if 'waypoints_file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	
	file = request.files['waypoints_file']
	
	# If the user does not select a file
	if file.filename == '':
		return jsonify({'error': 'No selected file'}), 400
	
	# Save the file to a temporary location
	file_path = os.path.join("/tmp", file.filename)
	file.save(file_path)
	
	# Parse the waypoints from the file
	waypoints = parse_waypoints(file_path)
	
	return jsonify({
		'status': 'Mission uploaded successfully',
		'waypoints': waypoints
	}), 200

@app.route('/start_mission', methods=['GET'])
def start_mission(waypoints):
	mission(waypoints)
	return jsonify({
		'status': 'Mission done successfully'
	}), 200

@app.route('/simple_delivery', methods=['POST'])
def simple_delivery():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']

	delivery(latitude, longitude)
	return jsonify({'status': 'Mission ended'}), 200

@app.route('/map_zone', methods=['POST'])
def map_zone():
	data = request.get_json()

	if 'boundary_coords' not in data or 'altitude' not in data:
		return jsonify({'error': 'Please provide boundary coordinates and altitude'}), 400
	
	boundary_coords = data['boundary_coords']
	altitude = data['altitude']
	grid_resolution = data.get('grid_resolution', 0.0001)  # default resolution if not provided

	# Create grid of waypoints within the boundary
	waypoints = create_grid_within_polygon(boundary_coords, grid_resolution, altitude)

	if not waypoints:
		return jsonify({'error': 'No valid waypoints generated within the boundary'}), 400

	lidar_log_file = populate_lidar(vehicle, altitude, waypoints)

	return jsonify({
		'status': 'Mapping completed successfully',
		'log_file': lidar_log_file
	}), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1559)
