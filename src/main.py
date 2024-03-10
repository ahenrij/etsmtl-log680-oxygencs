import os
from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
import psycopg2


class App:
    def __init__(self):
        self._hub_connection = None
        self._db_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = os.environ.get("HOST")  # host
        self.TOKEN = os.environ.get("TOKEN")  # token
        self.T_MAX = os.environ.get("T_MAX")  # max temperature
        self.T_MIN = os.environ.get("T_MIN")  # min temperature
        self.DATABASE_URL = os.environ.get("DATABASE_URL")  # database url
        self.DATABASE_USER = os.environ.get("DATABASE_USER")  # database user
        self.DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")  # database password
        self.DATABASE_NAME = os.environ.get("DATABASE_NAME")  # database name

    def __del__(self):
        if self._hub_connection is not None:
            self._hub_connection.stop()
        if self._db_connection is not None:
            self._db_connection.close()

    def start(self):
        """Start DB."""
        self._db_connection = self.connect_to_database()
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
        try:
            # To implement
            if self._db_connection is not None:
                action = None
                if float(temperature) >= float(self.T_MAX):
                    action = "TurnOnAc"
                elif float(temperature) <= float(self.T_MIN):
                    action = "TurnOnHeater"
                cur = self._db_connection.cursor()
                cur.execute(
                    "INSERT INTO sensor_data (timestamp, temperature, action) VALUES (%s, %s, %s)",
                    (timestamp, temperature, action),
                )
                self._db_connection.commit()
                cur.close()
            else:
                print("No database connection available.")
        except (Exception, psycopg2.DatabaseError) as e:
            print(f"An error occurred: {e}")
            pass

    def connect_to_database(self):
        """Connect to the database."""
        try:
            conn = psycopg2.connect(
                host=self.DATABASE_URL,
                database=self.DATABASE_NAME,
                user=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
            )
            # Create a cursor object
            cur = conn.cursor()

            print("You are connected to the database")
            cur.close()
            return conn
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None


if __name__ == "__main__":
    app = App()
    app.start()
