import __main__ as app
import datetime

import pytz

import __main__ as app
from dependencies import *

utc=pytz.UTC

def forceRound(x, n):
    import decimal
    d = decimal.Decimal(repr(x))
    targetdigit = decimal.Decimal("1e%d" % -n)
    chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
    return float(chopped)

class ExportInfluxDB:

    def __init__(self, usage_point_id, measurement_direction="consumption" ):
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction

    def daily(self, price, measurement_direction="consumption"):
        current_month = ""
        app.LOG.title(f'[{self.usage_point_id}] Exportation des données "{measurement_direction}" dans influxdb')
        for daily in app.DB.get_daily_all(self.usage_point_id):
            date = daily.date
            watt = daily.value
            kwatt = watt / 1000
            euro = kwatt * price
            if current_month != date.strftime('%m'):
                app.LOG.log(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
            app.INFLUXDB.write(
                measurement=measurement_direction,
                date=utc.localize(date),
                tags={
                    "usage_point_id": self.usage_point_id,
                    "year": daily.date.strftime("%Y"),
                    "month": daily.date.strftime("%m"),
                },
                fields={
                    "Wh": float(watt),
                    "kWh": float(forceRound(kwatt, 2)),
                    "price": float(forceRound(euro, 2))
                },
            )
            current_month = date.strftime("%m")

    def detail(self, price_hp, price_hc=0, measurement_direction="consumption_detail"):
        current_month = ""
        app.LOG.title(f'[{self.usage_point_id}] Exportation des données "{measurement_direction}" dans influxdb')
        for detail in app.DB.get_detail_all(self.usage_point_id):
            date = detail.date
            watt = detail.value
            kwatt = watt / 1000
            watth = watt / (60 / detail.interval)
            kwatth = watth / 1000
            if current_month != date.strftime('%m'):
                app.LOG.log(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
            if detail.measure_type == "HP":
                euro = kwatth * price_hp
            else:
                euro = kwatth * price_hc
            app.INFLUXDB.write(
                measurement=measurement_direction,
                date=utc.localize(date),
                tags={
                    "usage_point_id": self.usage_point_id,
                    "year": detail.date.strftime("%Y"),
                    "month": detail.date.strftime("%m"),
                    "internal": detail.interval,
                    "measure_type": detail.measure_type,
                },
                fields={
                    "W": float(watt),
                    "kW": float(forceRound(kwatt, 2)),
                    "Wh": float(watth),
                    "kWh": float(forceRound(kwatth, 2)),
                    "price": float(forceRound(euro, 2))
                },
            )
            current_month = date.strftime("%m")
