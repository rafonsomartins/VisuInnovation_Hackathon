from flask import request, jsonify
from missions import delivery, run_mission, auto_land_if_low_battery
from drone_utils import save_base_coordinates, parse_waypoints
import globals
import os
from drone_control import my_goto
import db_utils

@globals.app.route('/Auto-landing_test', methods=['POST'])
def	test_auto_landing():
	my_goto(-35.362387, 149.168299, 10, 10)
	auto_land_if_low_battery()

@globals.app.route('/set_home', methods=['POST'])
def set_home():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']
	save_base_coordinates(latitude, longitude)
	return jsonify({'status': 'Home coordinates updated successfully'}), 200

@globals.app.route('/import_mission', methods=['POST'])
def import_mission():
	# Check if the post request has the file part
	if 'waypoints_file' not in request.files:
		return jsonify({'error': 'No file part'}), 400
	
	file = request.files['waypoints_file']
	
	# If the user does not select a file
	if file.filename == '':
		return jsonify({'error': 'No selected file'}), 400
	
	# Save the file to a temporary location
	file_path = os.path.join(globals.BASE_ROUTE_PATH, file.filename)
	file.save(file_path)
	
	# Parse the waypoints from the file
	waypoints = parse_waypoints(file_path)
	
	return jsonify({
		'status': 'Mission uploaded successfully',
		'waypoints': waypoints
	}), 200

@globals.app.route('/simple_delivery', methods=['POST'])
def simple_delivery():
	data = request.get_json()
	if 'latitude' not in data or 'longitude' not in data:
		return jsonify({'error': 'Please provide latitude and longitude in the request body'}), 400

	latitude = data['latitude']
	longitude = data['longitude']

	delivery(latitude, longitude)
	return jsonify({'status': 'Mission ended'}), 200

@globals.app.route('/check_return_status', methods=['POST'])
def check_return_status():
	data = request.get_json()
	guest_id = data.get('guest_id')
	if not guest_id:
		return jsonify({"error": "Guest_id mandatory!"}), 400
	if guest_id != globals.guest["id"]:
		return jsonify({"return_confirm_allowed": False}), 200 
	return jsonify({"return_confirm_allowed": globals.guest["is_return_confirm_allowed"]}), 200

@globals.app.route('/confirm_return', methods=['POST'])
def confirm_return():
	data = request.get_json()
	guest_id = data.get('guest_id')

	if not guest_id:
		return jsonify({"error": "Guest_id mandatory!"}), 400

	if not globals.guest["is_return_confirm_allowed"] or guest_id != globals.guest["id"]:
		return jsonify({"error": "Return confirmation not allowed yet."}), 400

	globals.return_mission_event.set()
	return jsonify({"message": "Return route confirmed, drone will proceed back."}), 200

@globals.app.route('/run_mission', methods=['POST'])
def run_mission_endpoint():
	data = request.get_json()
	plan_file_name = data.get('plan_file_name')
	plan_back = data.get('plan_back')
	globals.guest["id"] = data.get('guest_id')
	globals.guest["user_id"] = get_user_id(data.get('username'))

	plan_file_name = os.path.join(globals.BASE_ROUTE_PATH, plan_file_name)
	plan_back = os.path.join(globals.BASE_ROUTE_PATH, plan_back) if plan_back else None

	if not plan_file_name:
		return jsonify({"error": "plan_file_name is required"}), 400
	try:
		run_mission(plan_file_name, plan_back)
		return jsonify({"message": "Mission ended successfully!"}), 200
	except Exception as e:
		return jsonify({"error": str(e)}), 500

@globals.app.route('/login', methods=['POST'])
def login():
	data = request.get_json()
	user = data.get('username')
	password = data.get('password')

	role = password_verificator(user, password)
	if not role:
		return jsonify({"error": "User not found"}), 400
	elif role == 1:
		return jonify({"error": "Password incorrect!"}), 400
	else
		return jonify({f"role: {role}"}), 200

@globals.app.route('/create_db', methods=['POST']) #Just use this route manually when the database is not created
	def create_db():
    db_config = get_db_config()
    
    db_utils.create_database()
    
    return "Database and tables created successfully!"
if __name__ == '__main__':
	globals.app.run(host='0.0.0.0', port=14459)

