from drone_control import my_goto, STD_SPEED, TAKEOFF_ALTITUDE, land_drone, return_home, run_route
from sensors_utils import get_lidar_data
from globals import vehicle, return_mission_event, is_return_confirm_allowed
from drone_utils import load_plan_file, get_mission_back
import os
import time

def delivery(latitude, longitude):
	my_goto(latitude, longitude, TAKEOFF_ALTITUDE, STD_SPEED)
	land_drone()
	return_home()

def run_mission(plan_file_name, plan_back):
	global is_return_confirm_allowed
	waypoints = load_plan_file(plan_file_name)
	waypoints_back = get_mission_back(plan_back, waypoints)

	waypoints.append(waypoints[-1])

	run_route(vehicle, waypoints)

	is_return_confirm_allowed = True
	return_mission_event.clear()
	print("Waiting for confirmation to start return route...")
	return_mission_event.wait()
	is_return_confirm_allowed = False

	run_route(vehicle, waypoints_back)
