import json
import logging
from datetime import datetime, timedelta
from math import floor

import pytz
from dateutil.relativedelta import relativedelta

from dependencies import get_version
from init import MQTT, DB, CONFIG
from models.stat import Stat

utc = pytz.UTC


def convert_kw(value):
    return truncate(value / 1000, 2)


def convert_kw_to_euro(value, price):
    if type(price) == str:
        price = float(price.replace(",", "."))
    return round(value / 1000 * price, 1)


def truncate(f, n):
    return floor(f * 10 ** n) / 10 ** n


def convert_price(price):
    if type(price) == str:
        price = price.replace(",", ".")
    return float(price)


class HomeAssistant:

    def __init__(self, usage_point_id):
        self.db = DB
        # self.mqtt_config = mqtt_config
        self.usage_point_id = usage_point_id
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.config = self.db.get_usage_point(self.usage_point_id)
        if hasattr(self.config, "consumption_price_base"):
            self.consumption_price_base = self.config.consumption_price_base
        else:
            self.consumption_price_base = 0
        if hasattr(self.config, "consumption_price_hp"):
            self.consumption_price_hp = self.config.consumption_price_hp
        else:
            self.consumption_price_hp = 0
        if hasattr(self.config, "consumption_price_hc"):
            self.consumption_price_hc = self.config.consumption_price_hc
        else:
            self.consumption_price_hc = 0
        if hasattr(self.config, "production_price"):
            self.production_price = self.config.production_price
        else:
            self.production_price = 0
        self.config_ha_config = CONFIG.home_assistant_config()
        if "card_myenedis" not in self.config_ha_config:
            self.card_myenedis = False
        else:
            self.card_myenedis = self.config_ha_config["card_myenedis"]
        if "discovery" not in self.config_ha_config:
            self.discovery = False
        else:
            self.discovery = self.config_ha_config["discovery"]
        if "discovery_prefix" not in self.config_ha_config:
            self.discovery_prefix = "home_assistant"
        else:
            self.discovery_prefix = self.config_ha_config["discovery_prefix"]
        if "enable" not in self.config_ha_config:
            self.enable = False
        else:
            self.enable = self.config_ha_config["enable"]
        if "hourly" not in self.config_ha_config:
            self.hourly = False
        else:
            self.hourly = self.config_ha_config["hourly"]
        self.contract = self.db.get_contract(self.usage_point_id)
        if hasattr(self.contract, "last_activation_date"):
            self.activation_date = self.contract.last_activation_date.strftime(self.date_format_detail)
        else:
            self.activation_date = None
        if hasattr(self.contract, "subscribed_power"):
            self.subscribed_power = self.contract.subscribed_power
        else:
            self.subscribed_power = None
        self.usage_point = self.db.get_usage_point(self.usage_point_id)
        self.mqtt = MQTT
        self.tempo_color = None

    def export(self):
        if (hasattr(self.config, "consumption") and self.config.consumption
                or (hasattr(self.config, "consumption_detail") and self.config.consumption_detail)):
            logging.info("Consommation :")
            self.myelectricaldata_usage_point_id("consumption")
            self.last_x_day(5, "consumption")
            self.history_usage_point_id("consumption")

        if (hasattr(self.config, "production") and self.config.production
                or (hasattr(self.config, "production_detail") and self.config.production_detail)):
            logging.info("Production :")
            self.myelectricaldata_usage_point_id("production")
            self.last_x_day(5, "production")
            self.history_usage_point_id("production")

        tempo_config = CONFIG.tempo_config()
        if tempo_config and "enable" in tempo_config and tempo_config["enable"]:
            self.tempo()
            self.tempo_info()
            self.tempo_days()
            self.tempo_price()
            self.ecowatt()

    def sensor(self, **kwargs):
        logging.info(f"- sensor.{kwargs['device_name'].lower().replace(' ', '_')}_{kwargs['uniq_id']}")
        topic = f"{self.discovery_prefix}/sensor/{kwargs['topic']}"
        if "device_class" not in kwargs:
            device_class = None
        else:
            device_class = kwargs["device_class"]
        config = {
            "name": f"{kwargs['name']}",
            "uniq_id": kwargs['uniq_id'],
            "stat_t": f"{topic}/state",
            "json_attr_t": f"{topic}/attributes",
            "device_class": device_class,
            "device": {
                "identifiers": kwargs['device_identifiers'],
                "name": kwargs['device_name'],
                "model": kwargs['device_model'],
                "manufacturer": "MyElectricalData"
            }
        }
        from pprint import pprint
        pprint(config)
        if "unit_of_measurement" in kwargs:
            config["unit_of_measurement"] = kwargs["unit_of_measurement"]
        if "numPDL" in kwargs:
            config["numPDL"] = kwargs["numPDL"]
        attributes_params = {}
        if "attributes" in kwargs:
            attributes_params = kwargs["attributes"]
        attributes = {
            **attributes_params,
            **{
                "version": get_version(),
                "activationDate": self.activation_date,
                "lastUpdate": datetime.now().strftime(self.date_format_detail),
                "timeLastCall": datetime.now().strftime(self.date_format_detail),
            }
        }

        data = {
            "config": json.dumps(config),
            "state": kwargs["state"],
            "attributes": json.dumps(attributes)
        }
        return self.mqtt.publish_multiple(data, topic)

    # sensor.linky_01226049119129_myelectricaldata_consumption_01226049119129_history
    def last_x_day(self, days, measurement_direction):
        uniq_id = f"linky_{measurement_direction}_last{days}day"
        end = datetime.combine(datetime.now() - timedelta(days=1), datetime.max.time())
        begin = datetime.combine(end - timedelta(days), datetime.min.time())
        range = self.db.get_detail_range(self.usage_point_id, begin, end, measurement_direction)
        attributes = {"time": [], measurement_direction: []}
        for data in range:
            attributes["time"].append(data.date.strftime("%Y-%m-%d %H:%M:%S"))
            attributes[measurement_direction].append(data.value)
        self.sensor(
            topic=f"myelectricaldata_{measurement_direction}_last_{days}_day/{self.usage_point_id}",
            name=f"{measurement_direction}.last{days}day",
            device_name=f"Linky {self.usage_point_id}",
            device_model=f"linky {self.usage_point_id}",
            device_identifiers=f"{self.usage_point_id}",
            uniq_id=uniq_id,
            unit_of_measurement="kWh",
            attributes=attributes,
            state=days,
            device_class="energy",
            numPDL=self.usage_point_id
        )

    def history_usage_point_id(self, measurement_direction):
        uniq_id = f"linky_{measurement_direction}_history"
        stats = Stat(self.usage_point_id, measurement_direction)
        state = self.db.get_daily_last(self.usage_point_id, measurement_direction)
        if state:
            state = state.value
        else:
            state = 0
        state = convert_kw(state)
        attributes = {
            "yesterdayDate": stats.daily(0)["begin"]
        }
        self.sensor(
            topic=f"myelectricaldata_{measurement_direction}_history/{self.usage_point_id}",
            name=f"{measurement_direction}.history",
            device_name=f"Linky {self.usage_point_id}",
            device_model=f"linky {self.usage_point_id}",
            device_identifiers=f"{self.usage_point_id}",
            uniq_id=uniq_id,
            unit_of_measurement="kWh",
            attributes=attributes,
            state=state,
            device_class="energy",
            numPDL=self.usage_point_id
        )

    def myelectricaldata_usage_point_id(self, measurement_direction):
        stats = Stat(self.usage_point_id, measurement_direction)
        state = self.db.get_daily_last(self.usage_point_id, measurement_direction)
        if state:
            state = state.value
        else:
            state = 0
        offpeak_hours_enedis = ""
        offpeak_hours = []
        if (
                hasattr(self.usage_point, "offpeak_hours_0") and self.usage_point.offpeak_hours_0 is not None or
                hasattr(self.usage_point, "offpeak_hours_1") and self.usage_point.offpeak_hours_1 is not None or
                hasattr(self.usage_point, "offpeak_hours_2") and self.usage_point.offpeak_hours_2 is not None or
                hasattr(self.usage_point, "offpeak_hours_3") and self.usage_point.offpeak_hours_3 is not None or
                hasattr(self.usage_point, "offpeak_hours_4") and self.usage_point.offpeak_hours_4 is not None or
                hasattr(self.usage_point, "offpeak_hours_5") and self.usage_point.offpeak_hours_5 is not None or
                hasattr(self.usage_point, "offpeak_hours_6") and self.usage_point.offpeak_hours_6 is not None
        ):
            offpeak_hours_enedis = (
                f"Lundi ({self.usage_point.offpeak_hours_0});"
                f"Mardi ({self.usage_point.offpeak_hours_1});"
                f"Mercredi ({self.usage_point.offpeak_hours_2});"
                f"Jeudi ({self.usage_point.offpeak_hours_3});"
                f"Vendredi ({self.usage_point.offpeak_hours_4});"
                f"Samedi ({self.usage_point.offpeak_hours_5});"
                f"Dimanche ({self.usage_point.offpeak_hours_6});"
            )

            idx = 0
            while idx <= 6:
                _offpeak_hours = []
                offpeak_hour = getattr(self.usage_point, f"offpeak_hours_{idx}")
                if type(offpeak_hour) != str:
                    logging.error([
                        f"offpeak_hours_{idx} n'est pas une chaine de caractères",
                        "  Format si une seule période : 00H00-06H00",
                        "  Format si plusieurs périodes : 00H00-06H00;12H00-14H00"
                    ])
                else:
                    for offpeak_hours_data in getattr(self.usage_point, f"offpeak_hours_{idx}").split(";"):
                        if type(offpeak_hours_data) == str:
                            _offpeak_hours.append(offpeak_hours_data.split("-"))

                offpeak_hours.append(_offpeak_hours)
                idx = idx + 1

        yesterday = datetime.combine(datetime.now() - relativedelta(days=1), datetime.max.time())
        previous_week = datetime.combine(yesterday - relativedelta(days=7), datetime.min.time())
        yesterday_last_year = yesterday - relativedelta(years=1)

        info = {
            "yesterday": yesterday.strftime(self.date_format),
            "previous_week": previous_week.strftime(self.date_format),
            "yesterday_last_year": yesterday_last_year.strftime(self.date_format)
        }

        # current_week
        current_week = stats.current_week()
        current_week_value = current_week["value"]
        info["current_week"] = {
            "begin": current_week["begin"],
            "end": current_week["end"]
        }
        # last_week
        last_week = stats.last_week()
        last_week_value = last_week["value"]
        info["last_week"] = {
            "begin": last_week["begin"],
            "end": last_week["end"]
        }
        # current_week_last_year
        current_week_last_year = stats.current_week_last_year()
        current_week_last_year_value = current_week_last_year["value"]
        info["current_week_last_year"] = {
            "begin": current_week_last_year["begin"],
            "end": current_week_last_year["end"]
        }
        # last_month
        last_month = stats.last_month()
        last_month_value = last_month["value"]
        info["last_month"] = {
            "begin": last_month["begin"],
            "end": last_month["end"]
        }
        # current_month
        current_month = stats.current_month()
        current_month_value = current_month["value"]
        info["current_month"] = {
            "begin": current_month["begin"],
            "end": current_month["end"]
        }
        # current_month_last_year
        current_month_last_year = stats.current_month_last_year()
        current_month_last_year_value = current_month_last_year["value"]
        info["current_month_last_year"] = {
            "begin": current_month_last_year["begin"],
            "end": current_month_last_year["end"]
        }
        # last_month_last_year
        last_month_last_year = stats.last_month_last_year()
        last_month_last_year_value = last_month_last_year["value"]
        info["last_month_last_year"] = {
            "begin": last_month_last_year["begin"],
            "end": last_month_last_year["end"]
        }
        # current_year
        current_year = stats.current_year()
        current_year_value = current_year["value"]
        info["current_year"] = {
            "begin": current_year["begin"],
            "end": current_year["end"]
        }
        # current_year_last_year
        current_year_last_year = stats.current_year_last_year()
        current_year_last_year_value = current_year_last_year["value"]
        info["current_year_last_year"] = {
            "begin": current_year_last_year["begin"],
            "end": current_year_last_year["end"]
        }
        # last_year
        last_year = stats.last_year()
        last_year_value = last_year["value"]
        info["last_year"] = {
            "begin": last_year["begin"],
            "end": last_year["end"]
        }
        # yesterday_hc_hp
        yesterday_hc_hp = stats.yesterday_hc_hp()
        yesterday_hc_value = yesterday_hc_hp["value"]["hc"]
        yesterday_hp_value = yesterday_hc_hp["value"]["hp"]
        info["yesterday_hc_hp"] = {
            "begin": yesterday_hc_hp["begin"],
            "end": yesterday_hc_hp["end"]
        }

        # evolution
        peak_offpeak_percent = stats.peak_offpeak_percent()
        current_week_evolution = stats.current_week_evolution()
        current_month_evolution = stats.current_month_evolution()
        yesterday_evolution = stats.yesterday_evolution()
        monthly_evolution = stats.monthly_evolution()
        yearly_evolution = stats.yearly_evolution()

        # LOG.show(yesterday_last_year)

        yesterday_last_year = self.db.get_daily_date(
            self.usage_point_id,
            datetime.combine(yesterday_last_year, datetime.min.time())
        )

        # LOG.show(yesterday_last_year)

        dailyweek_cost = []
        dailyweek_HP = []
        dailyweek_costHP = []
        dailyweek_HC = []
        dailyweek_costHC = []
        yesterday_hp_value_cost = 0
        if measurement_direction == "consumption":
            daily_cost = 0
            if hasattr(self.config, "plan") and self.config.plan.upper() == "HC/HP":
                for i in range(7):
                    hp = stats.detail(i, "HP")["value"]
                    hc = stats.detail(i, "HC")["value"]
                    dailyweek_HP.append(convert_kw(hp))
                    dailyweek_HC.append(convert_kw(hc))
                    cost_hp = convert_kw_to_euro(hp, self.consumption_price_hp)
                    cost_hc = convert_kw_to_euro(hc, self.consumption_price_hc)
                    dailyweek_costHP.append(cost_hp)
                    dailyweek_costHC.append(cost_hc)
                    value = cost_hp + cost_hc
                    if i == 0:
                        daily_cost = value
                    elif i == 1:
                        yesterday_hp_value_cost = convert_kw_to_euro(hp, self.consumption_price_hp)
                    dailyweek_cost.append(round(value, 1))
            elif hasattr(self.config, "plan") and self.config.plan.upper() == "TEMPO":
                tempo_config = self.db.get_tempo_config("price")
                for i in range(7):
                    tempo_data = stats.tempo(i)["value"]
                    hp = tempo_data["blue_hp"] + tempo_data["white_hp"] + tempo_data["red_hp"]
                    hc = tempo_data["blue_hc"] + tempo_data["white_hc"] + tempo_data["red_hc"]
                    dailyweek_HP.append(convert_kw(hp))
                    dailyweek_HC.append(convert_kw(hc))
                    cost_hp = (
                            convert_kw_to_euro(tempo_data["blue_hp"], convert_price(tempo_config["blue_hp"]))
                            + convert_kw_to_euro(tempo_data["white_hp"], convert_price(tempo_config["white_hp"]))
                            + convert_kw_to_euro(tempo_data["red_hp"], convert_price(tempo_config["red_hp"]))
                    )
                    cost_hc = (
                            convert_kw_to_euro(tempo_data["blue_hc"], convert_price(tempo_config["blue_hc"]))
                            + convert_kw_to_euro(tempo_data["white_hc"], convert_price(tempo_config["white_hc"]))
                            + convert_kw_to_euro(tempo_data["red_hc"], convert_price(tempo_config["red_hc"]))
                    )
                    dailyweek_costHP.append(cost_hp)
                    dailyweek_costHC.append(cost_hc)
                    value = cost_hp + cost_hc
                    if i == 0:
                        daily_cost = value
                    elif i == 1:
                        yesterday_hp_value_cost = cost_hp
                    dailyweek_cost.append(round(value, 1))
            else:
                for i in range(7):
                    hp = stats.detail(i, "HP")["value"]
                    hc = stats.detail(i, "HC")["value"]
                    dailyweek_HP.append(convert_kw(hp))
                    dailyweek_HC.append(convert_kw(hc))
                    dailyweek_costHP.append(convert_kw_to_euro(hp, self.consumption_price_base))
                    dailyweek_costHC.append(convert_kw_to_euro(hc, self.consumption_price_base))
                    dailyweek_cost.append(convert_kw_to_euro(stats.daily(i)["value"], self.consumption_price_base))
                    if i == 0:
                        daily_cost = convert_kw_to_euro(stats.daily(0)["value"], self.consumption_price_base)
                    elif i == 1:
                        yesterday_hp_value_cost = convert_kw_to_euro(hp, self.consumption_price_base)
        else:
            daily_cost = convert_kw_to_euro(stats.daily(0)["value"], self.production_price)
            for i in range(7):
                dailyweek_cost.append(convert_kw_to_euro(stats.daily(i)["value"], self.production_price))

        if not dailyweek_HP:
            dailyweek_HP = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_costHP:
            dailyweek_costHP = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_HC:
            dailyweek_HC = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_costHC:
            dailyweek_costHC = [0, 0, 0, 0, 0, 0, 0, 0]

        yesterday_consumption_max_power = 0
        if hasattr(self.config, "consumption_max_power") and self.config.consumption_max_power:
            yesterday_consumption_max_power = stats.max_power(0)["value"]

        error_last_call = self.db.get_error_log(self.usage_point_id)
        if error_last_call is None:
            error_last_call = ""

        attributes = {
            "yesterdayDate": stats.daily(0)["begin"],
            "yesterday": convert_kw(stats.daily(0)["value"]),
            "serviceEnedis": "myElectricalData",
            "yesterdayLastYearDate": (datetime.now() - relativedelta(years=1)).strftime(self.date_format),
            "yesterdayLastYear": convert_kw(yesterday_last_year.value) if hasattr(yesterday_last_year,
                                                                                  "value") else 0,
            "daily": [
                convert_kw(stats.daily(0)["value"]),
                convert_kw(stats.daily(1)["value"]),
                convert_kw(stats.daily(2)["value"]),
                convert_kw(stats.daily(3)["value"]),
                convert_kw(stats.daily(4)["value"]),
                convert_kw(stats.daily(5)["value"]),
                convert_kw(stats.daily(6)["value"])
            ],
            "current_week": convert_kw(current_week_value),
            "last_week": convert_kw(last_week_value),
            "day_1": convert_kw(stats.daily(0)["value"]),
            "day_2": convert_kw(stats.daily(1)["value"]),
            "day_3": convert_kw(stats.daily(2)["value"]),
            "day_4": convert_kw(stats.daily(3)["value"]),
            "day_5": convert_kw(stats.daily(4)["value"]),
            "day_6": convert_kw(stats.daily(5)["value"]),
            "day_7": convert_kw(stats.daily(6)["value"]),
            "current_week_last_year": convert_kw(current_week_last_year_value),
            "last_month": convert_kw(last_month_value),
            "current_month": convert_kw(current_month_value),
            "current_month_last_year": convert_kw(current_month_last_year_value),
            "last_month_last_year": convert_kw(last_month_last_year_value),
            "last_year": convert_kw(last_year_value),
            "current_year": convert_kw(current_year_value),
            "current_year_last_year": convert_kw(current_year_last_year_value),
            "dailyweek": [
                stats.daily(0)["begin"],
                stats.daily(1)["begin"],
                stats.daily(2)["begin"],
                stats.daily(3)["begin"],
                stats.daily(4)["begin"],
                stats.daily(5)["begin"],
                stats.daily(6)["begin"],
            ],
            "dailyweek_cost": dailyweek_cost,
            # TODO : If current_day = 0, dailyweek_hp & dailyweek_hc just next day...
            "dailyweek_costHP": dailyweek_costHP,
            "dailyweek_HP": dailyweek_HP,
            "dailyweek_costHC": dailyweek_costHC,
            "dailyweek_HC": dailyweek_HC,
            "daily_cost": daily_cost,
            "yesterday_HP_cost": yesterday_hp_value_cost,
            "yesterday_HP": convert_kw(yesterday_hp_value),
            "day_1_HP": stats.detail(0, "HP")["value"],
            "day_2_HP": stats.detail(1, "HP")["value"],
            "day_3_HP": stats.detail(2, "HP")["value"],
            "day_4_HP": stats.detail(3, "HP")["value"],
            "day_5_HP": stats.detail(4, "HP")["value"],
            "day_6_HP": stats.detail(5, "HP")["value"],
            "day_7_HP": stats.detail(6, "HP")["value"],

            "yesterday_HC_cost": convert_kw_to_euro(yesterday_hc_value, self.consumption_price_hc),
            "yesterday_HC": convert_kw(yesterday_hc_value),
            "day_1_HC": stats.detail(0, "HC")["value"],
            "day_2_HC": stats.detail(1, "HC")["value"],
            "day_3_HC": stats.detail(2, "HC")["value"],
            "day_4_HC": stats.detail(3, "HC")["value"],
            "day_5_HC": stats.detail(4, "HC")["value"],
            "day_6_HC": stats.detail(5, "HC")["value"],
            "day_7_HC": stats.detail(6, "HC")["value"],
            "peak_offpeak_percent": round(peak_offpeak_percent, 2),
            "yesterdayConsumptionMaxPower": yesterday_consumption_max_power,
            "dailyweek_MP": [
                convert_kw(stats.max_power(0)["value"]),
                convert_kw(stats.max_power(1)["value"]),
                convert_kw(stats.max_power(2)["value"]),
                convert_kw(stats.max_power(3)["value"]),
                convert_kw(stats.max_power(4)["value"]),
                convert_kw(stats.max_power(5)["value"]),
                convert_kw(stats.max_power(6)["value"]),
            ],
            "dailyweek_MP_time": [
                (stats.max_power_time(0)["value"]),
                (stats.max_power_time(1)["value"]),
                (stats.max_power_time(2)["value"]),
                (stats.max_power_time(3)["value"]),
                (stats.max_power_time(4)["value"]),
                (stats.max_power_time(5)["value"]),
                (stats.max_power_time(6)["value"]),
            ],
            "dailyweek_MP_over": [
                stats.max_power_over(0)["value"],
                stats.max_power_over(1)["value"],
                stats.max_power_over(2)["value"],
                stats.max_power_over(3)["value"],
                stats.max_power_over(4)["value"],
                stats.max_power_over(5)["value"],
                stats.max_power_over(6)["value"],
            ],
            "monthly_evolution": round(monthly_evolution, 2),
            "current_week_evolution": round(current_week_evolution, 2),
            "current_month_evolution": round(current_month_evolution, 2),
            "yesterday_evolution": round(yesterday_evolution, 2),
            "yearly_evolution": round(yearly_evolution, 2),
            "friendly_name": f"myelectricaldata.{self.usage_point_id}",
            "errorLastCall": error_last_call,
            "errorLastCallInterne": "",
            "current_week_number": yesterday.strftime("%V"),
            "offpeak_hours_enedis": offpeak_hours_enedis,
            "offpeak_hours": offpeak_hours,
            "subscribed_power": self.subscribed_power,
            # "info": info
        }

        uniq_id = f"linky_{measurement_direction}"
        self.sensor(
            topic=f"myelectricaldata_{measurement_direction}/{self.usage_point_id}",
            name=f"{measurement_direction}",
            device_name=f"Linky {self.usage_point_id}",
            device_model=f"linky {self.usage_point_id}",
            device_identifiers=f"{self.usage_point_id}",
            uniq_id=uniq_id,
            unit_of_measurement="kWh",
            attributes=attributes,
            state=convert_kw(state),
            device_class="energy",
            numPDL=self.usage_point_id
        )

    def tempo(self):
        uniq_id = f"today"
        begin = datetime.combine(datetime.now(), datetime.min.time())
        end = datetime.combine(datetime.now(), datetime.max.time())
        tempo_data = self.db.get_tempo_range(begin, end, "asc")
        if tempo_data:
            date = tempo_data[0].date.strftime(self.date_format_detail)
            state = tempo_data[0].color
        else:
            date = begin.strftime(self.date_format_detail)
            state = "Inconnu"
        attributes = {
            "date": date
        }
        self.tempo_color = state
        self.sensor(
            topic=f"myelectricaldata_rte_tempo/today",
            name=f"Today",
            device_name=f"RTE Tempo",
            device_model="RTE",
            device_identifiers=f"rte_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=state
        )

        uniq_id = f"tomorrow"
        begin = begin + timedelta(days=1)
        end = end + timedelta(days=1)
        tempo_data = self.db.get_tempo_range(begin, end, "asc")
        if tempo_data:
            date = tempo_data[0].date.strftime(self.date_format_detail)
            state = tempo_data[0].color
        else:
            date = begin.strftime(self.date_format_detail)
            state = "Inconnu"
        attributes = {
            "date": date
        }
        self.sensor(
            topic=f"myelectricaldata_rte_tempo/tomorrow",
            name=f"Tomorrow",
            device_name=f"RTE Tempo",
            device_model="RTE",
            device_identifiers=f"rte_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=state
        )

    def tempo_days(self):
        tempo_days = self.db.get_tempo_config("days")
        for color, days in tempo_days.items():
            self.tempo_days_sensor(f"{color}", days)

    def tempo_days_sensor(self, color, days):
        uniq_id = f"days_{color}"
        self.sensor(
            topic=f"myelectricaldata_edf_tempo_days/{color}",
            name=f"Days{color.capitalize()}",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers=f"edf_tempo",
            uniq_id=uniq_id,
            state=days
        )

    def tempo_info(self):
        uniq_id = f"info"
        tempo_days = self.db.get_tempo_config("days")
        tempo_price = self.db.get_tempo_config("price")
        if 22 > int(datetime.now().strftime("%H")) < 6:
            measure_type = "hc"
        else:
            measure_type = "hp"
        current_price = None
        if self.tempo_color.lower() in ["blue", "white", "red"]:
            current_price = convert_price(tempo_price[f"{self.tempo_color.lower()}_{measure_type}"].replace(",", "."))
        attributes = {
            "days_blue": f'{tempo_days["blue"]} / 300',
            "days_white": f'{tempo_days["white"]} / 43',
            "days_red": f'{tempo_days["red"]} / 22',
            "price_blue_hp": convert_price(tempo_price["blue_hp"]),
            "price_blue_hc": convert_price(tempo_price["blue_hc"]),
            "price_white_hp": convert_price(tempo_price["white_hp"]),
            "price_white_hc": convert_price(tempo_price["white_hc"]),
            "price_red_hp": convert_price(tempo_price["red_hp"]),
            "price_red_hc": convert_price(tempo_price["red_hc"])

        }
        self.sensor(
            topic=f"myelectricaldata_edf_tempo/info",
            name=f"Info",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers=f"edf_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=current_price,
            unit_of_measurement="EUR/kWh"
        )

    def tempo_price(self):
        tempo_price = self.db.get_tempo_config("price")
        for color, price in tempo_price.items():
            self.tempo_price_sensor(f"{color}", float(price.replace(",", ".")),
                                    f"{color.split('_')[0].capitalize()}{color.split('_')[1].capitalize()}")

    def tempo_price_sensor(self, color, price, name):
        uniq_id = f"price_{color}"
        self.sensor(
            topic=f"myelectricaldata_edf_tempo_price/{color}",
            name=f"Price {name}",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers=f"edf_tempo",
            uniq_id=uniq_id,
            state=convert_price(price),
            unit_of_measurement="EUR/kWh"
        )

    def ecowatt(self):
        self.ecowatt_delta("J0", 0)
        self.ecowatt_delta("J1", 1)
        self.ecowatt_delta("J2", 2)

    def ecowatt_delta(self, name, delta):
        uniq_id = f"{name}"
        current_date = datetime.combine(datetime.now(), datetime.min.time()) + timedelta(days=delta)
        fetch_date = current_date - timedelta(days=1)
        ecowatt_data = self.db.get_ecowatt_range(fetch_date, fetch_date, "asc")
        dayValue = 0
        if ecowatt_data:
            forecast = {}
            for data in ecowatt_data:
                dayValue = data.value
                for date, value in json.loads(data.detail.replace("'", '"')).items():
                    date = datetime.strptime(date, self.date_format_detail)
                    forecast[f'{date.strftime("%H")} h'] = value
            attributes = {
                "date": current_date.strftime(self.date_format),
                "forecast": forecast,
            }
            self.sensor(
                topic=f"myelectricaldata_rte_ecowatt{name}/tempo",
                name=f"{name}",
                device_name="RTE EcoWatt",
                device_model="RTE",
                device_identifiers=f"rte_ecowatt",
                uniq_id=uniq_id,
                attributes=attributes,
                state=dayValue
            )
