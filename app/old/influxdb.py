import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from pprint import pprint
import locale
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pytz

from importlib import import_module

main = import_module("main")
f = import_module("function")

# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
# timezone = pytz.timezone('Europe/Paris')


def influxdb_insert(cur, con, pdl, pdl_config, influxdb, influxdb_api):
    def forceRound(x, n):
        import decimal
        d = decimal.Decimal(repr(x))
        targetdigit = decimal.Decimal("1e%d" % -n)
        chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
        return float(chopped)

    price = {
        "BASE": pdl_config['consumption_price_base'],
        "HC": pdl_config['consumption_price_hc'],
        "HP": pdl_config['consumption_price_hp']
    }

    f.log(f" => Import daily")
    query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' ORDER BY date DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    for result in query_result:
        date = result[1]
        value_wh = result[2]
        value_kwh = value_wh / 1000
        current_price = forceRound(value_kwh * price["BASE"], 4)
        f.log(f"Insert daily {date} => {value_wh}", "DEBUG")
        dateObject = datetime.strptime(date, '%Y-%m-%d')
        p = influxdb_client.Point("enedisgateway_daily") \
            .tag("pdl", pdl) \
            .tag("year", dateObject.strftime("%Y")) \
            .tag("month", dateObject.strftime("%m")) \
            .field("Wh", int(value_wh)) \
            .field("kWh", forceRound(value_kwh, 2)) \
            .field("price", current_price) \
            .time(dateObject)
        influxdb_api.write(bucket=main.config['influxdb']['bucket'], org=main.config['influxdb']['org'], record=p)

    f.log(f" => Import detail")
    query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' AND date BETWEEN '2021-11-22' AND '2021-11-30' ORDER BY date"
    # query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' ORDER BY date DESC"
    cur.execute(query)
    query_result = cur.fetchall()
    for result in query_result:
        date = result[1]
        interval_length = result[3]
        measure_type = result[4]
        value = result[2]
        value_kw = value / 1000
        value_wh = value * interval_length / 60
        value_kwh = value_wh / 1000
        current_price = forceRound(value_kwh * price[measure_type], 4)
        dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date = dateObject - relativedelta(minutes=int(interval_length))
        f.log(f"Insert detail {date} => {value}", "DEBUG")
        p = influxdb_client.Point("enedisgateway_detail") \
            .tag("pdl", pdl) \
            .tag("measure_type", measure_type) \
            .tag("interval", interval_length) \
            .tag("year", dateObject.strftime("%Y")) \
            .tag("month", dateObject.strftime("%m")) \
            .field("W", int(value)) \
            .field("kW", forceRound(int(value_kw), 2)) \
            .field("Wh", forceRound(int(value_wh), 2)) \
            .field("kWh", forceRound(int(value_kwh), 2)) \
            .field("price", current_price) \
            .time(date)

        influxdb_api.write(bucket=main.config['influxdb']['bucket'], org=main.config['influxdb']['org'], record=p)
