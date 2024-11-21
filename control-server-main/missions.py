from drone_control import my_goto, STD_SPEED, TAKEOFF_ALTITUDE, land_drone, return_home, run_route, populate_lidar
import globals
from drone_utils import load_plan_file, get_mission_back, create_grid_within_polygon, find_best_landing_spot

def delivery(latitude, longitude):
    my_goto(latitude, longitude, TAKEOFF_ALTITUDE, STD_SPEED)
    land_drone()
    return_home()

def run_mission(plan_file_name, plan_back):
    waypoints = load_plan_file(plan_file_name)
    waypoints_back = get_mission_back(plan_back, waypoints)

    waypoints.append(waypoints[-1])

    run_route(globals.vehicle, waypoints)

    globals.guest["is_return_confirm_allowed"] = True
    globals.return_mission_event.clear()
    print("Waiting for confirmation to start return route...")
    globals.return_mission_event.wait()
    globals.guest["is_return_confirm_allowed"] = False

    run_route(globals.vehicle, waypoints_back)

def auto_land_if_low_battery(vehicle):
    battery_level = globals.vehicle.battery.level
    if battery_level < 20:  # Example threshold, adjust as needed
        print("Battery low. Initiating auto-land sequence...")

        # Define an area around the current location to scan
        current_location = globals.vehicle.location.global_relative_frame
        boundary_coords = [
            (current_location.lat - 0.00001, current_location.lon - 0.00001),
            (current_location.lat + 0.00001, current_location.lon - 0.00001),
            (current_location.lat + 0.00001, current_location.lon + 0.00001),
            (current_location.lat - 0.00001, current_location.lon + 0.00001),
        ]

        # Create grid and populate LiDAR data
        grid_resolution = 0.000005  # Smaller grid resolution for more precise landing data
        altitude = current_location.alt
        waypoints = create_grid_within_polygon(boundary_coords, grid_resolution, altitude)

        lidar_log_file = populate_lidar(globals.vehicle, altitude, waypoints)

        # Analyze the LiDAR data to find the best spot
        best_spot = find_best_landing_spot(lidar_log_file)

        if best_spot:
            lat, lon, alt = best_spot
            print("Landing at optimal location based on LiDAR data...")
            my_goto(lat, lon, alt, 5)  # Slowly approach the landing site
            land_drone(globals.vehicle)
        else:
            print("No suitable landing spot found. Returning to home...")
            return_home(globals.vehicle)
