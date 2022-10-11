import datetime

from dateutil.relativedelta import relativedelta

import influxdb_client

from influxdb_client.client.write_api import ASYNCHRONOUS
from influxdb_client.client.util import date_utils
from influxdb_client.client.util.date_utils import DateHelper
from dateutil.tz import tzlocal

from dependencies import *


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
        logSep()
        log(f"Connect to InfluxDB {self.hostname}:{self.port}")
        date_utils.date_helper = DateHelper(timezone=tzlocal())
        self.influxdb = influxdb_client.InfluxDBClient(
            url=f"http://{self.hostname}:{self.port}",
            token=self.token,
            org=self.org,
            timeout="600000"
        )
        health = self.influxdb.health()
        if health.status == "pass":
            log(" => Connection success")
        else:
            logging.critical([
                "Impossible de se connecter à la base influxdb.",
                "",
                "Vous pouvez récupérer un exemple ici :",
                "https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file"
            ])

        self.write_api = self.influxdb.write_api(write_options=ASYNCHRONOUS)
        self.delete_api = self.influxdb.delete_api()

    def purge_influxdb(self):
        logWarn()
        log(f"Wipe influxdb database {self.hostname}:{self.port}")
        start = "1970-01-01T00:00:00Z"
        stop = datetime.datetime.utcnow()
        self.delete_api.delete(start, stop, '_measurement="enedis_daily"', self.bucket,
                               org=self.org)
        start = datetime.datetime.utcnow() - relativedelta(years=2)
        self.delete_api.delete(start, stop, '_measurement="enedis_detail"', self.bucket,
                               org=self.org)
        log(f" => Data reset")
