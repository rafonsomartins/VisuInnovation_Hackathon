from dronekit import VehicleMode, LocationGlobalRelative, Command
import time
import os
from drone_utils import get_distance_metres, load_base_coordinates
from globals import vehicle, LiDAR_FILE
from pymavlink import mavutil
from sensors_utils import simulate_lidar

TAKEOFF_ALTITUDE = 10
CLOSE_ENOUGH_DIST = 1
STD_SPEED = 60

def set_mode(str, timeout=10):
	vehicle.mode = VehicleMode(str)
	start_time = time.time()
	while not vehicle.mode.name == str and time.time() - start_time < timeout:
		time.sleep(1)
	if not vehicle.mode.name == str:
		raise TimeoutError(f"Failed to set vehicle mode to {str}")

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

def upload_mission(vehicle, waypoints):
	cmds = vehicle.commands
	cmds.clear()

	# Adicionar comando de decolagem
	cmds.add(Command(
		0, 0, 0,
		mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
		mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
		0, 0, 0, 0, 0, 0,
		0, 0, 10))  # 10 metros de altitude

	# Adicionar os waypoints extraídos do arquivo
	for lat, lon, alt in waypoints:
		cmds.add(Command(
			0, 0, 0,
			mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
			mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
			0, 0, 0, 0, 0, 0,
			lat, lon, alt))

	# Enviar missão
	cmds.upload()

def run_route(vehicle, waypoints):
	arm_and_takeoff(10)
	upload_mission(vehicle, waypoints)

	set_mode("AUTO", 15)

	while vehicle.commands.next < len(waypoints):
		time.sleep(1)
	
	# Pause briefly before initiating landing
	time.sleep(0.5)
	land_drone()

def populate_lidar(vehicle, altitude, waypoints):
	with open(LiDAR_FILE, 'w') as log_file:
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
				lidar_data = simulate_lidar()
				i += 1
				time.sleep(1)
			if lidar_data is not None:
				log_file.write(f"{latitude},{longitude},{altitude},{lidar_data}\n")
			else:
				log_file.write(f"{latitude},{longitude},{altitude},No data\n")

	return LiDAR_FILE
