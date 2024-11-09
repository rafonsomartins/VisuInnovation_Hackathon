from drone_control import my_goto, STD_SPEED, TAKEOFF_ALTITUDE, land_drone, return_home, run_route
from sensors_utils import get_lidar_data
import os
import time
from connection import vehicle
from drone_utils import load_plan_file, get_mission_back

def mission(waypoints):
	for waypoint in waypoints:
		latitude = waypoint['latitude']
		longitude = waypoint['longitude']
		altitude = waypoint['altitude']

		my_goto(latitude, longitude, altitude, STD_SPEED)

	for waypoint in reversed(waypoints):
		latitude = waypoint['latitude']
		longitude = waypoint['longitude']
		altitude = waypoint['altitude']

		my_goto(latitude, longitude, altitude, STD_SPEED)

def delivery(latitude, longitude):
	my_goto(latitude, longitude, TAKEOFF_ALTITUDE, STD_SPEED)
	land_drone()
	return_home()

def populate_lidar(vehicle, altitude, waypoints):
	lidar_log_file = os.path.join("/tmp", "lidar_data_log.csv")
	with open(lidar_log_file, 'w') as log_file:
		log_file.write("Latitude,Longitude,Altitude,LiDAR Distance (m)\n")

		for waypoint in waypoints:
			latitude = waypoint['latitude']
			longitude = waypoint['longitude']
			altitude = waypoint['altitude']

			# Fly to the waypoint
			my_goto(latitude, longitude, altitude, 10)  # Speed set to 10

			i = 0
			lidar_data = None
			while lidar_data == None and i < 2:
				lidar_data = get_lidar_data(vehicle)
				i += 1
				time.sleep(1)
			if lidar_data is not None:
				log_file.write(f"{latitude},{longitude},{altitude},{lidar_data}\n")
			else:
				log_file.write(f"{latitude},{longitude},{altitude},No data\n")
			print(f"lidar data: {lidar_data}")
	
	return_home()

	return lidar_log_file

def run_mission(plan_file_name, plan_back):
	waypoints = load_plan_file(plan_file_name)
	waypoints_back = get_mission_back(plan_back, waypoints)

	waypoints.append(waypoints[-1])

	run_route(vehicle, waypoints)
	time.sleep(1)
	run_route(vehicle, waypoints_back)
