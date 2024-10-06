from flask import Flask, request, jsonify
from dronekit import connect, VehicleMode, LocationGlobalRelative, set_mode
import time

app = Flask(__name__)
vehicle = connect('127.0.0.1:14550', wait_ready=True)

@app.route('/start_mission', methods=['POST'])
def start_mission():
    try:
        data = request.get_json()
        route_name = data.get('route_name')

        if not route_name:
            return jsonify({'error': 'No route name provided'}), 400

        # 1. Arm the drone
        arm_and_takeoff(10)  # Takeoff to 10 meters

        # 2. Execute the mission
        print(f"Executing mission: {route_name}")
        start_mission_by_name(route_name)

        return jsonify({'status': f'Mission {route_name} started successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

def start_mission_by_name(route_name):
    """
    Starts a predefined mission loaded in the vehicle based on route_name.
    """
    # Assuming that the missions are preloaded into the vehicle
    vehicle.commands.next = 0  # Reset mission to the first waypoint
    vehicle.mode = VehicleMode("AUTO")  # Start the mission

    while True:
        next_waypoint = vehicle.commands.next
        print(f"Executing waypoint {next_waypoint}")
        
        # Check if mission is complete
        if next_waypoint == 0:
            print(f"Mission {route_name} completed")
            break
        time.sleep(1)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
