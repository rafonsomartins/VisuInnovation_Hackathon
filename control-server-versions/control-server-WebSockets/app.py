from flask import request, jsonify
from drone_control import delivery
from utils import save_base_coordinates
from connection import app, socketio, vehicle

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

@app.route('/delivery', methods=['POST'])
def delivery_route():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']
	
	delivery(latitude, longitude)
	return jsonify({'status': 'Mission started'}), 200

if __name__ == '__main__':
	socketio.run(app, host='0.0.0.0', port=5000)
