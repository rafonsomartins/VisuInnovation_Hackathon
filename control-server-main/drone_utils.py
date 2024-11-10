import os
import json
from globals import BASE_COORDINATES_FILE, vehicle

def load_base_coordinates():
	if os.path.exists(BASE_COORDINATES_FILE):
		with open(BASE_COORDINATES_FILE, 'r') as file:
			return json.load(file)
	else:
		return None

def save_base_coordinates(latitude, longitude):
	home_coords = {"latitude": latitude, "longitude": longitude}
	with open(BASE_COORDINATES_FILE, 'w') as file:
		json.dump(home_coords, file)

def get_distance_metres(loc1, loc2):
	""" Returns the ground distance in meters between two location objects. """
	dlat = loc2.lat - loc1.lat
	dlong = loc2.lon - loc1.lon
	return ((dlat ** 2) + (dlong ** 2)) ** 0.5 * 111320

def parse_waypoints(file_path):
	waypoints = []
	with open(file_path, 'r') as file:
		for line in file:
			# Skip the first line and any empty lines
			if line.startswith("QGC") or line.strip() == "":
				continue
			parts = line.split()
			latitude = float(parts[8])
			longitude = float(parts[9])
			altitude = float(parts[10])
			waypoints.append({
				'latitude': latitude,
				'longitude': longitude,
				'altitude': altitude
			})
	return waypoints

def load_plan_file(plan_file_path):
	with open(plan_file_path, 'r') as file:
		plan_data = json.load(file)

	waypoints = []
	for item in plan_data['mission']['items']:
		if item['command'] == 16:  # MAV_CMD_NAV_WAYPOINT
			lat = item['params'][4]
			lon = item['params'][5]
			alt = item['params'][6]
			waypoints.append((lat, lon, alt))

	return waypoints

def get_mission_back(plan_back, waypoints):
	if not plan_back:
			waypoints_back = list(reversed(waypoints))
			home_coords = load_base_coordinates()
			home_coords_tuple = (home_coords['latitude'], home_coords['longitude'], waypoints[-1][2])

			waypoints_back = waypoints_back[1:]
			waypoints_back.append(home_coords_tuple)
			waypoints_back.append(home_coords_tuple)
			waypoints_back.append(home_coords_tuple)
	else:
		waypoints_back = load_plan_file(plan_back)
		waypoints_back.append(waypoints_back[-1])
	return waypoints_back

def check_and_create_home_coords():
	if not os.path.exists(BASE_COORDINATES_FILE) and not vehicle.armed:
		# Retrieve current location from the drone
		location = vehicle.location.global_frame
		home_coords = {
			"latitude": location.lat,
			"longitude": location.lon,
			"altitude": location.alt
		}

		# Save coordinates to the home_coords file
		with open(BASE_COORDINATES_FILE, 'w') as file:
			json.dump(home_coords, file)
