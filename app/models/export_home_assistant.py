import __main__ as app
import json
from datetime import datetime, timezone, timedelta
from math import floor

import pytz
from dateutil.relativedelta import relativedelta

from models.log import Log
from models.stat import Stat

utc = pytz.UTC


def convert_kw(value):
    return truncate(value / 1000, 2)


def convert_kw_to_euro(value, price):
    return round(value / 1000 * price, 1)


def truncate(f, n):
    return floor(f * 10 ** n) / 10 ** n


class HomeAssistant:

    def __init__(self, usage_point_id, measurement_direction="consumption"):
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.config = app.DB.get_usage_point(usage_point_id)
        if hasattr(self.config, "consumption_price_base"):
            self.price_base = self.config.consumption_price_base
        else:
            self.price_base = 0
        if hasattr(self.config, "consumption_price_hp"):
            self.price_hp = self.config.consumption_price_hp
        else:
            self.price_hp = 0
        if hasattr(self.config, "consumption_price_hc"):
            self.price_hc = self.config.consumption_price_hc
        else:
            self.price_hc = 0
        self.config_ha_config = app.CONFIG.home_assistant_config()
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
        self.contract = app.DB.get_contract(self.usage_point_id)
        if hasattr(self.contract, "last_activation_date"):
            self.activation_date = self.contract.last_activation_date.strftime(self.date_format_detail)
        else:
            self.activation_date = None
        if hasattr(self.contract, "subscribed_power"):
            self.subscribed_power = self.contract.subscribed_power
        else:
            self.subscribed_power = None
        self.usage_point = app.DB.get_usage_point(self.usage_point_id)
        self.stat = Stat(self.usage_point_id)
    def export(self):

        app.LOG.title(f"[{self.usage_point_id}] Exportation des données dans Home Assistant (via MQTT)")
        self.myelectricaldata_usage_point_id()
        self.history_usage_point_id()
        self.last_x_day(5)

    def last_x_day(self, days):
        topic = f"{self.discovery_prefix}/sensor/myelectricaldata_last_{days}_day/{self.usage_point_id}"
        config = {
            "name": f"myelectricaldata_last{days}day_{self.usage_point_id}",
            "uniq_id": f"myelectricaldata_last{days}day.{self.usage_point_id}",
            "stat_t": f"{topic}/state",
            "json_attr_t": f"{topic}/attributes",
            "unit_of_measurement": "W",
            "device": {
                "identifiers": [
                    f"linky_history_{self.usage_point_id}"
                ],
                "name": f"Linky {self.usage_point_id}",
                "model": "Linky",
                "manufacturer": "MyElectricalData"
            }
        }
        config = json.dumps(config)
        state = days
        attributes = {
            "numPDL": self.usage_point_id,
            "activationDate": self.activation_date,
            "lastUpdate": datetime.now().strftime(self.date_format_detail),
            "timeLastCall": datetime.now().strftime(self.date_format_detail),
            "time": [],
            "consumption": []
        }
        end = datetime.now() - timedelta(days=1)
        begin = end - timedelta(days)
        range = app.DB.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction)
        for data in range:
            attributes["time"].append(data.date.strftime("%Y-%m-%d %H:%M:%S"))
            attributes["consumption"].append(data.value)
        attributes = json.dumps(attributes)

        data = {
            "config": config,
            "state": state,
            "attributes": attributes
        }
        app.MQTT.publish_multiple(data, topic)

    def history_usage_point_id(self):
        topic = f"{self.discovery_prefix}/sensor/myelectricaldata_history/{self.usage_point_id}"
        config = {
            "name": f"myelectricaldata_history_{self.usage_point_id}",
            "uniq_id": f"myelectricaldata_history.{self.usage_point_id}",
            "stat_t": f"{topic}/state",
            "json_attr_t": f"{topic}/attributes",
            "unit_of_measurement": "kWh",
            "device": {
                "identifiers": [
                    f"linky_history_{self.usage_point_id}"
                ],
                "name": f"Linky {self.usage_point_id}",
                "model": "Linky",
                "manufacturer": "MyElectricalData"
            }
        }
        config = json.dumps(config)

        state = app.DB.get_daily_last(self.usage_point_id, self.measurement_direction)
        if state:
            state = state.value
        else:
            state = 0
        state = convert_kw(state)

        attributes = {
            "numPDL": self.usage_point_id,
            "activationDate": self.activation_date,
            "lastUpdate": datetime.now().strftime(self.date_format_detail),
            "timeLastCall": datetime.now().strftime(self.date_format_detail),
            "yesterdayDate": self.stat.daily(0)["begin"]
        }
        attributes = json.dumps(attributes)
        data = {
            "config": config,
            "state": state,
            "attributes": attributes
        }
        app.MQTT.publish_multiple(data, topic)

    def myelectricaldata_usage_point_id(self):
        topic = f"{self.discovery_prefix}/sensor/myelectricaldata/{self.usage_point_id}"
        config = {
            f"config": json.dumps(
                {
                    "name": f"myelectricaldata_{self.usage_point_id}",
                    "uniq_id": f"myelectricaldata.{self.usage_point_id}",
                    "stat_t": f"{topic}/state",
                    "json_attr_t": f"{topic}/attributes",
                    "unit_of_measurement": "kWh",
                    "device": {
                        "identifiers": [
                            f"linky_{self.usage_point_id}"
                        ],
                        "name": f"Linky {self.usage_point_id}",
                        "model": "Linky",
                        "manufacturer": "MyElectricalData"
                    }
                })
        }
        app.MQTT.publish_multiple(config, topic)

        state = app.DB.get_daily_last(self.usage_point_id, self.measurement_direction)
        if state:
            state = state.value
        else:
            state = 0

        app.MQTT.publish_multiple({
            f"state": convert_kw(state)
        }, topic)

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
                    Log().error([
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
        current_week = self.stat.current_week("consumption")
        current_week_value = current_week["value"]
        info["current_week"] = {
            "begin": current_week["begin"],
            "end": current_week["end"]
        }
        # last_week
        last_week = self.stat.last_week("consumption")
        last_week_value = last_week["value"]
        info["last_week"] = {
            "begin": last_week["begin"],
            "end": last_week["end"]
        }
        # current_week_last_year
        current_week_last_year = self.stat.current_week_last_year("consumption")
        current_week_last_year_value = current_week_last_year["value"]
        info["current_week_last_year"] = {
            "begin": current_week_last_year["begin"],
            "end": current_week_last_year["end"]
        }
        # last_month
        last_month = self.stat.last_month("consumption")
        last_month_value = last_month["value"]
        info["last_month"] = {
            "begin": last_month["begin"],
            "end": last_month["end"]
        }
        # current_month
        current_month = self.stat.current_month("consumption")
        current_month_value = current_month["value"]
        info["current_month"] = {
            "begin": current_month["begin"],
            "end": current_month["end"]
        }
        # current_month_last_year
        current_month_last_year = self.stat.current_month_last_year("consumption")
        current_month_last_year_value = current_month_last_year["value"]
        info["current_month_last_year"] = {
            "begin": current_month_last_year["begin"],
            "end": current_month_last_year["end"]
        }
        # last_month_last_year
        last_month_last_year = self.stat.last_month_last_year("consumption")
        last_month_last_year_value = last_month_last_year["value"]
        info["last_month_last_year"] = {
            "begin": last_month_last_year["begin"],
            "end": last_month_last_year["end"]
        }
        # current_year
        current_year = self.stat.current_year("consumption")
        current_year_value = current_year["value"]
        info["current_year"] = {
            "begin": current_year["begin"],
            "end": current_year["end"]
        }
        # current_year_last_year
        current_year_last_year = self.stat.current_year_last_year("consumption")
        current_year_last_year_value = current_year_last_year["value"]
        info["current_year_last_year"] = {
            "begin": current_year_last_year["begin"],
            "end": current_year_last_year["end"]
        }
        # last_year
        last_year = self.stat.last_year("consumption")
        last_year_value = last_year["value"]
        info["last_year"] = {
            "begin": last_year["begin"],
            "end": last_year["end"]
        }
        # yesterday_hc_hp
        yesterday_hc_hp = self.stat.yesterday_hc_hp("consumption")
        yesterday_hc_value = yesterday_hc_hp["value"]["hc"]
        yesterday_hp_value = yesterday_hc_hp["value"]["hp"]
        info["yesterday_hc_hp"] = {
            "begin": yesterday_hc_hp["begin"],
            "end": yesterday_hc_hp["end"]
        }

        # evolution
        peak_offpeak_percent = self.stat.peak_offpeak_percent()
        current_week_evolution = self.stat.current_week_evolution()
        current_month_evolution = self.stat.current_month_evolution()
        yesterday_evolution = self.stat.yesterday_evolution()
        monthly_evolution = self.stat.monthly_evolution()

        yesterday_last_year = app.DB.get_daily_date(self.usage_point_id, yesterday_last_year)

        dailyweek_cost = []
        if hasattr(self.config, "plan") and self.config.plan.upper() == "HC/HP":
            daily_cost = (
                    convert_kw_to_euro(self.stat.detail(0, "HC")["value"], self.price_hc)
                    + convert_kw_to_euro(self.stat.detail(0, "HP")["value"], self.price_hp)
            )
            for i in range(7):
                value = (
                        convert_kw_to_euro(self.stat.detail(i, "HP")["value"], self.price_hp)
                        + convert_kw_to_euro(self.stat.detail(i, "HC")["value"], self.price_hc)
                )
                dailyweek_cost.append(round(value, 1))
        else:
            daily_cost = convert_kw_to_euro(self.stat.daily(0)["value"], self.price_base)
            for i in range(7):
                dailyweek_cost.append(convert_kw_to_euro(self.stat.daily(i)["value"], self.price_base))

        config = {
            f"attributes": json.dumps(
                {
                    "numPDL": self.usage_point_id,
                    "activationDate": self.activation_date,
                    "lastUpdate": datetime.now().strftime(self.date_format_detail),
                    "timeLastCall": datetime.now().strftime(self.date_format_detail),
                    "yesterdayDate": self.stat.daily(0)["begin"],
                    "yesterday": convert_kw(self.stat.daily(0)["value"]),
                    "yesterdayLastYearDate": (datetime.now() - relativedelta(years=1)).strftime(self.date_format),
                    "yesterdayLastYear": convert_kw(yesterday_last_year.value) if hasattr(yesterday_last_year,
                                                                                          "value") else 0,
                    "daily": [
                        convert_kw(self.stat.daily(0)["value"]),
                        convert_kw(self.stat.daily(1)["value"]),
                        convert_kw(self.stat.daily(2)["value"]),
                        convert_kw(self.stat.daily(3)["value"]),
                        convert_kw(self.stat.daily(4)["value"]),
                        convert_kw(self.stat.daily(5)["value"]),
                        convert_kw(self.stat.daily(6)["value"])
                    ],
                    "current_week": convert_kw(current_week_value),
                    "last_week": convert_kw(last_week_value),
                    "day_1": convert_kw(self.stat.daily(0)["value"]),
                    "day_2": convert_kw(self.stat.daily(1)["value"]),
                    "day_3": convert_kw(self.stat.daily(2)["value"]),
                    "day_4": convert_kw(self.stat.daily(3)["value"]),
                    "day_5": convert_kw(self.stat.daily(4)["value"]),
                    "day_6": convert_kw(self.stat.daily(5)["value"]),
                    "day_7": convert_kw(self.stat.daily(6)["value"]),
                    "current_week_last_year": convert_kw(current_week_last_year_value),
                    "last_month": convert_kw(last_month_value),
                    "current_month": convert_kw(current_month_value),
                    "current_month_last_year": convert_kw(current_month_last_year_value),
                    "last_month_last_year": convert_kw(last_month_last_year_value),
                    "last_year": convert_kw(last_year_value),
                    "current_year": convert_kw(current_year_value),
                    "current_year_last_year": convert_kw(current_year_last_year_value),
                    "dailyweek": [
                        self.stat.daily(0)["begin"],
                        self.stat.daily(1)["begin"],
                        self.stat.daily(2)["begin"],
                        self.stat.daily(3)["begin"],
                        self.stat.daily(4)["begin"],
                        self.stat.daily(5)["begin"],
                        self.stat.daily(6)["begin"],
                    ],
                    "dailyweek_cost": dailyweek_cost,
                    # TODO : If current_day = 0, dailyweek_hp & dailyweek_hc just next day...
                    "dailyweek_costHP": [
                        convert_kw_to_euro(self.stat.detail(0, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(1, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(2, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(3, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(4, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(5, "HP")["value"], self.price_hp),
                        convert_kw_to_euro(self.stat.detail(6, "HP")["value"], self.price_hp),
                    ],
                    "dailyweek_HP": [
                        convert_kw(self.stat.detail(0, "HP")["value"]),
                        convert_kw(self.stat.detail(1, "HP")["value"]),
                        convert_kw(self.stat.detail(2, "HP")["value"]),
                        convert_kw(self.stat.detail(3, "HP")["value"]),
                        convert_kw(self.stat.detail(4, "HP")["value"]),
                        convert_kw(self.stat.detail(5, "HP")["value"]),
                        convert_kw(self.stat.detail(6, "HP")["value"]),
                    ],
                    "daily_cost": daily_cost,
                    "yesterday_HP_cost": convert_kw_to_euro(yesterday_hp_value, self.price_hp),
                    "yesterday_HP": convert_kw(yesterday_hp_value),
                    "day_1_HP": self.stat.detail(0, "HP")["value"],
                    "day_2_HP": self.stat.detail(1, "HP")["value"],
                    "day_3_HP": self.stat.detail(2, "HP")["value"],
                    "day_4_HP": self.stat.detail(3, "HP")["value"],
                    "day_5_HP": self.stat.detail(4, "HP")["value"],
                    "day_6_HP": self.stat.detail(5, "HP")["value"],
                    "day_7_HP": self.stat.detail(6, "HP")["value"],
                    "dailyweek_costHC": [
                        convert_kw_to_euro(self.stat.detail(0, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(1, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(2, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(3, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(4, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(5, "HC")["value"], self.price_hc),
                        convert_kw_to_euro(self.stat.detail(6, "HC")["value"], self.price_hc),
                    ],
                    "dailyweek_HC": [
                        convert_kw(self.stat.detail(0, "HC")["value"]),
                        convert_kw(self.stat.detail(1, "HC")["value"]),
                        convert_kw(self.stat.detail(2, "HC")["value"]),
                        convert_kw(self.stat.detail(3, "HC")["value"]),
                        convert_kw(self.stat.detail(4, "HC")["value"]),
                        convert_kw(self.stat.detail(5, "HC")["value"]),
                        convert_kw(self.stat.detail(6, "HC")["value"]),
                    ],
                    "yesterday_HC_cost": convert_kw_to_euro(yesterday_hc_value, self.price_hc),
                    "yesterday_HC": convert_kw(yesterday_hc_value),
                    "day_1_HC": self.stat.detail(0, "HC")["value"],
                    "day_2_HC": self.stat.detail(1, "HC")["value"],
                    "day_3_HC": self.stat.detail(2, "HC")["value"],
                    "day_4_HC": self.stat.detail(3, "HC")["value"],
                    "day_5_HC": self.stat.detail(4, "HC")["value"],
                    "day_6_HC": self.stat.detail(5, "HC")["value"],
                    "day_7_HC": self.stat.detail(6, "HC")["value"],
                    "peak_offpeak_percent": round(peak_offpeak_percent, 2),
                    "monthly_evolution": round(monthly_evolution, 2),
                    "current_week_evolution": round(current_week_evolution, 2),
                    "current_month_evolution": round(current_month_evolution, 2),
                    "yesterday_evolution": round(yesterday_evolution, 2),
                    "friendly_name": f"myelectricaldata.{self.usage_point_id}",
                    "errorLastCall": "",
                    "errorLastCallInterne": "",
                    "current_week_number": yesterday.strftime("%V"),
                    "offpeak_hours_enedis": offpeak_hours_enedis,
                    "offpeak_hours": offpeak_hours,
                    "subscribed_power": self.subscribed_power
                })
        }
        for key, value in info.items():
            config[f"info/{key}"] = json.dumps(value)
        app.MQTT.publish_multiple(config, topic)
