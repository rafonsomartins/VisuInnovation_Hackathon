import os
import json
from shapely.geometry import Polygon, Point
import numpy as np

base_coordinates_file = "/home/ralves-e/.Drone_info/base_coordinates.txt"

def load_base_coordinates():
    if os.path.exists(base_coordinates_file):
        with open(base_coordinates_file, 'r') as file:
            return json.load(file)
    else:
        return None

def save_base_coordinates(latitude, longitude):
    home_coords = {"latitude": latitude, "longitude": longitude}
    with open(base_coordinates_file, 'w') as file:
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