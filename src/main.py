import json
import logging
import os
import time
import requests
import psycopg2.errors
from signalrcore.hub_connection_builder import HubConnectionBuilder
from src.crud import Crud, Table

class App:
    def __init__(self):
        """Setup environment variables and default values."""
        self._hub_connection = None
        self.host = os.getenv('HOST')
        self.token = os.getenv('TOKEN')

        self.ticks = int(os.getenv('TICKS', '1'))
        self.t_max = os.getenv('T_MAX', '25')
        self.t_min = os.getenv('T_MIN', '18')

        required_vars = ['HOST', 'TOKEN']
        self.crud_instance = Crud()
        missing_vars = [var for var in required_vars if os.getenv(var) is None]

        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

    def __del__(self):
        if self._hub_connection is not None:
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
            .with_url(f"{self.host}/SensorHub?token={self.token}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 5,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(
                f"||| An exception was thrown: {data['error']}"
            ))

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]  # Variable not used
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except KeyError as err:
            print(f"Error processing sensor data: {err}")

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if temperature >= float(self.t_max):
            self.send_action_to_hvac("TurnOnAc")
        elif temperature <= float(self.t_min):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.host}/api/hvac/{self.token}/{action}/{self.ticks}", timeout=10)
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            self.crud_instance.connect()
            self.crud_instance.insert_metric(Table.HVAC_EVENTS, timestamp, str(temperature))
            self.crud_instance.close_connection()
        except psycopg2.Error as e:
            print(f"Failed to save event to database: {e}")

if __name__ == "__main__":
    app = App()
    app.start()
