"""This module contains the InfluxDB class for connecting to and interacting with InfluxDB."""
import datetime
import inspect
import logging

import influxdb_client
from dateutil.tz import tzlocal
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

from config.main import APP_CONFIG
from const import TIMEZONE_UTC, URL_CONFIG_FILE
from utils import separator, separator_warning, title


class InfluxDB:
    """Class for connecting to and interacting with InfluxDB."""

    def __init__(self):
        self.influxdb = {}
        self.query_api = {}
        self.write_api = {}
        self.delete_api = {}
        self.buckets_api = {}
        self.retention = 0
        self.max_retention = None
        self.valid = False
        if APP_CONFIG.influxdb.enable:
            self.connect()
            if self.valid:
                if self.retention != 0:
                    day = int(self.retention / 60 / 60 / 24)
                    logging.warning(
                        f"<!> ATTENTION, InfluxDB est configuré avec une durée de rétention de {day} jours."
                    )
                    logging.warning(
                        f"    Toutes les données supérieures à {day} jours ne seront jamais insérées dans celui-ci."
                    )
                else:
                    logging.warning(" => Aucune durée de rétention de données détectée.")

    def connect(self):
        """Connect to InfluxDB.

        This method establishes a connection to the InfluxDB database using the provided configuration.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            separator()
            logging.info(f"Connect to InfluxDB {APP_CONFIG.influxdb.hostname}:{APP_CONFIG.influxdb.port}")
            date_utils.date_helper = DateHelper(timezone=tzlocal())
            self.influxdb = influxdb_client.InfluxDBClient(
                url=f"{APP_CONFIG.influxdb.scheme}://{APP_CONFIG.influxdb.hostname}:{APP_CONFIG.influxdb.port}",
                token=APP_CONFIG.influxdb.token,
                org=APP_CONFIG.influxdb.org,
                timeout="600000",
            )
            health = self.influxdb.health()
            if health.status == "pass":
                logging.info(" => Connection success")
                self.valid = True
                title(f"Méthode d'importation : {APP_CONFIG.influxdb.method.upper()}")
                if APP_CONFIG.influxdb.method.upper() == "ASYNCHRONOUS":
                    logging.warning(
                        ' <!> ATTENTION, le mode d\'importation "ASYNCHRONOUS"'
                        "est très consommateur de ressources système."
                    )
                    self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
                elif APP_CONFIG.influxdb.method.upper() == "SYNCHRONOUS":
                    self.write_api = self.influxdb.write_api(write_options=SYNCHRONOUS)
                else:
                    self.write_api = self.influxdb.write_api(
                        write_options=influxdb_client.WriteOptions(
                            batch_size=APP_CONFIG.influxdb.batching_options.batch_size,
                            flush_interval=APP_CONFIG.influxdb.batching_options.flush_interval,
                            jitter_interval=APP_CONFIG.influxdb.batching_options.jitter_interval,
                            retry_interval=APP_CONFIG.influxdb.batching_options.retry_interval,
                            max_retries=APP_CONFIG.influxdb.batching_options.max_retries,
                            max_retry_delay=APP_CONFIG.influxdb.batching_options.max_retry_delay,
                            exponential_base=APP_CONFIG.influxdb.batching_options.exponential_base,
                        )
                    )
                self.query_api = self.influxdb.query_api()
                self.delete_api = self.influxdb.delete_api()
                self.buckets_api = self.influxdb.buckets_api()
                self.get_list_retention_policies()
            else:
                logging.error(
                    f"""
    Impossible de se connecter à la base influxdb.

    Vous pouvez récupérer un exemple de configuration ici:
    {URL_CONFIG_FILE}
"""
                )

    def purge_influxdb(self):
        """Purge the InfluxDB database.

        This method wipes the InfluxDB database by deleting all data within specified measurement types.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            separator_warning()
            logging.warning(f"Wipe influxdb database {APP_CONFIG.influxdb.hostname}:{APP_CONFIG.influxdb.port}")
            start = "1970-01-01T00:00:00Z"
            stop = datetime.datetime.now(tz=TIMEZONE_UTC)
            measurement = [
                "consumption",
                "production",
                "consumption_detail",
                "production_detail",
            ]
            for mesure in measurement:
                self.delete_api.delete(
                    start, stop, f'_measurement="{mesure}"', APP_CONFIG.influxdb.bucket, org=APP_CONFIG.influxdb.org
                )
            logging.warning(" => Data reset")

    def get_list_retention_policies(self):
        """Get the list of retention policies.

        This method retrieves the list of retention policies for the InfluxDB database.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if APP_CONFIG.influxdb.org == "-":  # InfluxDB 1.8
                self.retention = 0
                self.max_retention = 0
                return
            buckets = self.buckets_api.find_buckets().buckets
            for bucket in buckets:
                if bucket.name == APP_CONFIG.influxdb.bucket:
                    self.retention = bucket.retention_rules[0].every_seconds
                    self.max_retention = datetime.datetime.now(tz=TIMEZONE_UTC) - datetime.timedelta(
                        seconds=self.retention
                    )

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
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if APP_CONFIG.influxdb.org != "-":
                query = f"""
    from(bucket: "{APP_CONFIG.influxdb.bucket}")
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
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if APP_CONFIG.influxdb.org != "-":
                query = f"""
    from(bucket: "{APP_CONFIG.influxdb.bucket}")
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
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            self.delete_api.delete(
                date, date, f'_measurement="{measurement}"', APP_CONFIG.influxdb.bucket, org=APP_CONFIG.influxdb.org
            )

    def write(self, tags, date=None, fields=None, measurement="log"):
        """Write data to the InfluxDB database.

        This method writes data to the specified measurement in the InfluxDB database.

        Args:
            tags (dict): Dictionary of tags associated with the data.
            date (datetime.datetime, optional): Date and time of the data. Defaults to None.
            fields (dict, optional): Dictionary of fields and their values. Defaults to None.
            measurement (str, optional): Name of the measurement. Defaults to "log".
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            date_max = self.max_retention
            if date is None:
                date_object = datetime.datetime.now(tz=TIMEZONE_UTC)
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
                self.write_api.write(bucket=APP_CONFIG.influxdb.bucket, org=APP_CONFIG.influxdb.org, record=record)
