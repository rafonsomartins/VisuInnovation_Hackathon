import argparse
import psycopg2
import configparser
import os
from datetime import datetime

def get_db_config(config_file="./config/db_config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['postgresql']

def create_tables():
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    conn.autocommit = True
    with conn.cursor() as cursor:
        print(f"Creating tables in database '{config['database']}'...\n")
        execute_sql_file(cursor, "./config/Migrations/01-SQL_Tables.sql")
        print("Tables created successfully.\n")

    conn.close()

def reset_constrains():
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    conn.autocommit = True
    with conn.cursor() as cursor:
        print(f"\nResetting constrains in database '{config['database']}'...\n")
        execute_sql_file(cursor, "./config/Migrations/02-SQL_Reset.sql")
        print("Constrains reset successfully.\n")
    conn.close()

def execute_sql_file(cursor, sql_file):
    if not os.path.isfile(sql_file):
        print(f"Error: SQL File '{sql_file}' does not exist.")
        return
    with open(sql_file, 'r') as file:
        sql = file.read()
    cursor.execute(sql)

struct = {
    int log_id,


}

def create_log_table(conn, mission_id):
    with conn.cursor() as cursor:
        try:
            query = f"CREATE TABLE logs.log_{mission_id} (LIKE logs.template INCLUDING ALL);"
            cursor.execute(query)
            print("YEYYY FUNCIONOU")
            conn.commit()
        except Exception as e:
            print(e)

def insert_mission(conn, drone_id, route_id, user_id):
    query = """
    INSERT INTO opeations.missions (drone_id, route_id, user_id)
    VALUES (%s, %s, %s)
    RETURNING id;
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (drone_id, route_id, user_id))
            mission_id = cursor.fetchone()[0]
            conn.commit()
            print(f"Mission inserted with the ID: {mission_id}")
            return mission_id
    except Exception as e:
        print(f"Failure: unable to insert mission: {e}")
        conn.rollback()
        return None

def innit_mission(conn, drone_id, route_id, user_id):
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    conn.autocommit = True
    mission_id = insert_mission(conn, drone_id, route_id, user_id)
    create_log_table(conn, mission_id)
    return mission_id

# TODO (Comment if testing for now)
def insert_status(mission_id, status):
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    conn.autocommit = True
    query = f"
    INSERT INTO logs.log_{mission_id}
    VALUES (%s)
    "
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (status))
            conn.commit()
            print(f"Status updated on mission {mission_id}")
            return mission_id
    except Exception as e:
        print(f"Failure: unable to update status: {e}")
        conn.rollback()
        return None

# INSERT TO quando recebemos um log (def inster_log_to_table(conn, log_name, infos = {estrutura dados SQL}))
def insert_log_table(data):
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    conn.autocommit = True
    mission_id = data['id']
    table_name = f"logs.log_{mission_id}"

    # Insert query with placeholders
    query = f"""
    INSERT INTO {table_name} (
        "mode", "armed", "altitude", "location_lat", "location_lon", "location_alt", 
        "velocity_x", "velocity_y", "velocity_z", "gps_fix_type", "gps_num_satellites", 
        "gps_satelites_visible", "gps_hdop", "attitude_roll", "attitude_yaw", "groundspeed", 
        "airspeed", "battery_voltage", "battery_current", "battery_level", "battery_remaining", 
        "rc_channel_1", "rc_channel_2", "rc_channel_3", "rc_channel_4", "rc_channel_5", 
        "rc_channel_6", "rc_channel_7", "rc_channel_8", "total_waypoints", "current_waypoint"
    ) 
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    """
    values = (
        data['mode'], data['armed'], data['altitude'], data['location_lat'], data['location_lon'], data['location_alt'],
        data['velocity_x'], data['velocity_y'], data['velocity_z'], data['gps_fix_type'], data['gps_num_satellites'],
        data['gps_satelites_visible'], data['gps_hdop'], data['attitude_roll'], data['attitude_yaw'], data['groundspeed'],
        data['airspeed'], data['battery_voltage'], data['battery_current'], data['battery_level'], data['battery_remaining'],
        data['rc_channel_1'], data['rc_channel_2'], data['rc_channel_3'], data['rc_channel_4'], data['rc_channel_5'],
        data['rc_channel_6'], data['rc_channel_7'], data['rc_channel_8'], data['total_waypoints'], data['current_waypoint'],
    )

    try:
        with conn.cursor() as cursor:
            # Execute the query with the data array as parameters
            cursor.execute(query, values)
            conn.commit()
            return True
    except Exception as e:
        print(f"Error inserting log: {e}")
        conn.rollback()
        return False
# SELECT FROM (conn, log_name, infos = {estrutura dados SQL})
def select_from_table(conn, log_name, infos=None):
    base_query = f"SELECT * FROM logs.{log_name}"

    if infos:
        conditions = ' AND '.join([f"{key} = %s" for key in infos.keys()])
        query = f"{base_query} WHERE {conditions}"
        params = list(infos.values()) 
    else:
        query = base_query
        params = []
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchal1()
            print(f"Selected data from table {log_name}: {result}")
            return result
    except Exception as e:
        print(f"Failure: unable to select data from {log_name}: {e}")
    
def main():
    parser = argparse.ArgumentParser(description="Database Management Script")
    parser.add_argument('command', choices=['create', 'reset', 'recreate', 'create_log'], help="Command to execute")
    config = get_db_config()
    conn = psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
    
    args = parser.parse_args()

    if args.command == 'create':
        try:
            create_tables()
        except:
            print("\nError: Did you reset the database before creating the tables? Use 'recreate' instead.\n")
    elif args.command == 'reset':
        reset_constrains()
    elif args.command == 'recreate':
        reset_constrains()
        create_tables()
    elif args.command == "create_log":
        create_log_table(conn, 1)

def password_verificator(username, password):
    query = "SELECT id, nickname, password FROM management.users WHERE nickname = %s"
    try:
        with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                if user is None:
                    return False
                elif password == user[2]
                    return user[4]
        return 1
    except Exception as e:
        print(f"Failure: unable to authenticate: {e}")

def get_user_id(username):
    query = "SELECT id FROM management.users WHERE nickname = %s"
    try:
        with conn.cursor() as cursor:
                cursor.execute(query, (username,))
                user = cursor.fetchone()
                if user is None:
                    return False
                else
                    return user[0]
    except Exception as e:
        print(f"Failure: unable to authenticate: {e}")
    

if __name__ == "__main__":
    main()
