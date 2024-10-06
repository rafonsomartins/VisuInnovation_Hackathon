from flask import Flask
from dronekit import connect

app = Flask(__name__)
vehicle = connect('127.0.0.1:14550', wait_ready=True)
