import ast
import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from dependencies import title
from init import CONFIG, DB, MQTT
from models.stat import Stat


class ExportMqtt:
    def __init__(self, usage_point_id):
        self.config = CONFIG
        self.db = DB
        self.usage_point_id = usage_point_id
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.mqtt = MQTT

    def status(self):
        logging.info("Statut du compte.")
        usage_point_id_config = self.db.get_usage_point(self.usage_point_id)
        # consentement_expiration_date = usage_point_id_config.consentement_expiration.strftime("%Y-%m-%d %H:%M:%S")
        if (
            hasattr(usage_point_id_config, "consentement_expiration")
            and usage_point_id_config.consentement_expiration is not None
        ):
            consentement_expiration_date = usage_point_id_config.consentement_expiration.strftime("%Y-%m-%d %H:%M:%S")
        else:
            consentement_expiration_date = ""
        if hasattr(usage_point_id_config, "call_number") and usage_point_id_config.call_number is not None:
            call_number = usage_point_id_config.call_number
        else:
            call_number = ""
        if hasattr(usage_point_id_config, "quota_reached") and usage_point_id_config.quota_reached is not None:
            quota_reached = usage_point_id_config.quota_reached
        else:
            quota_reached = ""
        if hasattr(usage_point_id_config, "quota_limit") and usage_point_id_config.quota_limit is not None:
            quota_limit = usage_point_id_config.quota_limit
        else:
            quota_limit = ""
        if hasattr(usage_point_id_config, "quota_reset_at") and usage_point_id_config.quota_reset_at is not None:
            quota_reset_at = (usage_point_id_config.quota_reset_at.strftime("%Y-%m-%d %H:%M:%S"),)
        else:
            quota_reset_at = ""
        if hasattr(usage_point_id_config, "last_call") and usage_point_id_config.last_call is not None:
            last_call = (usage_point_id_config.last_call.strftime("%Y-%m-%d %H:%M:%S"),)
        else:
            last_call = ""
        if hasattr(usage_point_id_config, "ban") and usage_point_id_config.ban is not None:
            ban = usage_point_id_config.ban
        else:
            ban = ""
        consentement_expiration = {
            f"{self.usage_point_id}/status/consentement_expiration": consentement_expiration_date,
            f"{self.usage_point_id}/status/call_number": str(call_number),
            f"{self.usage_point_id}/status/quota_reached": str(quota_reached),
            f"{self.usage_point_id}/status/quota_limit": str(quota_limit),
            f"{self.usage_point_id}/status/quota_reset_at": str(quota_reset_at),
            f"{self.usage_point_id}/status/last_call": str(last_call),
            f"{self.usage_point_id}/status/ban": str(ban),
        }
        # print(consentement_expiration)
        self.mqtt.publish_multiple(consentement_expiration)
        logging.info(" => OK")

    def contract(self):
        logging.info("Génération des messages du contrat")
        contract_data = self.db.get_contract(self.usage_point_id)
        if hasattr(contract_data, "__table__"):
            output = {}
            for column in contract_data.__table__.columns:
                output[f"{self.usage_point_id}/contract/{column.name}"] = str(getattr(contract_data, column.name))
            self.mqtt.publish_multiple(output)
            logging.info(" => OK")
        else:
            logging.info(" => ERREUR")

    def address(self):
        logging.info(f"Génération des messages d'addresse")
        address_data = self.db.get_addresse(self.usage_point_id)
        if hasattr(address_data, "__table__"):
            output = {}
            for column in address_data.__table__.columns:
                output[f"{self.usage_point_id}/address/{column.name}"] = str(getattr(address_data, column.name))
            self.mqtt.publish_multiple(output)
            logging.info(" => OK")
        else:
            logging.info(" => ERREUR")

    def daily_annual(self, price, measurement_direction="consumption"):
        logging.info("Génération des données annuelles")
        date_range = self.db.get_daily_date_range(self.usage_point_id)
        stat = Stat(self.usage_point_id, measurement_direction)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = datetime.combine(date_end.replace(month=1).replace(day=1), datetime.min.time())
            finish = False
            while not finish:
                year = int(date_begin_current.strftime("%Y"))
                get_daily_year = stat.get_year(year=year)
                get_daily_month = stat.get_month(year=year)
                get_daily_week = stat.get_week(year=year)
                if year == int(datetime.now().strftime("%Y")):
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
                    begin_day = datetime.strptime(stat.daily(week)["begin"], self.date_format).strftime("%A")
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
                date_end = datetime.combine(
                    (date_end - relativedelta(years=1)).replace(month=12, day=31),
                    datetime.max.time(),
                )
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = date_begin

                self.mqtt.publish_multiple(mqtt_data)

            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def daily_linear(self, price, measurement_direction="consumption"):
        logging.info("Génération des données linéaires journalières.")
        date_range = self.db.get_daily_date_range(self.usage_point_id)
        stat = Stat(self.usage_point_id, measurement_direction)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = date_end - relativedelta(years=1)
            idx = 0
            finish = False
            while not finish:
                if idx == 0:
                    key = "year"
                else:
                    key = f"year-{idx}"
                sub_prefix = f"{self.usage_point_id}/{measurement_direction}/linear/{key}"
                get_daily_year_linear = stat.get_year_linear(
                    idx,
                )
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
                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine((date_end - relativedelta(years=1)), datetime.max.time())
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = datetime.combine(date_begin, datetime.min.time())
                idx = idx + 1

                self.mqtt.publish_multiple(mqtt_data)

            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def detail_annual(self, price_hp, price_hc=0, measurement_direction="consumption"):
        logging.info("Génération des données annuelles détaillé.")
        date_range = self.db.get_daily_date_range(self.usage_point_id)
        stat = Stat(self.usage_point_id, measurement_direction)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = datetime.combine(date_end.replace(month=1).replace(day=1), datetime.min.time())
            finish = False
            while not finish:
                year = int(date_begin_current.strftime("%Y"))
                month = int(datetime.now().strftime("%m"))
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

                if year == int(datetime.now().strftime("%Y")):
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
                    begin_hp_day = datetime.strptime(stat.detail(week, "HP")["begin"], self.date_format).strftime("%A")
                    value_hp = stat.detail(week, "HP")["value"]
                    prefix = f"{sub_prefix}/week/{begin_hp_day}/hp"
                    mqtt_data[f"{prefix}/Wh"] = value_hp
                    mqtt_data[f"{prefix}/kWh"] = round(value_hp / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(value_hp / 1000 * price_hp, 2)
                    # HC
                    begin_hc_day = datetime.strptime(stat.detail(week, "HC")["begin"], self.date_format).strftime("%A")
                    value_hc = stat.detail(week, "HC")["value"]
                    prefix = f"{sub_prefix}/week/{begin_hc_day}/hc"
                    mqtt_data[f"{prefix}/Wh"] = value_hc
                    mqtt_data[f"{prefix}/kWh"] = round(value_hc / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(value_hc / 1000 * price_hc, 2)

                for month in range(12):
                    month = month + 1
                    # HP
                    get_detail_month_hp = stat.get_month(year=year, month=month, measure_type="HP")
                    prefix = f"{sub_prefix}/month/{month}/hp"
                    mqtt_data[f"{prefix}/Wh"] = get_detail_month_hp["value"]
                    mqtt_data[f"{prefix}/kWh"] = round(get_detail_month_hp["value"] / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(get_detail_month_hp["value"] / 1000 * price_hp, 2)
                    # HC
                    get_detail_month_hc = stat.get_month(year=year, month=month, measure_type="HC")
                    prefix = f"{sub_prefix}/month/{month}/hc"
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
                if date_begin_current < date_begin:
                    date_begin_current = date_begin

                self.mqtt.publish_multiple(mqtt_data)

            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def detail_linear(self, price_hp, price_hc=0, measurement_direction="consumption"):
        logging.info("Génération des données linéaires détaillées")
        date_range = self.db.get_detail_date_range(self.usage_point_id)
        stat = Stat(self.usage_point_id, measurement_direction)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
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
                    f"{sub_prefix}/thisYear/hp/euro": round(get_daily_year_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisYear/hc/Wh": get_daily_year_linear_hc["value"],
                    f"{sub_prefix}/thisYear/hc/kWh": round(get_daily_year_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/hc/euro": round(get_daily_year_linear_hc["value"] / 1000 * price_hc, 2),
                    # thisMonth
                    f"{sub_prefix}/thisMonth/hp/Wh": get_detail_month_linear_hp["value"],
                    f"{sub_prefix}/thisMonth/hp/kWh": round(get_detail_month_linear_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hp/euro": round(get_detail_month_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisMonth/hc/Wh": get_detail_month_linear_hc["value"],
                    f"{sub_prefix}/thisMonth/hc/kWh": round(get_detail_month_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hc/euro": round(get_detail_month_linear_hc["value"] / 1000 * price_hc, 2),
                    # thisWeek
                    f"{sub_prefix}/thisWeek/hp/Wh": get_detail_week_linear_hp["value"],
                    f"{sub_prefix}/thisWeek/hp/kWh": round(get_detail_week_linear_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hp/euro": round(get_detail_week_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisWeek/hc/Wh": get_detail_week_linear_hc["value"],
                    f"{sub_prefix}/thisWeek/hc/kWh": round(get_detail_week_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hc/euro": round(get_detail_week_linear_hc["value"] / 1000 * price_hc, 2),
                }

                # CALCUL NEW DATE
                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine((date_end - relativedelta(years=1)), datetime.max.time())
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = datetime.combine(date_begin, datetime.min.time())
                idx = idx + 1

                self.mqtt.publish_multiple(mqtt_data)
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def max_power(self):
        logging.info("Génération des données de puissance max journalières.")
        max_power_data = self.db.get_daily_max_power_all(self.usage_point_id, order="asc")
        mqtt_data = {}
        contract = self.db.get_contract(self.usage_point_id)
        max_value = 0
        if max_power_data:
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
                    else:
                        mqtt_data[f"{sub_prefix}/threshold_exceeded"] = 1
                    threshold_usage = int(100 * value_w / max_value)
                    mqtt_data[f"{sub_prefix}/percentage_usage"] = threshold_usage
            self.mqtt.publish_multiple(mqtt_data)
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def ecowatt(self):
        logging.info("Génération des données Ecowatt")
        begin = datetime.combine(datetime.now() - relativedelta(days=1), datetime.min.time())
        end = begin + timedelta(days=7)
        ecowatt = self.db.get_ecowatt_range(begin, end)
        today = datetime.combine(datetime.now(), datetime.min.time())
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
                    date = datetime.strptime(date, self.date_format_detail).strftime("%H")
                    mqtt_data[f"ecowatt/{queue}/detail/{date}"] = value
            self.mqtt.publish_multiple(mqtt_data)
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def tempo(self):
        logging.info("Envoie des données Tempo")
        mqtt_data = {}
        tempo_data = self.db.get_stat(self.usage_point_id, "price_consumption")
        tempo_price = self.db.get_tempo_config("price")
        if tempo_price:
            for color, price in tempo_price.items():
                mqtt_data[f"tempo/price/{color}"] = price
        tempo_days = self.db.get_tempo_config("days")
        if tempo_days:
            for color, days in tempo_days.items():
                mqtt_data[f"tempo/days/{color}"] = days
        today = datetime.combine(datetime.now(), datetime.min.time())
        tempo_color = self.db.get_tempo_range(today, today)
        if tempo_color:
            mqtt_data[f"tempo/color/today"] = tempo_color[0].color
        tomorrow = today + timedelta(days=1)
        tempo_color = self.db.get_tempo_range(tomorrow, tomorrow)
        if tempo_color:
            mqtt_data[f"tempo/color/tomorrow"] = tempo_color[0].color
        if tempo_data:
            for year, data in ast.literal_eval(tempo_data[0].value).items():
                if year == datetime.now().strftime("%Y"):
                    year = "current"
                for color, tempo in data["TEMPO"].items():
                    mqtt_data[f"{self.usage_point_id}/consumption/annual/{year}/thisYear/tempo/{color}/Wh"] = round(
                        tempo["Wh"], 2
                    )
                    mqtt_data[f"{self.usage_point_id}/consumption/annual/{year}/thisYear/tempo/{color}/kWh"] = round(
                        tempo["kWh"], 2
                    )
                    mqtt_data[f"{self.usage_point_id}/consumption/annual/{year}/thisYear/tempo/{color}/euro"] = round(
                        tempo["euro"], 2
                    )
                for month, month_data in data["month"].items():
                    for month_color, month_tempo in month_data["TEMPO"].items():
                        if month == datetime.strftime(datetime.now(), "%m"):
                            if month_tempo:
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{year}/thisMonth/tempo/{month_color}/Wh"
                                ] = round(month_tempo["Wh"], 2)
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{year}/thisMonth/tempo/{month_color}/kWh"
                                ] = round(month_tempo["kWh"], 2)
                                mqtt_data[
                                    f"{self.usage_point_id}/consumption/annual/{year}/thisMonth/tempo/{month_color}/euro"
                                ] = round(month_tempo["euro"], 2)
                        if month_tempo:
                            mqtt_data[
                                f"{self.usage_point_id}/consumption/annual/{year}/month/{int(month)}/tempo/{month_color}/Wh"
                            ] = round(month_tempo["Wh"], 2)
                            mqtt_data[
                                f"{self.usage_point_id}/consumption/annual/{year}/month/{int(month)}/tempo/{month_color}/kWh"
                            ] = round(month_tempo["kWh"], 2)
                            mqtt_data[
                                f"{self.usage_point_id}/consumption/annual/{year}/month/{int(month)}/tempo/{month_color}/euro"
                            ] = round(month_tempo["euro"], 2)
            self.mqtt.publish_multiple(mqtt_data)
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")
