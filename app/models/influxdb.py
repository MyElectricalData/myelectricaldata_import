import datetime

import __main__ as app

import influxdb_client
from dateutil.tz import tzlocal
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS

from dependencies import *


class InfluxDB:

    def __init__(self, hostname, port, token, org="myelectricaldata.fr", bucket="myelectricaldata", method="batching",
                 write_options=None):
        if write_options is None:
            write_options = {}
        self.hostname = hostname
        self.port = port
        self.token = token
        self.org = org
        self.bucket = bucket
        self.influxdb = {}
        self.write_api = {}
        self.delete_api = {}
        self.buckets_api = {}
        self.method = method
        self.write_options = {}
        if "batch_size" in write_options:
            self.write_options["batch_size"] = write_options["batch_size"]
        else:
            self.write_options["batch_size"] = 1000
        if "flush_interval" in write_options:
            self.write_options["flush_interval"] = write_options["flush_interval"]
        else:
            self.write_options["flush_interval"] = 1000
        if "jitter_interval" in write_options:
            self.write_options["jitter_interval"] = write_options["jitter_interval"]
        else:
            self.write_options["jitter_interval"] = 0
        if "retry_interval" in write_options:
            self.write_options["retry_interval"] = write_options["retry_interval"]
        else:
            self.write_options["retry_interval"] = 5000
        if "max_retry_time" in write_options:
            self.write_options["max_retry_time"] = write_options["max_retry_time"]
        else:
            self.write_options["max_retry_time"] = "180_000"
        if "max_retries" in write_options:
            self.write_options["max_retries"] = write_options["max_retries"]
        else:
            self.write_options["max_retries"] = 5
        if "max_retry_delay" in write_options:
            self.write_options["max_retry_delay"] = write_options["max_retry_delay"]
        else:
            self.write_options["max_retry_delay"] = 125_000
        if "exponential_base" in write_options:
            self.write_options["exponential_base"] = write_options["exponential_base"]
        else:
            self.write_options["exponential_base"] = 2
        self.connect()
        self.retention = 0
        self.max_retention = None
        self.get_list_retention_policies()
        if self.retention < 94608000:
            day = int(self.retention / 60 / 60 / 24)
            app.LOG.log([
                f" => ATTENTION, l'InfluxDB est configuré avec une durée de retention de {day} jours.",
                f"    Toutes les données supérieurs à {day} jours ne seront jamais inséré dans celui-ci."
            ])


    def connect(self):
        app.LOG.separator()
        app.LOG.log(f"Connect to InfluxDB {self.hostname}:{self.port}")
        date_utils.date_helper = DateHelper(timezone=tzlocal())
        self.influxdb = influxdb_client.InfluxDBClient(
            url=f"http://{self.hostname}:{self.port}",
            token=self.token,
            org=self.org,
            timeout="600000"
        )
        health = self.influxdb.health()
        if health.status == "pass":
            app.LOG.log(" => Connection success")
        else:
            app.LOG.critical([
                "Impossible de se connecter à la base influxdb.",
                "",
                "Vous pouvez récupérer un exemple ici :",
                "https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file"
            ])

        if self.method.upper() == "ASYNCHRONOUS":
            self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
        elif self.method.upper() == "SYNCHRONOUS":
            self.write_api = self.influxdb.write_api(write_options=SYNCHRONOUS)
        else:
            self.write_api = self.influxdb.write_api(write_options=influxdb_client.WriteOptions(
                batch_size=self.write_options["batch_size"],
                flush_interval=self.write_options["flush_interval"],
                jitter_interval=self.write_options["jitter_interval"],
                retry_interval=self.write_options["retry_interval"],
                max_retries=self.write_options["max_retries"],
                max_retry_delay=self.write_options["max_retry_delay"],
                exponential_base=self.write_options["exponential_base"]))
        self.delete_api = self.influxdb.delete_api()
        self.buckets_api = self.influxdb.buckets_api()
        self.get_list_retention_policies()

    def purge_influxdb(self):
        app.LOG.separator_warning()
        app.LOG.warning(f"Wipe influxdb database {self.hostname}:{self.port}")
        start = "1970-01-01T00:00:00Z"
        stop = datetime.datetime.utcnow()
        measurement = [
            "consumption",
            "production",
            "consumption_detail",
            "production_detail",
        ]
        for mesure in measurement:
            self.delete_api.delete(start, stop, f'_measurement="{mesure}"', self.bucket,
                                   org=self.org)
        # app.CONFIG.set("wipe_influxdb", False)
        app.LOG.warning(f" => Data reset")

    def get_list_retention_policies(self):
        buckets = self.buckets_api.find_buckets().buckets
        for bucket in buckets:
            if bucket.name == self.bucket:
                self.retention = bucket.retention_rules[0].every_seconds
                self.max_retention = datetime.datetime.now() - datetime.timedelta(seconds=self.retention)

    def write(self, tags, date=None, fields=None, measurement="log"):
        date_max = datetime.datetime.now() - datetime.timedelta(seconds=self.retention)
        if date is None:
            date_object = datetime.datetime.now()
        else:
            date_object = date
        if date.replace(tzinfo=None) > date_max.replace(tzinfo=None):
            record = {
                "measurement": measurement,
                "time": date_object,
                "tags": {},
                "fields": {}
            }
            if tags:
                for key, value in tags.items():
                    record["tags"][key] = value
            if fields is not None:
                for key, value in fields.items():
                    record["fields"][key] = value
            self.write_api.write(bucket=self.bucket, org=self.org, record=record)