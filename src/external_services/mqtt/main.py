"""Export des données vers MQTT."""

import ast
import inspect
import logging
import traceback
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from config.main import APP_CONFIG
from const import TIMEZONE_UTC
from database.addresses import DatabaseAddresses
from database.contracts import DatabaseContracts
from database.daily import DatabaseDaily
from database.detail import DatabaseDetail
from database.ecowatt import DatabaseEcowatt
from database.max_power import DatabaseMaxPower
from database.statistique import DatabaseStatistique
from database.tempo import DatabaseTempo
from database.usage_points import DatabaseUsagePoints
from external_services.mqtt.client import Mqtt
from models.stat import Stat


class ExportMqtt:
    """A class for exporting MQTT data."""

    def __init__(self, usage_point_id):
        self.usage_point_id = usage_point_id
        self.usage_point_config = APP_CONFIG.myelectricaldata.usage_point_config[self.usage_point_id]
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.mqtt_client = Mqtt()
        self.bootstrap()

    def bootstrap(self):
        """Bootstrap apps with cleanup."""
        try:
            if self.mqtt_client.valid:
                self.run()
            else:
                logging.critical("=> Export MQTT Désactivée (Echec de connexion)")
        except Exception:
            traceback.print_exc()
        finally:
            self.cleanup()

    def run(self):
        """Run jobs."""
        self.status()
        self.contract()
        self.address()
        self.ecowatt()
        if getattr(self.usage_point_config, "consumption", False) or getattr(
            self.usage_point_config, "consumption_detail", False
        ):
            self.tempo()
        if getattr(self.usage_point_config, "consumption", False):
            price_base = self.usage_point_config.consumption_price_base
            self.daily_annual(price_base, measurement_direction="consumption")
            self.daily_linear(price_base, measurement_direction="consumption")
        if getattr(self.usage_point_config, "production", False):
            self.daily_annual(self.usage_point_config.production_price, measurement_direction="production")
            self.daily_linear(self.usage_point_config.production_price, measurement_direction="production")
        if getattr(self.usage_point_config, "consumption_detail", False):
            price_hp = self.usage_point_config.consumption_price_hp
            price_hc = self.usage_point_config.consumption_price_hc
            self.detail_annual(price_hp, price_hc, measurement_direction="consumption")
            self.detail_linear(price_hp, price_hc, measurement_direction="consumption")
        if getattr(self.usage_point_config, "production_detail", False):
            self.detail_annual(self.usage_point_config.production_price, measurement_direction="production")
            self.detail_linear(self.usage_point_config.production_price, measurement_direction="production")
        if getattr(self.usage_point_config, "consumption_max_power", False):
            self.max_power()

    def status(self):
        """Get the status of the account."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Statut du compte.")
            usage_point_config = DatabaseUsagePoints(self.usage_point_id).get()
            send_data = [
                "consentement_expiration",
                "call_number",
                "quota_reached",
                "quota_limit",
                "quota_reset_at",
                "last_call",
                "ban",
            ]
            consentement_expiration = {}
            for item in send_data:
                if hasattr(usage_point_config, item):
                    queue = f"{self.usage_point_id}/status/{item}"
                    value = getattr(usage_point_config, item)
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    consentement_expiration[queue] = str(getattr(usage_point_config, item))
            self.mqtt_client.publish_multiple(consentement_expiration)
            logging.info(" => OK")

    def contract(self):
        """Get the contract data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des messages du contrat")
            contract_data = DatabaseContracts(self.usage_point_id).get()
            if hasattr(contract_data, "__table__"):
                output = {}
                for column in contract_data.__table__.columns:
                    output[f"{self.usage_point_id}/contract/{column.name}"] = str(getattr(contract_data, column.name))
                self.mqtt_client.publish_multiple(output)
                logging.info(" => OK")
            else:
                logging.info(" => ERREUR")

    def address(self):
        """Get the address data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des messages d'addresse")
            address_data = DatabaseAddresses(self.usage_point_id).get()
            if hasattr(address_data, "__table__"):
                output = {}
                for column in address_data.__table__.columns:
                    output[f"{self.usage_point_id}/address/{column.name}"] = str(getattr(address_data, column.name))
                self.mqtt_client.publish_multiple(output)
                logging.info(" => OK")
            else:
                logging.info(" => ERREUR")

    def daily_annual(self, price, measurement_direction="consumption"):
        """Get the daily annual data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données annuelles")
            date_range = DatabaseDaily(self.usage_point_id).get_date_range()
            stat = Stat(self.usage_point_id, measurement_direction)
            if date_range["begin"] and date_range["end"]:
                date_begin = datetime.combine(date_range["begin"], datetime.min.time()).astimezone(TIMEZONE_UTC)
                date_end = datetime.combine(date_range["end"], datetime.max.time()).astimezone(TIMEZONE_UTC)
                date_begin_current = datetime.combine(
                    date_end.replace(month=1).replace(day=1), datetime.min.time()
                ).astimezone(TIMEZONE_UTC)
                finish = False
                while not finish:
                    year = int(date_begin_current.strftime("%Y"))
                    get_daily_year = stat.get_year(year=year)
                    get_daily_month = stat.get_month(year=year)
                    get_daily_week = stat.get_week(year=year)
                    if year == int(datetime.now(tz=TIMEZONE_UTC).strftime("%Y")):
                        sub_prefix = f"{self.usage_point_id}/{measurement_direction}/annual/current"
                    else:
                        sub_prefix = f"{self.usage_point_id}/{measurement_direction}/annual/{year}"
                    mqtt_data = {
                        # thisYear
                        f"{sub_prefix}/thisYear/dateBegin": get_daily_year["begin"],
                        f"{sub_prefix}/thisYear/dateEnd": get_daily_year["end"],
                        f"{sub_prefix}/thisYear/base/Wh": get_daily_year["value"],
                        f"{sub_prefix}/thisYear/base/kWh": round(get_daily_year["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/base/euro": round(get_daily_year["value"] / 1000 * price, 2),
                        # thisMonth
                        f"{sub_prefix}/thisMonth/dateBegin": get_daily_month["begin"],
                        f"{sub_prefix}/thisMonth/dateEnd": get_daily_month["end"],
                        f"{sub_prefix}/thisMonth/base/Wh": get_daily_month["value"],
                        f"{sub_prefix}/thisMonth/base/kWh": round(get_daily_month["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/base/euro": round(get_daily_month["value"] / 1000 * price, 2),
                        # thisWeek
                        f"{sub_prefix}/thisWeek/dateBegin": get_daily_week["begin"],
                        f"{sub_prefix}/thisWeek/dateEnd": get_daily_week["end"],
                        f"{sub_prefix}/thisWeek/base/Wh": get_daily_week["value"],
                        f"{sub_prefix}/thisWeek/base/kWh": round(get_daily_week["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/base/euro": round(get_daily_week["value"] / 1000 * price, 2),
                    }

                    for week in range(7):
                        begin = stat.daily(week)["begin"]
                        begin_day = (
                            datetime.strptime(stat.daily(week)["begin"], self.date_format)
                            .astimezone(TIMEZONE_UTC)
                            .strftime("%A")
                        )
                        end = stat.daily(week)["end"]
                        value = stat.daily(week)["value"]
                        mqtt_data[f"{sub_prefix}/week/{begin_day}/dateBegin"] = begin
                        mqtt_data[f"{sub_prefix}/week/{begin_day}/dateEnd"] = end
                        mqtt_data[f"{sub_prefix}/week/{begin_day}/base/Wh"] = value
                        mqtt_data[f"{sub_prefix}/week/{begin_day}/base/kWh"] = round(value / 1000, 2)
                        mqtt_data[f"{sub_prefix}/week/{begin_day}/base/euro"] = round(value / 1000 * price, 2)

                    for month in range(1, 13):
                        get_daily_month = stat.get_month(year=year, month=month)
                        mqtt_data[f"{sub_prefix}/month/{month}/dateBegin"] = get_daily_month["begin"]
                        mqtt_data[f"{sub_prefix}/month/{month}/dateEnd"] = get_daily_month["end"]
                        mqtt_data[f"{sub_prefix}/month/{month}/base/Wh"] = get_daily_month["value"]
                        mqtt_data[f"{sub_prefix}/month/{month}/base/kWh"] = round(get_daily_month["value"] / 1000, 2)
                        mqtt_data[f"{sub_prefix}/month/{month}/base/euro"] = round(
                            get_daily_month["value"] / 1000 * price, 2
                        )

                    if date_begin_current == date_begin:
                        finish = True
                    date_begin_current = date_begin_current - relativedelta(years=1)
                    if date_begin_current < date_begin:
                        date_begin_current = date_begin
                    self.mqtt_client.publish_multiple(mqtt_data)

                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def daily_linear(self, price, measurement_direction="consumption"):
        """Get the daily linear data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données linéaires journalières.")
            date_range = DatabaseDaily(self.usage_point_id).get_date_range()
            stat = Stat(self.usage_point_id, measurement_direction)
            if date_range["begin"] and date_range["end"]:
                date_begin = datetime.combine(date_range["begin"], datetime.min.time()).astimezone(TIMEZONE_UTC)
                date_end = datetime.combine(date_range["end"], datetime.max.time()).astimezone(TIMEZONE_UTC)
                date_begin_current = date_end - relativedelta(years=1)
                date_begin_current = date_begin_current.astimezone(TIMEZONE_UTC)
                idx = 0
                finish = False
                while not finish:
                    if idx == 0:
                        key = "year"
                    else:
                        key = f"year-{idx}"
                    sub_prefix = f"{self.usage_point_id}/{measurement_direction}/linear/{key}"
                    get_daily_year_linear = stat.get_year_linear(idx)
                    get_daily_month_linear = stat.get_month_linear(idx)
                    get_daily_week_linear = stat.get_week_linear(idx)
                    mqtt_data = {
                        # thisYear
                        f"{sub_prefix}/thisYear/dateBegin": get_daily_year_linear["begin"],
                        f"{sub_prefix}/thisYear/dateEnd": get_daily_year_linear["end"],
                        f"{sub_prefix}/thisYear/base/Wh": get_daily_year_linear["value"],
                        f"{sub_prefix}/thisYear/base/kWh": round(get_daily_year_linear["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/base/euro": round(get_daily_year_linear["value"] / 1000 * price, 2),
                        # thisMonth
                        f"{sub_prefix}/thisMonth/dateBegin": get_daily_month_linear["begin"],
                        f"{sub_prefix}/thisMonth/dateEnd": get_daily_month_linear["end"],
                        f"{sub_prefix}/thisMonth/base/Wh": get_daily_month_linear["value"],
                        f"{sub_prefix}/thisMonth/base/kWh": round(get_daily_month_linear["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/base/euro": round(get_daily_month_linear["value"] / 1000 * price, 2),
                        # thisWeek
                        f"{sub_prefix}/thisWeek/dateBegin": get_daily_week_linear["begin"],
                        f"{sub_prefix}/thisWeek/dateEnd": get_daily_week_linear["end"],
                        f"{sub_prefix}/thisWeek/base/Wh": get_daily_week_linear["value"],
                        f"{sub_prefix}/thisWeek/base/kWh": round(get_daily_week_linear["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/base/euro": round(get_daily_week_linear["value"] / 1000 * price, 2),
                    }

                    # CALCUL NEW DATE
                    if date_begin_current <= date_begin:
                        finish = True
                    date_end = datetime.combine((date_end - relativedelta(years=1)), datetime.max.time())
                    date_begin_current = date_begin_current - relativedelta(years=1)
                    if date_begin_current.astimezone(TIMEZONE_UTC) < date_begin.astimezone(TIMEZONE_UTC):
                        date_begin_current = datetime.combine(date_begin, datetime.min.time()).astimezone(TIMEZONE_UTC)
                    idx = idx + 1

                    self.mqtt_client.publish_multiple(mqtt_data)

                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def detail_annual(self, price_hp, price_hc=0, measurement_direction="consumption"):  # noqa: PLR0915
        """Get the detailed annual data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données annuelles détaillé.")
            date_range = DatabaseDetail(self.usage_point_id).get_date_range()
            stat = Stat(self.usage_point_id, measurement_direction)
            if date_range["begin"] and date_range["end"]:
                date_begin = datetime.combine(date_range["begin"], datetime.min.time()).astimezone(TIMEZONE_UTC)
                date_end = datetime.combine(date_range["end"], datetime.max.time()).astimezone(TIMEZONE_UTC)
                date_begin_current = datetime.combine(date_end.replace(month=1).replace(day=1), datetime.min.time())
                finish = False
                while not finish:
                    year = int(date_begin_current.strftime("%Y"))
                    month = int(datetime.now(tz=TIMEZONE_UTC).strftime("%m"))
                    get_detail_year_hp = stat.get_year(year=year, measure_type="HP")
                    get_detail_year_hc = stat.get_year(year=year, measure_type="HC")
                    get_detail_month_hp = stat.get_month(year=year, month=month, measure_type="HP")
                    get_detail_month_hc = stat.get_month(year=year, month=month, measure_type="HC")
                    get_detail_week_hp = stat.get_week(
                        year=year,
                        month=month,
                        measure_type="HP",
                    )
                    get_detail_week_hc = stat.get_week(
                        year=year,
                        month=month,
                        measure_type="HC",
                    )

                    if year == int(datetime.now(tz=TIMEZONE_UTC).strftime("%Y")):
                        sub_prefix = f"{self.usage_point_id}/{measurement_direction}/annual/current"
                    else:
                        sub_prefix = f"{self.usage_point_id}/{measurement_direction}/annual/{year}"
                    mqtt_data = {
                        # thisYear - HP
                        f"{sub_prefix}/thisYear/hp/Wh": get_detail_year_hp["value"],
                        f"{sub_prefix}/thisYear/hp/kWh": round(get_detail_year_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/hp/euro": round(get_detail_year_hp["value"] / 1000 * price_hp, 2),
                        # thisYear - HC
                        f"{sub_prefix}/thisYear/hc/Wh": get_detail_year_hc["value"],
                        f"{sub_prefix}/thisYear/hc/kWh": round(get_detail_year_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/hc/euro": round(get_detail_year_hc["value"] / 1000 * price_hc, 2),
                        # thisMonth - HP
                        f"{sub_prefix}/thisMonth/hp/Wh": get_detail_month_hp["value"],
                        f"{sub_prefix}/thisMonth/hp/kWh": round(get_detail_month_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/hp/euro": round(get_detail_month_hp["value"] / 1000 * price_hp, 2),
                        # thisMonth - HC
                        f"{sub_prefix}/thisMonth/hc/Wh": get_detail_month_hc["value"],
                        f"{sub_prefix}/thisMonth/hc/kWh": round(get_detail_month_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/hc/euro": round(get_detail_month_hc["value"] / 1000 * price_hc, 2),
                        # thisWeek - HP
                        f"{sub_prefix}/thisWeek/hp/Wh": get_detail_week_hp["value"],
                        f"{sub_prefix}/thisWeek/hp/kWh": round(get_detail_week_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/hp/euro": round(get_detail_week_hp["value"] / 1000 * price_hp, 2),
                        # thisWeek - HC
                        f"{sub_prefix}/thisWeek/hc/Wh": get_detail_week_hc["value"],
                        f"{sub_prefix}/thisWeek/hc/kWh": round(get_detail_week_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/hc/euro": round(get_detail_week_hc["value"] / 1000 * price_hc, 2),
                    }

                    for week in range(7):
                        # HP
                        begin_hp_day = (
                            datetime.strptime(stat.detail(week, "HP")["begin"], self.date_format)
                            .astimezone(TIMEZONE_UTC)
                            .strftime("%A")
                        )
                        value_hp = stat.detail(week, "HP")["value"]
                        prefix = f"{sub_prefix}/week/{begin_hp_day}/hp"
                        mqtt_data[f"{prefix}/Wh"] = value_hp
                        mqtt_data[f"{prefix}/kWh"] = round(value_hp / 1000, 2)
                        mqtt_data[f"{prefix}/euro"] = round(value_hp / 1000 * price_hp, 2)
                        # HC
                        begin_hc_day = (
                            datetime.strptime(stat.detail(week, "HC")["begin"], self.date_format)
                            .astimezone(TIMEZONE_UTC)
                            .strftime("%A")
                        )
                        value_hc = stat.detail(week, "HC")["value"]
                        prefix = f"{sub_prefix}/week/{begin_hc_day}/hc"
                        mqtt_data[f"{prefix}/Wh"] = value_hc
                        mqtt_data[f"{prefix}/kWh"] = round(value_hc / 1000, 2)
                        mqtt_data[f"{prefix}/euro"] = round(value_hc / 1000 * price_hc, 2)

                    for month in range(12):
                        current_month = month + 1
                        # HP
                        get_detail_month_hp = stat.get_month(year=year, month=current_month, measure_type="HP")
                        prefix = f"{sub_prefix}/month/{current_month}/hp"
                        mqtt_data[f"{prefix}/Wh"] = get_detail_month_hp["value"]
                        mqtt_data[f"{prefix}/kWh"] = round(get_detail_month_hp["value"] / 1000, 2)
                        mqtt_data[f"{prefix}/euro"] = round(get_detail_month_hp["value"] / 1000 * price_hp, 2)
                        # HC
                        get_detail_month_hc = stat.get_month(year=year, month=current_month, measure_type="HC")
                        prefix = f"{sub_prefix}/month/{current_month}/hc"
                        mqtt_data[f"{prefix}/Wh"] = get_detail_month_hc["value"]
                        mqtt_data[f"{prefix}/kWh"] = round(get_detail_month_hc["value"] / 1000, 2)
                        mqtt_data[f"{prefix}/euro"] = round(get_detail_month_hc["value"] / 1000 * price_hc, 2)
                    if date_begin_current == date_begin:
                        finish = True
                    date_end = datetime.combine(
                        (date_end - relativedelta(years=1)).replace(month=12, day=31),
                        datetime.max.time(),
                    )
                    date_begin_current = date_begin_current - relativedelta(years=1)
                    if date_begin_current.astimezone(TIMEZONE_UTC) < date_begin.astimezone(TIMEZONE_UTC):
                        date_begin_current = date_begin

                    self.mqtt_client.publish_multiple(mqtt_data)

                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def detail_linear(self, price_hp, price_hc=0, measurement_direction="consumption"):
        """Get the detailed linear data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données linéaires détaillées")
            date_range = DatabaseDetail(self.usage_point_id).get_date_range()
            stat = Stat(self.usage_point_id, measurement_direction)
            if date_range["begin"] and date_range["end"]:
                date_begin = datetime.combine(date_range["begin"], datetime.min.time()).astimezone(TIMEZONE_UTC)
                date_end = datetime.combine(date_range["end"], datetime.max.time()).astimezone(TIMEZONE_UTC)
                date_begin_current = date_end - relativedelta(years=1)
                idx = 0
                finish = False
                while not finish:
                    if idx == 0:
                        key = "year"
                    else:
                        key = f"year-{idx}"
                    sub_prefix = f"{self.usage_point_id}/{measurement_direction}/linear/{key}"
                    get_daily_year_linear_hp = stat.get_year_linear(idx, "HP")
                    get_daily_year_linear_hc = stat.get_year_linear(idx, "HC")
                    get_detail_month_linear_hp = stat.get_month_linear(idx, "HP")
                    get_detail_month_linear_hc = stat.get_month_linear(idx, "HC")
                    get_detail_week_linear_hp = stat.get_week_linear(idx, "HP")
                    get_detail_week_linear_hc = stat.get_week_linear(
                        idx,
                        "HC",
                    )
                    mqtt_data = {
                        # thisYear
                        f"{sub_prefix}/thisYear/hp/Wh": get_daily_year_linear_hp["value"],
                        f"{sub_prefix}/thisYear/hp/kWh": round(get_daily_year_linear_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/hp/euro": round(
                            get_daily_year_linear_hp["value"] / 1000 * price_hp, 2
                        ),
                        f"{sub_prefix}/thisYear/hc/Wh": get_daily_year_linear_hc["value"],
                        f"{sub_prefix}/thisYear/hc/kWh": round(get_daily_year_linear_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisYear/hc/euro": round(
                            get_daily_year_linear_hc["value"] / 1000 * price_hc, 2
                        ),
                        # thisMonth
                        f"{sub_prefix}/thisMonth/hp/Wh": get_detail_month_linear_hp["value"],
                        f"{sub_prefix}/thisMonth/hp/kWh": round(get_detail_month_linear_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/hp/euro": round(
                            get_detail_month_linear_hp["value"] / 1000 * price_hp, 2
                        ),
                        f"{sub_prefix}/thisMonth/hc/Wh": get_detail_month_linear_hc["value"],
                        f"{sub_prefix}/thisMonth/hc/kWh": round(get_detail_month_linear_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisMonth/hc/euro": round(
                            get_detail_month_linear_hc["value"] / 1000 * price_hc, 2
                        ),
                        # thisWeek
                        f"{sub_prefix}/thisWeek/hp/Wh": get_detail_week_linear_hp["value"],
                        f"{sub_prefix}/thisWeek/hp/kWh": round(get_detail_week_linear_hp["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/hp/euro": round(
                            get_detail_week_linear_hp["value"] / 1000 * price_hp, 2
                        ),
                        f"{sub_prefix}/thisWeek/hc/Wh": get_detail_week_linear_hc["value"],
                        f"{sub_prefix}/thisWeek/hc/kWh": round(get_detail_week_linear_hc["value"] / 1000, 2),
                        f"{sub_prefix}/thisWeek/hc/euro": round(
                            get_detail_week_linear_hc["value"] / 1000 * price_hc, 2
                        ),
                    }

                    # CALCUL NEW DATE
                    if date_begin_current.astimezone(TIMEZONE_UTC) <= date_begin.astimezone(TIMEZONE_UTC):
                        finish = True
                    date_end = datetime.combine((date_end - relativedelta(years=1)), datetime.max.time())
                    date_begin_current = date_begin_current - relativedelta(years=1)
                    if date_begin_current.astimezone(TIMEZONE_UTC) < date_begin.astimezone(TIMEZONE_UTC):
                        date_begin_current = datetime.combine(date_begin, datetime.min.time())
                    idx = idx + 1

                    self.mqtt_client.publish_multiple(mqtt_data)
                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def max_power(self):
        """Get the maximum power data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données de puissance max journalières.")
            max_power_data = DatabaseMaxPower(self.usage_point_id).get_all(order="asc")
            mqtt_data = {}
            contract = DatabaseContracts(self.usage_point_id).get()
            if max_power_data:
                max_value = 0
                if hasattr(contract, "subscribed_power"):
                    max_value = int(contract.subscribed_power.split(" ")[0]) * 1000
                for data in max_power_data:
                    if data.event_date is not None:
                        date = data.event_date.strftime("%A")
                        sub_prefix = f"{self.usage_point_id}/power_max/{date}"
                        mqtt_data[f"{sub_prefix}/date"] = data.event_date.strftime("%Y-%m-%d")
                        mqtt_data[f"{sub_prefix}/event_hour"] = data.event_date.strftime("%H:%M:%S")
                        mqtt_data[f"{sub_prefix}/value"] = data.value
                        value_w = data.value
                        if max_value != 0 and max_value >= value_w:
                            mqtt_data[f"{sub_prefix}/threshold_exceeded"] = 0
                            threshold_usage = int(100 * value_w / max_value)
                        else:
                            mqtt_data[f"{sub_prefix}/threshold_exceeded"] = 1
                            threshold_usage = int(0)
                        mqtt_data[f"{sub_prefix}/percentage_usage"] = threshold_usage
                self.mqtt_client.publish_multiple(mqtt_data)
                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def ecowatt(self):
        """Get the ecowatt data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Génération des données Ecowatt")
            begin = datetime.combine(datetime.now(tz=TIMEZONE_UTC) - relativedelta(days=1), datetime.min.time())
            end = begin + timedelta(days=7)
            ecowatt = DatabaseEcowatt().get_range(begin, end)
            today = datetime.combine(datetime.now(tz=TIMEZONE_UTC), datetime.min.time())
            mqtt_data = {}
            if ecowatt:
                for data in ecowatt:
                    if data.date == today:
                        queue = "j0"
                    elif data.date == today + timedelta(days=1):
                        queue = "j1"
                    else:
                        queue = "j2"
                    mqtt_data[f"ecowatt/{queue}/date"] = data.date.strftime(self.date_format_detail)
                    mqtt_data[f"ecowatt/{queue}/value"] = data.value
                    mqtt_data[f"ecowatt/{queue}/message"] = data.message
                    for date, value in ast.literal_eval(data.detail).items():
                        date_tmp = (
                            datetime.strptime(date, self.date_format_detail).astimezone(TIMEZONE_UTC).strftime("%H")
                        )
                        mqtt_data[f"ecowatt/{queue}/detail/{date_tmp}"] = value
                self.mqtt_client.publish_multiple(mqtt_data)
                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def tempo(self):  # noqa: C901
        """Get the tempo data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            logging.info("Envoie des données Tempo")
            mqtt_data = {}
            tempo_data = DatabaseStatistique(self.usage_point_id).get("price_consumption")
            tempo_price = DatabaseTempo().get_config("price")
            if tempo_price:
                for color, price in tempo_price.items():
                    mqtt_data[f"tempo/price/{color}"] = price
            tempo_days = DatabaseTempo().get_config("days")
            if tempo_days:
                for color, days in tempo_days.items():
                    mqtt_data[f"tempo/days/{color}"] = days
            today = datetime.combine(datetime.now(tz=TIMEZONE_UTC), datetime.min.time())
            tempo_color = DatabaseTempo().get_range(today, today)
            if tempo_color:
                mqtt_data["tempo/color/today"] = tempo_color[0].color
            tomorrow = today + timedelta(days=1)
            tempo_color = DatabaseTempo().get_range(tomorrow, tomorrow)
            if tempo_color:
                mqtt_data["tempo/color/tomorrow"] = tempo_color[0].color
            if tempo_data:
                for year, data in ast.literal_eval(tempo_data[0].value).items():
                    select_year = year
                    if year == datetime.now(tz=TIMEZONE_UTC).strftime("%Y"):
                        select_year = "current"
                    for color, tempo in data["TEMPO"].items():
                        mqtt_data[
                            f"{self.usage_point_id}/consumption/annual/{select_year}/thisYear/tempo/{color}/Wh"
                        ] = round(tempo["Wh"], 2)
                        mqtt_data[
                            f"{self.usage_point_id}/consumption/annual/{select_year}/thisYear/tempo/{color}/kWh"
                        ] = round(tempo["kWh"], 2)
                        mqtt_data[
                            f"{self.usage_point_id}/consumption/annual/{select_year}/thisYear/tempo/{color}/euro"
                        ] = round(tempo["euro"], 2)
                    for month, month_data in data["month"].items():
                        for month_color, month_tempo in month_data["TEMPO"].items():
                            if month == datetime.strftime(datetime.now(tz=TIMEZONE_UTC), "%m"):
                                if month_tempo:
                                    mqtt_data[
                                        f"{self.usage_point_id}/consumption/annual/{select_year}/thisMonth/tempo/{month_color}/Wh"
                                    ] = round(month_tempo["Wh"], 2)
                                    mqtt_data[
                                        f"{self.usage_point_id}/consumption/annual/{select_year}/thisMonth/tempo/{month_color}/kWh"
                                    ] = round(month_tempo["kWh"], 2)
                                    mqtt_data[
                                        f"{self.usage_point_id}/consumption/annual/{select_year}/thisMonth/tempo/{month_color}/euro"
                                    ] = round(month_tempo["euro"], 2)
                            if month_tempo:
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{select_year}/month/{int(month)}/tempo/{month_color}/Wh"
                                ] = round(month_tempo["Wh"], 2)
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{select_year}/month/{int(month)}/tempo/{month_color}/kWh"
                                ] = round(month_tempo["kWh"], 2)
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{select_year}/month/{int(month)}/tempo/{month_color}/euro"
                                ] = round(month_tempo["euro"], 2)
                self.mqtt_client.publish_multiple(mqtt_data)
                logging.info(" => OK")
            else:
                logging.info(" => Pas de donnée")

    def cleanup(self):
        """Cleanup MQTT connection."""
        if hasattr(self, "mqtt_client"):
            self.mqtt_client.disconnect()

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
