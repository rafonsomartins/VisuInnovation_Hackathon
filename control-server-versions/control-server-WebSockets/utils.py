import os
import json

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