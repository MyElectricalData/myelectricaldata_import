import datetime

import influxdb_client
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzlocal
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper
from influxdb_client.client.write_api import ASYNCHRONOUS

import __main__ as app
from dependencies import *
from models.log import Log


class InfluxDB:

    def __init__(self, hostname, port, token, org="myelectricaldata.fr", bucket="myelectricaldata"):
        self.hostname = hostname
        self.port = port
        self.token = token
        self.org = org
        self.bucket = bucket
        self.influxdb = {}
        self.write_api = {}
        self.delete_api = {}
        self.connect()

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

        self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
        self.delete_api = self.influxdb.delete_api()

    def purge_influxdb(self):
        app.LOG.separator_warning()
        app.LOG.log(f"Wipe influxdb database {self.hostname}:{self.port}")
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
        # start = datetime.datetime.utcnow() - relativedelta(years=2)
        # self.delete_api.delete(start, stop, '_measurement="consumption_detail"', self.bucket,
        #                        org=self.org)
        app.LOG.log(f" => Data reset")

    def write(self, tags, date=None, fields=None, measurement="log"):
        if date is None:
            date_object = datetime.datetime.now()
        else:
            date_object = date
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
