"""Class for exporting data to InfluxDB."""

import ast
import logging
from datetime import datetime

import pytz

from config import TIMEZONE_UTC
from database.daily import DatabaseDaily
from database.detail import DatabaseDetail
from database.ecowatt import DatabaseEcowatt
from database.tempo import DatabaseTempo
from init import INFLUXDB
from models.stat import Stat


def force_round(x, n):
    """Round a number to a specified number of decimal places.

    Args:
        x (float): The number to be rounded.
        n (int): The number of decimal places to round to.

    Returns:
        float: The rounded number.
    """
    import decimal

    d = decimal.Decimal(repr(x))
    targetdigit = decimal.Decimal("1e%d" % -n)
    chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
    return float(chopped)


class ExportInfluxDB:
    """Class for exporting data to InfluxDB."""

    def __init__(self, influxdb_config, usage_point_config, measurement_direction="consumption"):
        self.influxdb_config = influxdb_config
        self.usage_point_config = usage_point_config
        self.usage_point_id = self.usage_point_config.usage_point_id
        self.measurement_direction = measurement_direction
        self.stat = Stat(self.usage_point_id, measurement_direction=measurement_direction)
        self.time_format = "%Y-%m-%dT%H:%M:%SZ"
        if "timezone" not in self.influxdb_config or self.influxdb_config["timezone"] == "UTC":
            self.tz = TIMEZONE_UTC
        else:
            self.tz = pytz.timezone(self.influxdb_config["timezone"])

    def daily(self, measurement_direction="consumption"):
        """Export daily data to InfluxDB.

        Args:
            measurement_direction (str, optional): The measurement direction. Defaults to "consumption".
        """
        current_month = ""
        if measurement_direction == "consumption":
            price = self.usage_point_config.consumption_price_base
        else:
            price = self.usage_point_config.production_price
        logging.info(f'Envoi des données "{measurement_direction.upper()}" dans influxdb')
        get_daily_all = DatabaseDaily(self.usage_point_id).get_all()
        get_daily_all_count = len(get_daily_all)
        last_data = DatabaseDaily(self.usage_point_id, measurement_direction).get_last_date()
        first_data = DatabaseDaily(self.usage_point_id, measurement_direction).get_first_date()
        if last_data and first_data:
            start = datetime.strftime(last_data, self.time_format)
            end = datetime.strftime(first_data, self.time_format)
            influxdb_data = INFLUXDB.count(start, end, measurement_direction)
            count = 1
            for data in influxdb_data:
                for record in data.records:
                    count += record.get_value()
            if get_daily_all_count != count:
                logging.info(f" Cache : {get_daily_all_count} / InfluxDb : {count}")
                for daily in get_daily_all:
                    date = daily.date
                    if current_month != date.strftime("%m"):
                        logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
                    # if len(INFLUXDB.get(start, end, measurement_direction)) == 0:
                    watt = daily.value
                    kwatt = watt / 1000
                    euro = kwatt * price
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
                            "kWh": float(force_round(kwatt, 5)),
                            "price": float(force_round(euro, 5)),
                        },
                    )
                    current_month = date.strftime("%m")
                logging.info(" => OK")
            else:
                logging.info(f" => Données synchronisées ({count} valeurs)")
        else:
            logging.info(" => Aucune donnée")

    def detail(self, measurement_direction="consumption"):
        """Export detailed data to InfluxDB.

        Args:
            measurement_direction (str, optional): The measurement direction. Defaults to "consumption".
        """
        current_month = ""
        measurement = f"{measurement_direction}_detail"
        logging.info(f'Envoi des données "{measurement.upper()}" dans influxdb')
        get_detail_all = DatabaseDetail(self.usage_point_id, measurement_direction).get_all()
        get_detail_all_count = len(get_detail_all)
        last_data = DatabaseDetail(self.usage_point_id, measurement_direction).get_last_date()
        first_data = DatabaseDetail(self.usage_point_id, measurement_direction).get_first_date()
        if last_data and first_data:
            start = datetime.strftime(last_data, self.time_format)
            end = datetime.strftime(first_data, self.time_format)
            influxdb_data = INFLUXDB.count(start, end, measurement)
            count = 1
            for data in influxdb_data:
                for record in data.records:
                    count += record.get_value()

            if get_detail_all_count != count:
                logging.info(f" Cache : {get_detail_all_count} / InfluxDb : {count}")
                for _, detail in enumerate(get_detail_all):
                    date = detail.date
                    if current_month != date.strftime("%m"):
                        logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
                    watt = detail.value
                    kwatt = watt / 1000
                    watth = watt / (60 / detail.interval)
                    kwatth = watth / 1000
                    if measurement_direction == "consumption":
                        measure_type = self.stat.get_mesure_type(date)
                        if measure_type == "HP":
                            euro = kwatth * self.usage_point_config.consumption_price_hp
                        else:
                            euro = kwatth * self.usage_point_config.consumption_price_hc
                    else:
                        measure_type = "BASE"
                        euro = kwatth * self.usage_point_config.production_price
                    INFLUXDB.write(
                        measurement=measurement,
                        date=self.tz.localize(date),
                        tags={
                            "usage_point_id": self.usage_point_id,
                            "year": detail.date.strftime("%Y"),
                            "month": detail.date.strftime("%m"),
                            "internal": detail.interval,
                            "measure_type": measure_type,
                        },
                        fields={
                            "W": float(watt),
                            "kW": float(force_round(kwatt, 5)),
                            "Wh": float(watth),
                            "kWh": float(force_round(kwatth, 5)),
                            "price": float(force_round(euro, 5)),
                        },
                    )
                    current_month = date.strftime("%m")
                logging.info(" => OK")
            else:
                logging.info(f" => Données synchronisées ({count} valeurs)")
        else:
            logging.info(" => Aucune donnée")

    def tempo(self):
        """Export tempo data to InfluxDB."""
        measurement = "tempo"
        logging.info('Envoi des données "TEMPO" dans influxdb')
        tempo_data = DatabaseTempo().get()
        if tempo_data:
            for data in tempo_data:
                INFLUXDB.write(
                    measurement=measurement,
                    date=self.tz.localize(data.date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                    },
                    fields={"color": data.color},
                )
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def ecowatt(self):
        """Export ecowatt data to InfluxDB."""
        measurement = "ecowatt"
        logging.info('Envoi des données "ECOWATT" dans influxdb')
        ecowatt_data = DatabaseEcowatt().get()
        if ecowatt_data:
            for data in ecowatt_data:
                INFLUXDB.write(
                    measurement=f"{measurement}_daily",
                    date=self.tz.localize(data.date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                    },
                    fields={"value": data.value, "message": data.message},
                )
                data_detail = ast.literal_eval(data.detail)
                for date, value in data_detail.items():
                    date_format = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    INFLUXDB.write(
                        measurement=f"{measurement}_detail",
                        date=self.tz.localize(date_format),
                        tags={
                            "usage_point_id": self.usage_point_id,
                        },
                        fields={"value": value},
                    )
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")
