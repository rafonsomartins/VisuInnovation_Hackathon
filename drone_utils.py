import os
import json
from globals import BASE_COORDINATES_FILE, vehicle
from shapely.geometry import Polygon, Point
import numpy as np

def create_grid_within_polygon(boundary_coords, grid_resolution, altitude):
	polygon = Polygon(boundary_coords)

	# Determine the bounding box for the polygon
	min_lat = min(coord[0] for coord in boundary_coords)
	max_lat = max(coord[0] for coord in boundary_coords)
	min_lon = min(coord[1] for coord in boundary_coords)
	max_lon = max(coord[1] for coord in boundary_coords)

	# Create a grid of points covering the bounding box
	lat_points = np.arange(min_lat, max_lat, grid_resolution)
	lon_points = np.arange(min_lon, max_lon, grid_resolution)

	# Check each grid point to see if it's inside the polygon
	waypoints = []
	for lat in lat_points:
		for lon in lon_points:
			point = Point(lat, lon)
			if polygon.contains(point):
				waypoints.append({'latitude': lat, 'longitude': lon, 'altitude': altitude})

	return waypoints

def find_best_landing_spot(lidar_log_file):
    best_spot = None
    min_variation = float('inf')

    with open(lidar_log_file, 'r') as file:
        next(file)  # Skip header
        for line in file:
            lat, lon, alt, lidar_distance = line.strip().split(',')
            lidar_distance = float(lidar_distance)
            
            # Using variation as a placeholder for flatness criteria
            variation = abs(lidar_distance - 1.0)  # Ideal distance around 1 meter (adjust as needed)
            
            if variation < min_variation:
                min_variation = variation
                best_spot = (float(lat), float(lon), float(alt))

    print(f"Best landing spot found at: {best_spot}")
    return best_spot

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

def battery_check_distance(waypoints, vehicle_battery):
	distance = 0
	for i in range(len(waypoints) - 1):
		distance += get_distance_metres(waypoints[i], waypoints[i + 1])
	nedded_battery = (vehicle_battery * 100) / 7.5
	nedded_battery *= 0.9
	if nedded_battery >= vehicle_battery:
		return 1
	else:
		print("Not enough battery!")
		return 0
