from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
import os

import psycopg2
from psycopg2 import sql
from datetime import datetime, timezone


class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = os.getenv("HOST_ENV", 'http://159.203.50.162')#"http://159.203.50.162"  # Setup your host here
        self.TOKEN = os.getenv('HOST_TOKEN', '3f0a57e541e13a3b6549')#"3f0a57e541e13a3b6549"  # Setup your token here
        self.T_MAX = os.getenv('OXYGEN_T_MAX', 60)#60  # Setup your max temperature here
        self.T_MIN = os.getenv('OXYGEN_T_MIN', 20)#20  # Setup your min temperature here.
        self.DATABASE_URL = os.getenv('OXYGEN_DATABASE_URL', 'postgresql://user02eq12:E84YDXF2l5P4FkFG@157.230.69.113:5432/db02eq12')  # Setup your database here

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""

        DB_CONNECTION_PARAMS = {
            'dbname': 'db02eq12',
            'user': 'user02eq12',
            'password': 'E84YDXF2l5P4FkFG',
            'host': '157.230.69.113',
            'port': '5432',
        }
        table_name = 'hvac_events'
        action = "None"
        if float(temperature) >= float(self.T_MAX):
            action = "TurnOnAc"
        elif float(temperature) <= float(self.T_MIN):
            action = "TurnOnHeater"

        try:
            # Connect to the PostgreSQL database
            connection = psycopg2.connect(**DB_CONNECTION_PARAMS)
            cursor = connection.cursor()

            
            # Insert HVAC event into the hvac_events table
            cursor.execute(
            f"INSERT INTO {table_name} (timestamp_event, temperature, event_type) VALUES (%s, %s, %s)",
            (timestamp, temperature, action),
            )

            # Commit the changes and close the connection
            connection.commit()
            cursor.close()
            connection.close()
            
        except psycopg2.Error as e:
            print(f"Error saving HVAC event to the database: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    app = App()
    app.start()
