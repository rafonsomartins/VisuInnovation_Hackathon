from dronekit import VehicleMode, LocationGlobalRelative
import time
from drone_utils import get_distance_metres, load_base_coordinates
from connection import vehicle

TAKEOFF_ALTITUDE = 10
CLOSE_ENOUGH_DIST = 1
STD_SPEED = 30

def set_mode(str):
	vehicle.mode = VehicleMode(str)
	while not vehicle.mode.name == str:
		time.sleep(1)

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

def my_goto(latitude, longitude, altitude, groundspeed):
	if vehicle.armed == False:
		arm_and_takeoff(altitude)
	target_location = LocationGlobalRelative(latitude, longitude, altitude)
	vehicle.simple_goto(target_location, groundspeed=groundspeed)

	while vehicle.mode.name == "GUIDED":
		current_location = vehicle.location.global_frame
		distance = get_distance_metres(current_location, target_location)
		if distance < 1:
			break
		time.sleep(1)

def land_drone():
	set_mode("LAND")
	while vehicle.armed:
		time.sleep(1)

def return_home():
	home_coords = load_base_coordinates()
	my_goto(home_coords['latitude'], home_coords['longitude'], TAKEOFF_ALTITUDE, STD_SPEED)
	land_drone()
