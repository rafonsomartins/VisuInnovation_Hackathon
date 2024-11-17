from flask import request, jsonify
from missions import delivery, run_mission, auto_land_if_low_battery
from drone_utils import save_base_coordinates, parse_waypoints
from globals import app, return_mission_event, is_return_confirm_allowed, BASE_ROUTE_PATH
import os
from drone_control import my_goto

@app.route('/Auto-landing_test', methods=['POST'])
def	test_auto_landing():
	my_goto(-35.362387, 149.168299, 10, 10)
	auto_land_if_low_battery()

@app.route('/set_home', methods=['POST'])
def set_home():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']
	save_base_coordinates(latitude, longitude)
	return jsonify({'status': 'Home coordinates updated successfully'}), 200

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
	file_path = os.path.join(BASE_ROUTE_PATH, file.filename)
	file.save(file_path)
	
	# Parse the waypoints from the file
	waypoints = parse_waypoints(file_path)
	
	return jsonify({
		'status': 'Mission uploaded successfully',
		'waypoints': waypoints
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

@app.route('/check_return_status', methods=['GET'])
def check_return_status():
	global is_return_confirm_allowed
	return jsonify({"return_confirm_allowed": is_return_confirm_allowed}), 200

@app.route('/confirm_return', methods=['POST'])
def confirm_return():
	global is_return_confirm_allowed
	if not is_return_confirm_allowed:
		return jsonify({"error": "Return confirmation not allowed yet."}), 400

	# Signal to run the return route by setting the event
	is_return_confirm_allowed = False  # Reset the confirmation allowance
	return_mission_event.set()
	return jsonify({"message": "Return route confirmed, drone will proceed back."}), 200

@app.route('/run_mission', methods=['POST'])
def run_mission_endpoint():
	data = request.get_json()
	plan_file_name = data.get('plan_file_name')
	plan_back = data.get('plan_back')

	plan_file_name = os.path.join(BASE_ROUTE_PATH, plan_file_name)
	plan_back = os.path.join(BASE_ROUTE_PATH, plan_back) if plan_back else None

	if not plan_file_name:
		return jsonify({"error": "plan_file_name is required"}), 400
	try:
		run_mission(plan_file_name, plan_back)
		return jsonify({"message": "Mission ended successfully!"}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=1559)
