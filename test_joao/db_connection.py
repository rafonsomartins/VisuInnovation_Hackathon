import psycopg2
import configparser

def get_db_config(config_file="./config/db_config.ini"):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['postgresql']

def get_db_connection():
    config = get_db_config()
    return psycopg2.connect(
        host=config['host'],
        port=config['port'],
        user=config['user'],
        password=config['password'],
        database=config['database']
    )
