from pymavlink import mavutil
import time
import random

# def lidar_callback(message):
# 	current_distance = message.current_distance / 100.0  # Convert from cm to meters
# 	return current_distance

# Assuming liDAR is integrated with ArduPilot
def get_lidar_data(vehicle):
	lidar_data = None

	# def capture_lidar_data(message):
	# 	nonlocal lidar_data  # Allow access to lidar_data from the outer scope
	# 	lidar_data = message.current_distance / 100.0  # Convert from cm to meters

	# vehicle.add_message_listener('HEIGHT_SENSOR', capture_lidar_data)

	# # Wait a moment for data to be received
	# time.sleep(1)

	# vehicle.remove_message_listener('HEIGHT_SENSOR', capture_lidar_data)
	lidar_data = vehicle.rangefinder.distance

	return lidar_data

def simulate_lidar():
    # Returns a simulated LiDAR distance in meters
    return round(random.uniform(0.5, 5.0), 2)
