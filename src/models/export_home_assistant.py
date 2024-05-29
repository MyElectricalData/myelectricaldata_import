"""This module contains the code for exporting data to Home Assistant."""

import json
import logging
from datetime import datetime, timedelta

import pytz
from dateutil.relativedelta import relativedelta

from dependencies import get_version, truncate
from init import CONFIG, DB, MQTT
from models.stat import Stat

UTC = pytz.UTC


def convert_kw(value):
    """Convert a value from kilowatts to watts.

    Args:
        value (float): The value in kilowatts.

    Returns:
        float: The value in watts.
    """
    return truncate(value / 1000, 2)


def convert_kw_to_euro(value, price):
    """Convert a value from kilowatts to euros.

    Args:
        value (float): The value in kilowatts.
        price (float): The price per kilowatt-hour.

    Returns:
        float: The value in euros.
    """
    if isinstance(price, str):
        price = float(price.replace(",", "."))
    return round(value / 1000 * price, 1)


def convert_price(price):
    """Convert a price from string to float.

    Args:
        price (str): The price as a string.

    Returns:
        float: The price as a float.
    """
    if isinstance(price, str):
        price = price.replace(",", ".")
    return float(price)


class HomeAssistant:  # pylint: disable=R0902
    """Represents a Home Assistant instance."""

    class Config:  # pylint: disable=R0902
        """Default configuration for Home Assistant."""

        def __init__(self) -> None:
            """Initialize the ExportHomeAssistant object.

            Attributes:
            - consumption (bool): Flag indicating if consumption data is enabled.
            - consumption_detail (bool): Flag indicating if detailed consumption data is enabled.
            - production (bool): Flag indicating if production data is enabled.
            - production_detail (bool): Flag indicating if detailed production data is enabled.
            - consumption_price_base (float): The base consumption price.
            - consumption_price_hp (float): The consumption price for high peak hours.
            - consumption_price_hc (float): The consumption price for low peak hours.
            - production_price (float): The production price.
            - discovery_prefix (str): The prefix for Home Assistant discovery.
            - activation_date (datetime): The date of the last activation.
            - subscribed_power (str): The subscribed power value.
            - consumption_max_power (bool): Flag indicating if maximum power consumption is enabled.
            - offpeak_hours_0 (str): Off-peak hours for day 0 - Monday.
            - offpeak_hours_1 (str): Off-peak hours for day 1 - Tuesday.
            - offpeak_hours_2 (str): Off-peak hours for day 2 - Wednesday.
            - offpeak_hours_3 (str): Off-peak hours for day 3 - Thursday.
            - offpeak_hours_4 (str): Off-peak hours for day 4 - Friday.
            - offpeak_hours_5 (str): Off-peak hours for day 5 - Saturday.
            - offpeak_hours_6 (str): Off-peak hours for day 6 - Sunday.
            """
            self.consumption: bool = True
            self.consumption_detail: bool = True
            self.production: bool = False
            self.production_detail: bool = False
            self.consumption_price_base: float = 0
            self.consumption_price_hp: float = 0
            self.consumption_price_hc: float = 0
            self.production_price: float = 0
            self.discovery_prefix: str = "home_assistant"
            self.activation_date: datetime = None
            self.subscribed_power: str = None
            self.consumption_max_power: bool = True
            self.offpeak_hours_0: str = None
            self.offpeak_hours_1: str = None
            self.offpeak_hours_2: str = None
            self.offpeak_hours_3: str = None
            self.offpeak_hours_4: str = None
            self.offpeak_hours_5: str = None
            self.offpeak_hours_6: str = None

    def __init__(self, usage_point_id):
        self.usage_point_id = usage_point_id
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.config_usage_point = DB.get_usage_point(self.usage_point_id)
        self.config = None
        self.load_config()
        self.usage_point = DB.get_usage_point(self.usage_point_id)
        self.mqtt = MQTT
        self.tempo_color = None

    def load_config(self):
        """Load the configuration for Home Assistant.

        This method loads the configuration values from the usage point and contract objects.
        """
        self.config = self.Config()
        for key in self.config.__dict__:
            if hasattr(self.config_usage_point, key):
                setattr(self.config, key, getattr(self.config_usage_point, key))

        config_ha_config = CONFIG.home_assistant_config()
        for key in self.config.__dict__:
            if key in config_ha_config:
                setattr(self.config, key, config_ha_config[key])

        contract = DB.get_contract(self.usage_point_id)
        for key in self.config.__dict__:
            if hasattr(contract, key):
                setattr(self.config, key, getattr(contract, key))

    def export(self):
        """Export data to Home Assistant.

        This method exports consumption, production, tempo, and ecowatt data to Home Assistant.
        """
        if self.config.consumption or self.config.consumption_detail:
            logging.info("Consommation :")
            self.myelectricaldata_usage_point_id("consumption")
            self.last_x_day(5, "consumption")
            self.history_usage_point_id("consumption")

        if self.config.production or self.config.production_detail:
            logging.info("Production :")
            self.myelectricaldata_usage_point_id("production")
            self.last_x_day(5, "production")
            self.history_usage_point_id("production")

        self.tempo()
        self.tempo_info()
        self.tempo_days()
        self.tempo_price()
        self.ecowatt()

    def sensor(self, **kwargs):
        """Publish sensor data to Home Assistant.

        This method publishes sensor data to Home Assistant using MQTT.
        """
        logging.info(
            f"- sensor.{kwargs['device_name'].lower().replace(' ', '_')}_{kwargs['name'].lower().replace(' ', '_')}"
        )
        topic = f"{self.config.discovery_prefix}/sensor/{kwargs['topic']}"
        if "device_class" not in kwargs:
            device_class = None
        else:
            device_class = kwargs["device_class"]
        config = {
            "name": f"{kwargs['name']}",
            "uniq_id": kwargs["uniq_id"],
            "stat_t": f"{topic}/state",
            "json_attr_t": f"{topic}/attributes",
            "device_class": device_class,
            "device": {
                "identifiers": kwargs["device_identifiers"],
                "name": kwargs["device_name"],
                "model": kwargs["device_model"],
                "manufacturer": "MyElectricalData",
            },
        }
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
                "activationDate": self.config.activation_date,
                "lastUpdate": datetime.now(tz=UTC).strftime(self.date_format_detail),
                "timeLastCall": datetime.now(tz=UTC).strftime(self.date_format_detail),
            },
        }

        data = {
            "config": json.dumps(config),
            "state": kwargs["state"],
            "attributes": json.dumps(attributes),
        }
        return self.mqtt.publish_multiple(data, topic)

    def last_x_day(self, days, measurement_direction):
        """Get data for the last x days and publish it to Home Assistant.

        Args:
            days (int): The number of days to retrieve data for.
            measurement_direction (str): The direction of the measurement (e.g., consumption or production).
        """
        uniq_id = f"myelectricaldata_linky_{self.usage_point_id}_{measurement_direction}_last{days}day"
        end = datetime.combine(datetime.now(tz=UTC) - timedelta(days=1), datetime.max.time())
        begin = datetime.combine(end - timedelta(days), datetime.min.time())
        range = DB.get_detail_range(self.usage_point_id, begin, end, measurement_direction)
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
            numPDL=self.usage_point_id,
        )

    def history_usage_point_id(self, measurement_direction):
        """Retrieve the historical usage point ID and publishes it to Home Assistant.

        Args:
            measurement_direction (str): The direction of the measurement (e.g., "consumption", "production").
        """
        uniq_id = f"myelectricaldata_linky_{self.usage_point_id}_{measurement_direction}_history"
        stats = Stat(self.usage_point_id, measurement_direction)
        state = DB.get_daily_last(self.usage_point_id, measurement_direction)
        if state:
            state = state.value
        else:
            state = 0
        state = convert_kw(state)
        attributes = {"yesterdayDate": stats.daily(0)["begin"]}
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
            numPDL=self.usage_point_id,
        )

    def myelectricaldata_usage_point_id(self, measurement_direction):  # noqa: PLR0912, PLR0915, C901
        """Retrieve the usage point ID and calculates various statistics related to energy consumption.

        Args:
            measurement_direction (str): The direction of the measurement (e.g., "consumption", "production").

        Returns:
            dict: A dictionary containing various statistics related to energy consumption, such as daily, weekly,
                  monthly, and yearly values.
        """
        stats = Stat(self.usage_point_id, measurement_direction)
        state = DB.get_daily_last(self.usage_point_id, measurement_direction)
        if state:
            state = state.value
        else:
            state = 0

        offpeak_hours_enedis = (
            f"Lundi ({self.config.offpeak_hours_0});"
            f"Mardi ({self.config.offpeak_hours_1});"
            f"Mercredi ({self.config.offpeak_hours_2});"
            f"Jeudi ({self.config.offpeak_hours_3});"
            f"Vendredi ({self.config.offpeak_hours_4});"
            f"Samedi ({self.config.offpeak_hours_5});"
            f"Dimanche ({self.config.offpeak_hours_6});"
        )

        offpeak_hours = []
        idx = 0
        while idx <= 6:
            _offpeak_hours = []
            offpeak_hour = getattr(self.config, f"offpeak_hours_{idx}")
            if not isinstance(offpeak_hour, str):
                logging.error(
                    [
                        f"offpeak_hours_{idx} n'est pas une chaine de caractères",
                        "  Format si une seule période : 00H00-06H00",
                        "  Format si plusieurs périodes : 00H00-06H00;12H00-14H00",
                    ]
                )
            else:
                for offpeak_hours_data in getattr(self.config, f"offpeak_hours_{idx}").split(";"):
                    if isinstance(offpeak_hours_data, str):
                        _offpeak_hours.append(offpeak_hours_data.split("-"))

            offpeak_hours.append(_offpeak_hours)
            idx = idx + 1

        yesterday = datetime.combine(datetime.now(tz=UTC) - relativedelta(days=1), datetime.max.time())
        previous_week = datetime.combine(yesterday - relativedelta(days=7), datetime.min.time())
        yesterday_last_year = yesterday - relativedelta(years=1)

        info = {
            "yesterday": yesterday.strftime(self.date_format),
            "previous_week": previous_week.strftime(self.date_format),
            "yesterday_last_year": yesterday_last_year.strftime(self.date_format),
        }

        # current_week
        current_week = stats.current_week()
        current_week_value = current_week["value"]
        info["current_week"] = {
            "begin": current_week["begin"],
            "end": current_week["end"],
        }
        # last_week
        last_week = stats.last_week()
        last_week_value = last_week["value"]
        info["last_week"] = {"begin": last_week["begin"], "end": last_week["end"]}
        # current_week_last_year
        current_week_last_year = stats.current_week_last_year()
        current_week_last_year_value = current_week_last_year["value"]
        info["current_week_last_year"] = {
            "begin": current_week_last_year["begin"],
            "end": current_week_last_year["end"],
        }
        # last_month
        last_month = stats.last_month()
        last_month_value = last_month["value"]
        info["last_month"] = {"begin": last_month["begin"], "end": last_month["end"]}
        # current_month
        current_month = stats.current_month()
        current_month_value = current_month["value"]
        info["current_month"] = {
            "begin": current_month["begin"],
            "end": current_month["end"],
        }
        # current_month_last_year
        current_month_last_year = stats.current_month_last_year()
        current_month_last_year_value = current_month_last_year["value"]
        info["current_month_last_year"] = {
            "begin": current_month_last_year["begin"],
            "end": current_month_last_year["end"],
        }
        # last_month_last_year
        last_month_last_year = stats.last_month_last_year()
        last_month_last_year_value = last_month_last_year["value"]
        info["last_month_last_year"] = {
            "begin": last_month_last_year["begin"],
            "end": last_month_last_year["end"],
        }
        # current_year
        current_year = stats.current_year()
        current_year_value = current_year["value"]
        info["current_year"] = {
            "begin": current_year["begin"],
            "end": current_year["end"],
        }
        # current_year_last_year
        current_year_last_year = stats.current_year_last_year()
        current_year_last_year_value = current_year_last_year["value"]
        info["current_year_last_year"] = {
            "begin": current_year_last_year["begin"],
            "end": current_year_last_year["end"],
        }
        # last_year
        last_year = stats.last_year()
        last_year_value = last_year["value"]
        info["last_year"] = {"begin": last_year["begin"], "end": last_year["end"]}
        # yesterday_hc_hp
        yesterday_hc_hp = stats.yesterday_hc_hp()
        yesterday_hc_value = yesterday_hc_hp["value"]["hc"]
        yesterday_hp_value = yesterday_hc_hp["value"]["hp"]
        info["yesterday_hc_hp"] = {
            "begin": yesterday_hc_hp["begin"],
            "end": yesterday_hc_hp["end"],
        }

        # evolution
        peak_offpeak_percent = stats.peak_offpeak_percent()
        current_week_evolution = stats.current_week_evolution()
        current_month_evolution = stats.current_month_evolution()
        yesterday_evolution = stats.yesterday_evolution()
        monthly_evolution = stats.monthly_evolution()
        yearly_evolution = stats.yearly_evolution()
        yesterday_last_year = DB.get_daily_date(
            self.usage_point_id,
            datetime.combine(yesterday_last_year, datetime.min.time()),
        )
        dailyweek_cost = []
        dailyweek_hp = []
        dailyweek_cost_hp = []
        dailyweek_hc = []
        dailyweek_cost_hc = []
        yesterday_hp_value_cost = 0
        if measurement_direction == "consumption":
            daily_cost = 0
            plan = DB.get_usage_point_plan(self.usage_point_id).upper()
            if plan in ("HC/HP", "HC/HP"):
                for i in range(7):
                    hp = stats.detail(i, "HP")["value"]
                    hc = stats.detail(i, "HC")["value"]
                    dailyweek_hp.append(convert_kw(hp))
                    dailyweek_hc.append(convert_kw(hc))
                    cost_hp = convert_kw_to_euro(hp, self.config.consumption_price_hp)
                    cost_hc = convert_kw_to_euro(hc, self.config.consumption_price_hc)
                    dailyweek_cost_hp.append(cost_hp)
                    dailyweek_cost_hc.append(cost_hc)
                    value = cost_hp + cost_hc
                    if i == 0:
                        daily_cost = value
                    elif i == 1:
                        yesterday_hp_value_cost = convert_kw_to_euro(hp, self.config.consumption_price_hp)
                    dailyweek_cost.append(round(value, 1))
            elif plan == "TEMPO":
                tempo_config = DB.get_tempo_config("price")
                for i in range(7):
                    tempo_data = stats.tempo(i)["value"]
                    hp = tempo_data["blue_hp"] + tempo_data["white_hp"] + tempo_data["red_hp"]
                    hc = tempo_data["blue_hc"] + tempo_data["white_hc"] + tempo_data["red_hc"]
                    dailyweek_hp.append(convert_kw(hp))
                    dailyweek_hc.append(convert_kw(hc))
                    cost_hp = (
                        convert_kw_to_euro(
                            tempo_data["blue_hp"],
                            convert_price(tempo_config["blue_hp"]),
                        )
                        + convert_kw_to_euro(
                            tempo_data["white_hp"],
                            convert_price(tempo_config["white_hp"]),
                        )
                        + convert_kw_to_euro(tempo_data["red_hp"], convert_price(tempo_config["red_hp"]))
                    )
                    cost_hc = (
                        convert_kw_to_euro(
                            tempo_data["blue_hc"],
                            convert_price(tempo_config["blue_hc"]),
                        )
                        + convert_kw_to_euro(
                            tempo_data["white_hc"],
                            convert_price(tempo_config["white_hc"]),
                        )
                        + convert_kw_to_euro(tempo_data["red_hc"], convert_price(tempo_config["red_hc"]))
                    )
                    dailyweek_cost_hp.append(cost_hp)
                    dailyweek_cost_hc.append(cost_hc)
                    value = cost_hp + cost_hc
                    if i == 0:
                        daily_cost = value
                    elif i == 1:
                        yesterday_hp_value_cost = cost_hp
                    dailyweek_cost.append(round(value, 1))
            else:
                for i in range(7):
                    hour_hp = stats.detail(i, "HP")["value"]
                    hour_hc = stats.detail(i, "HC")["value"]
                    dailyweek_hp.append(convert_kw(hour_hp))
                    dailyweek_hc.append(convert_kw(hour_hc))
                    dailyweek_cost_hp.append(convert_kw_to_euro(hour_hp, self.config.consumption_price_base))
                    dailyweek_cost_hc.append(convert_kw_to_euro(hour_hc, self.config.consumption_price_base))
                    dailyweek_cost.append(
                        convert_kw_to_euro(stats.daily(i)["value"], self.config.consumption_price_base)
                    )
                    if i == 0:
                        daily_cost = convert_kw_to_euro(stats.daily(0)["value"], self.config.consumption_price_base)
                    elif i == 1:
                        yesterday_hp_value_cost = convert_kw_to_euro(hour_hp, self.config.consumption_price_base)
        else:
            daily_cost = convert_kw_to_euro(stats.daily(0)["value"], self.config.production_price)
            for i in range(7):
                dailyweek_cost.append(convert_kw_to_euro(stats.daily(i)["value"], self.config.production_price))

        if not dailyweek_hp:
            dailyweek_hp = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_cost_hp:
            dailyweek_cost_hp = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_hc:
            dailyweek_hc = [0, 0, 0, 0, 0, 0, 0, 0]
        if not dailyweek_cost_hc:
            dailyweek_cost_hc = [0, 0, 0, 0, 0, 0, 0, 0]

        yesterday_consumption_max_power = 0
        if self.config.consumption_max_power:
            yesterday_consumption_max_power = stats.max_power(0)["value"]

        error_last_call = DB.get_error_log(self.usage_point_id)
        if error_last_call is None:
            error_last_call = ""

        attributes = {
            "yesterdayDate": stats.daily(0)["begin"],
            "yesterday": convert_kw(stats.daily(0)["value"]),
            "serviceEnedis": "myElectricalData",
            "yesterdayLastYearDate": (datetime.now(tz=UTC) - relativedelta(years=1)).strftime(self.date_format),
            "yesterdayLastYear": convert_kw(yesterday_last_year.value) if hasattr(yesterday_last_year, "value") else 0,
            "daily": [
                convert_kw(stats.daily(0)["value"]),
                convert_kw(stats.daily(1)["value"]),
                convert_kw(stats.daily(2)["value"]),
                convert_kw(stats.daily(3)["value"]),
                convert_kw(stats.daily(4)["value"]),
                convert_kw(stats.daily(5)["value"]),
                convert_kw(stats.daily(6)["value"]),
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
            "dailyweek_costHP": dailyweek_cost_hp,
            "dailyweek_HP": dailyweek_hp,
            "dailyweek_costHC": dailyweek_cost_hc,
            "dailyweek_HC": dailyweek_hc,
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
            "yesterday_HC_cost": convert_kw_to_euro(yesterday_hc_value, self.config.consumption_price_hc),
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
            "dailyweek_Tempo": [
                stats.tempo_color(0)["value"],
                stats.tempo_color(1)["value"],
                stats.tempo_color(2)["value"],
                stats.tempo_color(3)["value"],
                stats.tempo_color(4)["value"],
                stats.tempo_color(5)["value"],
                stats.tempo_color(6)["value"],
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
            "subscribed_power": self.config.subscribed_power,
            # "info": info
        }

        uniq_id = f"myelectricaldata_linky_{self.usage_point_id}_{measurement_direction}"
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
            numPDL=self.usage_point_id,
        )

    def tempo(self):
        """Add a sensor to Home Assistant with the tempo data for today and tomorrow.

        Returns:
            None

        """
        uniq_id = "myelectricaldata_tempo_today"
        begin = datetime.combine(datetime.now(tz=UTC), datetime.min.time())
        end = datetime.combine(datetime.now(tz=UTC), datetime.max.time())
        tempo_data = DB.get_tempo_range(begin, end, "asc")
        if tempo_data:
            date = tempo_data[0].date.strftime(self.date_format_detail)
            state = tempo_data[0].color
        else:
            date = begin.strftime(self.date_format_detail)
            state = "Inconnu"
        attributes = {"date": date}
        self.tempo_color = state
        self.sensor(
            topic="myelectricaldata_rte/tempo_today",
            name="Today",
            device_name="RTE Tempo",
            device_model="RTE",
            device_identifiers="rte_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=state,
        )

        uniq_id = "myelectricaldata_tempo_tomorrow"
        begin = begin + timedelta(days=1)
        end = end + timedelta(days=1)
        tempo_data = DB.get_tempo_range(begin, end, "asc")
        if tempo_data:
            date = tempo_data[0].date.strftime(self.date_format_detail)
            state = tempo_data[0].color
        else:
            date = begin.strftime(self.date_format_detail)
            state = "Inconnu"
        attributes = {"date": date}
        self.sensor(
            topic="myelectricaldata_rte/tempo_tomorrow",
            name="Tomorrow",
            device_name="RTE Tempo",
            device_model="RTE",
            device_identifiers="rte_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=state,
        )

    def tempo_days(self):
        """Add tempo days sensors to Home Assistant.

        This method retrieves tempo days configuration from the database
        and creates sensors for each color and corresponding number of days.

        Returns:
            None
        """
        tempo_days = DB.get_tempo_config("days")
        for color, days in tempo_days.items():
            self.tempo_days_sensor(f"{color}", days)

    def tempo_days_sensor(self, color, days):
        """Add a sensor to Home Assistant with the given name and state.

        Args:
            color (str): The color of the tempo (e.g. blue, white, red).
            days (int): The number of days in the tempo.

        Returns:
            None

        """
        uniq_id = f"myelectricaldata_tempo_days_{color}"
        self.sensor(
            topic=f"myelectricaldata_edf/tempo_days_{color}",
            name=f"Days {color.capitalize()}",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers="edf_tempo",
            uniq_id=uniq_id,
            state=days,
        )

    def tempo_info(self):
        """Add tempo information sensor to Home Assistant.

        This method retrieves tempo configuration from the database
        and creates a sensor with information about tempo days and prices.

        Returns:
            None
        """
        uniq_id = "myelectricaldata_tempo_info"
        tempo_days = DB.get_tempo_config("days")
        tempo_price = DB.get_tempo_config("price")
        if 22 > int(datetime.now(tz=UTC).strftime("%H")) < 6:
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
            "price_red_hc": convert_price(tempo_price["red_hc"]),
        }
        self.sensor(
            topic="myelectricaldata_edf/tempo_info",
            name="Info",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers="edf_tempo",
            uniq_id=uniq_id,
            attributes=attributes,
            state=current_price,
            unit_of_measurement="EUR/kWh",
        )

    def tempo_price(self):
        """Add tempo price sensors to Home Assistant.

        This method retrieves tempo price configuration from the database
        and creates sensors for each color with corresponding price.

        Returns:
            None
        """
        tempo_price = DB.get_tempo_config("price")
        for color, price in tempo_price.items():
            self.tempo_price_sensor(
                f"{color}",
                float(price.replace(",", ".")),
                f"{color.split('_')[0].capitalize()}{color.split('_')[1].capitalize()}",
            )

    def tempo_price_sensor(self, color, price, name):
        """Add tempo price sensor to Home Assistant.

        This method creates a sensor for a specific tempo color with the corresponding price.

        Args:
            color (str): The color of the tempo.
            price (float): The price of the tempo.
            name (str): The name of the tempo.

        Returns:
            None
        """
        uniq_id = f"myelectricaldata_tempo_price_{color}"
        name = f"{name[0:-2]} {name[-2:]}"
        self.sensor(
            topic=f"myelectricaldata_edf/tempo_price_{color}",
            name=f"Price {name}",
            device_name="EDF Tempo",
            device_model="EDF",
            device_identifiers="edf_tempo",
            uniq_id=uniq_id,
            state=convert_price(price),
            unit_of_measurement="EUR/kWh",
        )

    def ecowatt(self):
        """Calculate the ecowatt sensor values for different delta values.

        This method calculates the ecowatt sensor values for different delta values (0, 1, and 2).
        It calls the `ecowatt_delta` method with the corresponding delta values.

        Returns:
            None
        """
        self.ecowatt_delta("J0", 0)
        self.ecowatt_delta("J1", 1)
        self.ecowatt_delta("J2", 2)

    def ecowatt_delta(self, name, delta):
        """Calculate the delta value for the ecowatt sensor.

        Args:
            name (str): The name of the ecowatt sensor.
            delta (int): The number of days to calculate the delta.

        Returns:
            None
        """
        uniq_id = f"myelectricaldata_ecowatt_{name}"
        current_date = datetime.combine(datetime.now(tz=UTC), datetime.min.time()) + timedelta(days=delta)
        fetch_date = current_date - timedelta(days=1)
        ecowatt_data = DB.get_ecowatt_range(fetch_date, fetch_date, "asc")
        day_value = 0
        if ecowatt_data:
            forecast = {}
            for data in ecowatt_data:
                day_value = data.value
                for date, value in json.loads(data.detail.replace("'", '"')).items():
                    date = datetime.strptime(date, self.date_format_detail)
                    forecast[f'{date.strftime("%H")} h'] = value
            attributes = {
                "date": current_date.strftime(self.date_format),
                "forecast": forecast,
            }
            self.sensor(
                topic=f"myelectricaldata_rte/ecowatt_{name}",
                name=f"{name}",
                device_name="RTE EcoWatt",
                device_model="RTE",
                device_identifiers="rte_ecowatt",
                uniq_id=uniq_id,
                attributes=attributes,
                state=day_value,
            )
