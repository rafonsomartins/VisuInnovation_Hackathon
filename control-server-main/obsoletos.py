# app.py:

# @app.route('/map_zone', methods=['POST'])
# def map_zone():
# 	data = request.get_json()

# 	if 'boundary_coords' not in data or 'altitude' not in data:
# 		return jsonify({'error': 'Please provide boundary coordinates and altitude'}), 400
	
# 	boundary_coords = data['boundary_coords']
# 	altitude = data['altitude']
# 	grid_resolution = data.get('grid_resolution', 0.0001)  # default resolution if not provided

# 	# Create grid of waypoints within the boundary
# 	waypoints = create_grid_within_polygon(boundary_coords, grid_resolution, altitude)

# 	if not waypoints:
# 		return jsonify({'error': 'No valid waypoints generated within the boundary'}), 400

# 	lidar_log_file = populate_lidar(vehicle, altitude, waypoints)

# 	return jsonify({
# 		'status': 'Mapping completed successfully',
# 		'log_file': lidar_log_file
# 	}), 200

# @app.route('/start_mission', methods=['GET'])
# def start_mission(waypoints):
# 	mission(waypoints)
# 	return jsonify({
# 		'status': 'Mission done successfully'
# 	}), 200

# @app.route('/status', methods=['GET'])
# def status():
# 	""" Return the current status of the drone """
# 	return jsonify({
# 		'mode': vehicle.mode.name,
# 		'armed': vehicle.armed,
# 		'altitude': vehicle.location.global_relative_frame.alt,
# 		'location': {
# 			'lat': vehicle.location.global_frame.lat,
# 			'lon': vehicle.location.global_frame.lon,
# 			'alt': vehicle.location.global_frame.alt
# 		}
# 	}), 200

# @app.route('/test_failsafe', methods=['GET'])
# def low_battery():
# 	vehicle.parameters['FS_THR_ENABLE'] = 1
# 	vehicle.parameters['BATT_LOW_VOLT'] = 10.0
# 	vehicle.parameters['GPS_TYPE'] = 0 
# 	my_goto(-35.362387, 149.16839383, 10, 10)
# 	return jsonify({'status': 'Mission ended'}), 200



# mission.py:

# def mission(waypoints):
# 	for waypoint in waypoints:
# 		latitude = waypoint['latitude']
# 		longitude = waypoint['longitude']
# 		altitude = waypoint['altitude']

# 		my_goto(latitude, longitude, altitude, STD_SPEED)

# 	for waypoint in reversed(waypoints):
# 		latitude = waypoint['latitude']
# 		longitude = waypoint['longitude']
# 		altitude = waypoint['altitude']

# 		my_goto(latitude, longitude, altitude, STD_SPEED)

# def populate_lidar(vehicle, altitude, waypoints):
# 	lidar_log_file = os.path.join("/tmp", "lidar_data_log.csv")
# 	with open(lidar_log_file, 'w') as log_file:
# 		log_file.write("Latitude,Longitude,Altitude,LiDAR Distance (m)\n")

# 		for waypoint in waypoints:
# 			latitude = waypoint['latitude']
# 			longitude = waypoint['longitude']
# 			altitude = waypoint['altitude']

# 			# Fly to the waypoint
# 			my_goto(latitude, longitude, altitude, 10)  # Speed set to 10

# 			i = 0
# 			lidar_data = None
# 			while lidar_data == None and i < 2:
# 				lidar_data = get_lidar_data(vehicle)
# 				i += 1
# 				time.sleep(1)
# 			if lidar_data is not None:
# 				log_file.write(f"{latitude},{longitude},{altitude},{lidar_data}\n")
# 			else:
# 				log_file.write(f"{latitude},{longitude},{altitude},No data\n")
# 			print(f"lidar data: {lidar_data}")
	
# 	return_home()

# 	return lidar_log_file



# drone_utils.py:

# def create_grid_within_polygon(boundary_coords, grid_resolution, altitude):
# 	polygon = Polygon(boundary_coords)

# 	# Determine the bounding box for the polygon
# 	min_lat = min(coord[0] for coord in boundary_coords)
# 	max_lat = max(coord[0] for coord in boundary_coords)
# 	min_lon = min(coord[1] for coord in boundary_coords)
# 	max_lon = max(coord[1] for coord in boundary_coords)

# 	# Create a grid of points covering the bounding box
# 	lat_points = np.arange(min_lat, max_lat, grid_resolution)
# 	lon_points = np.arange(min_lon, max_lon, grid_resolution)

# 	# Check each grid point to see if it's inside the polygon
# 	waypoints = []
# 	for lat in lat_points:
# 		for lon in lon_points:
# 			point = Point(lat, lon)
# 			if polygon.contains(point):
# 				waypoints.append({'latitude': lat, 'longitude': lon, 'altitude': altitude})

# 	return waypoints
