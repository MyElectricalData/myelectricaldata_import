import datetime
import logging

import influxdb_client
from dateutil.tz import tzlocal
from influxdb_client.client.util.date_utils import DateHelper
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

from dependencies import separator, separator_warning, title


class InfluxDB:
    def __init__(
        self,
        scheme: str,
        hostname: str,
        port: int,
        token: str,
        org: str = "myelectricaldata.fr",
        bucket: str = "myelectricaldata",
        method="SYNCHRONOUS",
        write_options=None,
        vm_mode=False,
    ):
        if write_options is None:
            write_options = {}
        self.scheme = scheme
        self.hostname = hostname
        self.port = port
        self.token = token
        self.org = org
        self.bucket = bucket
        self.vm_mode = vm_mode
        self.influxdb = {}
        self.query_api = {}
        self.write_api = {}
        self.delete_api = {}
        self.buckets_api = {}
        self.method = method
        self.write_options = {
            "batch_size": write_options.get("batch_size", 1000),
            "flush_interval": write_options.get("flush_interval", 1000),
            "jitter_interval": write_options.get("jitter_interval", 0),
            "retry_interval": write_options.get("retry_interval", 5000),
            "max_retry_time": write_options.get("max_retry_time", "180_000"),
            "max_retries": write_options.get("max_retries", 5),
            "max_retry_delay": write_options.get("max_retry_delay", 125_000),
            "exponential_base": write_options.get("exponential_base", 2),
        }
        self.connect()
        self.retention = 0
        self.max_retention = None
        self.get_list_retention_policies()
        if self.retention != 0:
            day = int(self.retention / 60 / 60 / 24)
            logging.warning(f"<!> ATTENTION, InfluxDB est configuré avec une durée de rétention de {day} jours.")
            logging.warning(f"    Toutes les données supérieures à {day} jours ne seront jamais insérées dans celui-ci.")
        else:
            logging.warning(" => Aucune durée de rétention de données détectée.")

    def connect(self):
        separator()
        logging.info(f"Connexion à la base de données : {self.scheme}://{self.hostname}:{self.port} (vm_mode={self.vm_mode})")

        self.influxdb = influxdb_client.InfluxDBClient(
            url=f"{self.scheme}://{self.hostname}:{self.port}",
            token=self.token,
            org=self.org,
            timeout="600000",
        )

        if not self.vm_mode:
            try:
                health = self.influxdb.health()
                if health.status == "pass":
                    title("Connection success")
                else:
                    logging.critical("Impossible de se connecter à InfluxDB.")
                    exit(1)
            except Exception as e:
                logging.critical(f"Erreur de connexion InfluxDB : {e}")
                exit(1)
        else:
            title("Mode VictoriaMetrics actif (pas de vérification de santé)")

        title(f"Méthode d'importation : {self.method.upper()}")
        if self.method.upper() == "ASYNCHRONOUS":
            logging.warning(' <!> ATTENTION, le mode "ASYNCHRONOUS" est très consommateur de ressources système.')
            self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
        elif self.method.upper() == "SYNCHRONOUS":
            self.write_api = self.influxdb.write_api(write_options=SYNCHRONOUS)
        else:
            self.write_api = self.influxdb.write_api(
                write_options=influxdb_client.WriteOptions(
                    batch_size=self.write_options["batch_size"],
                    flush_interval=self.write_options["flush_interval"],
                    jitter_interval=self.write_options["jitter_interval"],
                    retry_interval=self.write_options["retry_interval"],
                    max_retries=self.write_options["max_retries"],
                    max_retry_delay=self.write_options["max_retry_delay"],
                    exponential_base=self.write_options["exponential_base"],
                )
            )

        self.query_api = self.influxdb.query_api()
        self.delete_api = self.influxdb.delete_api()
        self.buckets_api = self.influxdb.buckets_api()

    def purge_influxdb(self):
        separator_warning()
        logging.warning(f"Suppression des données InfluxDB {self.hostname}:{self.port}")
        start = "1970-01-01T00:00:00Z"
        stop = datetime.datetime.utcnow()
        measurement = ["consumption", "production", "consumption_detail", "production_detail"]
        for mesure in measurement:
            self.delete_api.delete(start, stop, f'_measurement="{mesure}"', self.bucket, org=self.org)
        logging.warning(" => Données supprimées")

    def get_list_retention_policies(self):
        if self.org == "-" or self.vm_mode:
            self.retention = 0
            self.max_retention = datetime.datetime.now()
        else:
            try:
                buckets = self.buckets_api.find_buckets().buckets
                for bucket in buckets:
                    if bucket.name == self.bucket:
                        self.retention = bucket.retention_rules[0].every_seconds
                        self.max_retention = datetime.datetime.now() - datetime.timedelta(seconds=self.retention)
            except Exception as e:
                logging.warning(f"Impossible de récupérer les règles de rétention : {e}")
                self.retention = 0
                self.max_retention = datetime.datetime.now()

    def get(self, start, end, measurement):
        if self.org != "-" and not self.vm_mode:
            query = f"""
from(bucket: "{self.bucket}")
  |> range(start: {start}, stop: {end})
  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
"""
            logging.debug(query)
            return self.query_api.query(query)
        return []

    def count(self, start, end, measurement):
        if self.org != "-" and not self.vm_mode:
            query = f"""
from(bucket: "{self.bucket}")
    |> range(start: {start}, stop: {end})
    |> filter(fn: (r) => r["_measurement"] == "{measurement}")
    |> filter(fn: (r) => r["_field"] == "Wh")
    |> count()
    |> yield(name: "count")
"""
            logging.debug(query)
            return self.query_api.query(query)
        return []

    def delete(self, date, measurement):
        self.delete_api.delete(date, date, f'_measurement="{measurement}"', self.bucket, org=self.org)

    def write(self, tags, date=None, fields=None, measurement="log"):
        date_max = self.max_retention
        if date is None:
            date_object = datetime.datetime.now()
        else:
            date_object = date
        if self.retention == 0 or (date.replace(tzinfo=None) > date_max.replace(tzinfo=None)):
            record = {
                "measurement": measurement,
                "time": date_object,
                "tags": tags or {},
                "fields": fields or {},
            }
            self.write_api.write(bucket=self.bucket, org=self.org, record=record)
