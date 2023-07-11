import pytz
import logging
from dependencies import title

from init import INFLUXDB, DB


def forceRound(x, n):
    import decimal
    d = decimal.Decimal(repr(x))
    targetdigit = decimal.Decimal("1e%d" % -n)
    chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
    return float(chopped)


class ExportInfluxDB:

    def __init__(self, influxdb_config, usage_point_config, measurement_direction="consumption"):
        self.influxdb_config = influxdb_config
        self.db = DB
        self.usage_point_config = usage_point_config
        self.usage_point_id = self.usage_point_config.usage_point_id
        self.measurement_direction = measurement_direction
        if "timezone" not in self.influxdb_config or self.influxdb_config["timezone"] == "UTC":
            self.tz = pytz.UTC
        else:
            self.tz = pytz.timezone(self.influxdb_config["timezone"])

    def daily(self, measurement_direction="consumption"):
        current_month = ""
        if measurement_direction == "consumption":
            price = self.usage_point_config.consumption_price_base
        else:
            price = self.usage_point_config.production_price
        title(f'[{self.usage_point_id}] Exportation des données "{measurement_direction}" dans influxdb')
        for daily in self.db.get_daily_all(self.usage_point_id):
            date = daily.date
            watt = daily.value
            kwatt = watt / 1000
            euro = kwatt * price
            if current_month != date.strftime('%m'):
                logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
            # INFLUXDB.delete(self.tz.localize(date), measurement_direction)
            INFLUXDB.write(
                measurement=measurement_direction,
                date=self.tz.localize(date),
                tags={
                    "usage_point_id": self.usage_point_id,
                    "year": daily.date.strftime("%Y"),
                    "month": daily.date.strftime("%m"),
                },
                fields={
                    "Wh": float(watt),
                    "kWh": float(forceRound(kwatt, 5)),
                    "price": float(forceRound(euro, 5))
                },
            )
            current_month = date.strftime("%m")

    def detail(self, measurement_direction="consumption"):
        current_month = ""
        measurement = f"{measurement_direction}_detail"
        title(f'[{self.usage_point_id}] Exportation des données "{measurement.upper()}" dans influxdb')
        for detail in self.db.get_detail_all(self.usage_point_id, measurement_direction):
            date = detail.date
            watt = detail.value
            kwatt = watt / 1000
            watth = watt / (60 / detail.interval)
            kwatth = watth / 1000
            if current_month != date.strftime('%m'):
                logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
            if measurement_direction == "consumption":
                if detail.measure_type == "HP":
                    euro = kwatth * self.usage_point_config.consumption_price_hp
                else:
                    euro = kwatth * self.usage_point_config.consumption_price_hc
            else:
                euro = kwatth * self.usage_point_config.production_price
            INFLUXDB.write(
                measurement=measurement,
                date=self.tz.localize(date),
                tags={
                    "usage_point_id": self.usage_point_id,
                    "year": detail.date.strftime("%Y"),
                    "month": detail.date.strftime("%m"),
                    "internal": detail.interval,
                    "measure_type": detail.measure_type,
                },
                fields={
                    "W": float(watt),
                    "kW": float(forceRound(kwatt, 5)),
                    "Wh": float(watth),
                    "kWh": float(forceRound(kwatth, 5)),
                    "price": float(forceRound(euro, 5))
                },
            )
            current_month = date.strftime("%m")
