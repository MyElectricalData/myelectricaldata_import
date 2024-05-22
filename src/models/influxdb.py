"""This module contains the InfluxDB class for connecting to and interacting with InfluxDB."""
import datetime
import json
import logging
import sys

import influxdb_client
from dateutil.tz import tzlocal
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

from database.config import DatabaseConfig
from dependencies import separator, separator_warning, title

# from . import INFLUXDB


class InfluxDB:
    """Class for connecting to and interacting with InfluxDB."""

    class BatchingOptions:
        """Default configuration for InfluxDB batching options."""

        def __init__(self) -> None:
            """Initialize a new instance of the InfluxDB class.

            Parameters:
                batch_size (int): The number of data points to batch together before writing to InfluxDB.
                flush_interval (int): The time interval (in milliseconds) between flushing batches to InfluxDB.
                jitter_interval (int): The maximum random interval (in milliseconds) to add to the flush interval.
                retry_interval (int): The time interval (in milliseconds) between retry attempts when writing to InfluxDB fails.
                max_retry_time (str): The maximum total time (in milliseconds) to spend on retry attempts.
                max_retries (int): The maximum number of retry attempts when writing to InfluxDB fails.
                max_retry_delay (str): The maximum delay (in milliseconds) between retry attempts.
                exponential_base (int): The base value for exponential backoff when retrying.

            Returns:
                None
            """
            self.batch_size: int = 1000
            self.flush_interval: int = 1000
            self.jitter_interval: int = 0
            self.retry_interval: int = 5000
            self.max_retry_time: str = "180_000"
            self.max_retries: int = 5
            self.max_retry_delay: str = "125_000"
            self.exponential_base: int = 2

    class Config:
        """Default configuration for InfluxDB."""

        def __init__(self) -> None:
            """Initialize an instance of the InfluxDBConfig class.

            Attributes:
            - enable (bool): Indicates whether InfluxDB is enabled or not.
            - scheme (str): The scheme to use for connecting to InfluxDB (e.g., "http", "https").
            - hostname (str): The hostname of the InfluxDB server.
            - port (int): The port number to use for connecting to InfluxDB.
            - token (str): The authentication token for accessing InfluxDB.
            - org (str): The organization name in InfluxDB.
            - bucket (str): The bucket name in InfluxDB.
            - method (str): The method to use for writing data to InfluxDB (e.g., "SYNCHRONOUS", "BATCHING").
            """
            self.enable: bool = False
            self.scheme: str = "http"
            self.hostname: str = "localhost"
            self.port: int = 8086
            self.token: str = "my-token"
            self.org: str = "myorg"
            self.bucket: str = "mybucket"
            self.method: str = "SYNCHRONOUS"

    def __init__(
        self,
    ):
        self.influxdb = {}
        self.query_api = {}
        self.write_api = {}
        self.delete_api = {}
        self.buckets_api = {}
        self.retention = 0
        self.max_retention = None
        self.config = self.Config()
        self.config_batching = self.BatchingOptions()
        self.load_config()
        if self.config.enable:
            self.connect()
            self.get_list_retention_policies()
            if self.retention != 0:
                day = int(self.retention / 60 / 60 / 24)
                logging.warning(f"<!> ATTENTION, InfluxDB est configuré avec une durée de rétention de {day} jours.")
                logging.warning(
                    f"    Toutes les données supérieures à {day} jours ne seront jamais insérées dans celui-ci."
                )
            else:
                logging.warning(" => Aucune durée de rétention de données détectée.")

    def load_config(self):
        """Load the configuration for InfluxDB.

        This method loads the configuration values from the usage point and contract objects.
        """
        self.influxdb_config = json.loads(DatabaseConfig().get("influxdb").value)
        for key in self.config.__dict__:
            if key in self.influxdb_config:
                setattr(self.config, key, self.influxdb_config.get(key))

        if "batching" in self.influxdb_config:
            self.batching_options = self.influxdb_config.get("batching")
            for key in self.config_batching.__dict__:
                if key in self.batching_options:
                    setattr(self.config_batching, key, self.batching_options.get(key))

    def connect(self):
        """Connect to InfluxDB.

        This method establishes a connection to the InfluxDB database using the provided configuration.
        """
        separator()
        logging.info(f"Connect to InfluxDB {self.config.hostname}:{self.config.port}")
        date_utils.date_helper = DateHelper(timezone=tzlocal())
        self.influxdb = influxdb_client.InfluxDBClient(
            url=f"{self.config.scheme}://{self.config.hostname}:{self.config.port}",
            token=self.config.token,
            org=self.config.org,
            timeout="600000",
        )
        health = self.influxdb.health()
        if health.status == "pass":
            title("Connection success")
        else:
            logging.critical(
                """
Impossible de se connecter à la base influxdb.

Vous pouvez récupérer un exemple ici :
https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file
"""
            )
            sys.exit(1)

        title(f"Méthode d'importation : {self.config.method.upper()}")
        if self.config.method.upper() == "ASYNCHRONOUS":
            logging.warning(
                ' <!> ATTENTION, le mode d\'importation "ASYNCHRONOUS" est très consommateur de ressources système.'
            )
            self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
        elif self.config.method.upper() == "SYNCHRONOUS":
            self.write_api = self.influxdb.write_api(write_options=SYNCHRONOUS)
        else:
            self.write_api = self.influxdb.write_api(
                write_options=influxdb_client.WriteOptions(
                    batch_size=self.config_batching.batch_size,
                    flush_interval=self.config_batching.flush_interval,
                    jitter_interval=self.config_batching.jitter_interval,
                    retry_interval=self.config_batching.retry_interval,
                    max_retries=self.config_batching.max_retries,
                    max_retry_delay=self.config_batching.max_retry_delay,
                    exponential_base=self.config_batching.exponential_base,
                )
            )
        self.query_api = self.influxdb.query_api()
        self.delete_api = self.influxdb.delete_api()
        self.buckets_api = self.influxdb.buckets_api()
        self.get_list_retention_policies()

    def purge_influxdb(self):
        """Purge the InfluxDB database.

        This method wipes the InfluxDB database by deleting all data within specified measurement types.
        """
        separator_warning()
        logging.warning(f"Wipe influxdb database {self.config.hostname}:{self.config.port}")
        start = "1970-01-01T00:00:00Z"
        stop = datetime.datetime.utcnow()
        measurement = [
            "consumption",
            "production",
            "consumption_detail",
            "production_detail",
        ]
        for mesure in measurement:
            self.delete_api.delete(start, stop, f'_measurement="{mesure}"', self.config.bucket, org=self.config.org)
        logging.warning(" => Data reset")

    def get_list_retention_policies(self):
        """Get the list of retention policies.

        This method retrieves the list of retention policies for the InfluxDB database.
        """
        if self.config.org == "-":  # InfluxDB 1.8
            self.retention = 0
            self.max_retention = 0
            return
        else:
            buckets = self.buckets_api.find_buckets().buckets
            for bucket in buckets:
                if bucket.name == self.config.bucket:
                    self.retention = bucket.retention_rules[0].every_seconds
                    self.max_retention = datetime.datetime.now() - datetime.timedelta(seconds=self.retention)

    def get(self, start, end, measurement):
        """Retrieve data from the InfluxDB database.

        This method retrieves data from the specified measurement within the given time range.

        Args:
            start (str): Start time of the data range.
            end (str): End time of the data range.
            measurement (str): Name of the measurement to retrieve data from.

        Returns:
            list: List of data points retrieved from the database.
        """
        if self.config.org != "-":
            query = f"""
from(bucket: "{self.config.bucket}")
  |> range(start: {start}, stop: {end})
  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
"""
            logging.debug(query)
            output = self.query_api.query(query)
        else:
            # Skip for InfluxDB 1.8
            output = []
        return output

    def count(self, start, end, measurement):
        """Count the number of data points within a specified time range and measurement.

        Args:
            start (str): Start time of the data range.
            end (str): End time of the data range.
            measurement (str): Name of the measurement to count data points from.

        Returns:
            list: List of count values.
        """
        if self.config.org != "-":
            query = f"""
from(bucket: "{self.config.bucket}")
    |> range(start: {start}, stop: {end})
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> filter(fn: (r) => r["_field"] == "Wh")
    |> count()
    |> yield(name: "count")
"""
            logging.debug(query)
            output = self.query_api.query(query)
        else:
            # Skip for InfluxDB 1.8
            output = []
        return output

    def delete(self, date, measurement):
        """Delete data from the InfluxDB database.

        This method deletes data from the specified measurement for a given date.

        Args:
            date (str): Date of the data to be deleted.
            measurement (str): Name of the measurement to delete data from.
        """
        self.delete_api.delete(date, date, f'_measurement="{measurement}"', self.config.bucket, org=self.config.org)

    def write(self, tags, date=None, fields=None, measurement="log"):
        """Write data to the InfluxDB database.

        This method writes data to the specified measurement in the InfluxDB database.

        Args:
            tags (dict): Dictionary of tags associated with the data.
            date (datetime.datetime, optional): Date and time of the data. Defaults to None.
            fields (dict, optional): Dictionary of fields and their values. Defaults to None.
            measurement (str, optional): Name of the measurement. Defaults to "log".
        """
        date_max = self.max_retention
        if date is None:
            date_object = datetime.datetime.now()
        else:
            date_object = date
        if self.retention == 0 or (date.replace(tzinfo=None) > date_max.replace(tzinfo=None)):
            record = {
                "measurement": measurement,
                "time": date_object,
                "tags": {},
                "fields": {},
            }
            if tags:
                for key, value in tags.items():
                    record["tags"][key] = value
            if fields is not None:
                for key, value in fields.items():
                    record["fields"][key] = value
            self.write_api.write(bucket=self.config.bucket, org=self.config.org, record=record)
