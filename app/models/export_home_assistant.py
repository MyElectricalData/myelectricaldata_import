import __main__ as app
import calendar
import json
import sys
from datetime import datetime, timezone, timedelta

from pprint import pprint
from statistics import median

import pytz
from dateutil.relativedelta import relativedelta

utc = pytz.UTC


class HomeAssistant:

    def __init__(self, usage_point_id, mesure_type="consumption"):
        self.usage_point_id = usage_point_id
        self.mesure_type = mesure_type
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
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

        self.topic = f"{self.discovery_prefix}/sensor/myelectricaldata/{self.usage_point_id}"

    def export(self, price_base, price_hp, price_hc):

        app.LOG.title(f"[{self.usage_point_id}] Exportation des données dans Home Assistant (via MQTT)")

        def convert_kw(value):
            return round(value / 1000, 1)

        def convert_kw_to_euro(value, price):
            return round(value / 1000 * price, 1)

        config = {
            f"config": json.dumps(
                {
                    "name": f"myelectricaldata_{self.usage_point_id}",
                    "uniq_id": f"myelectricaldata.{self.usage_point_id}",
                    "stat_t": f"{self.topic}/state",
                    "json_attr_t": f"{self.topic}/attributes",
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
        app.MQTT.publish_multiple(config, self.topic)
        state = app.DB.get_daily_last(self.usage_point_id, self.mesure_type)
        if state:
            state = state.value
        else:
            state = 0

        app.MQTT.publish_multiple({
            f"state": convert_kw(state)
        }, self.topic)

        now = datetime.now(timezone.utc)
        contract = app.DB.get_contract(self.usage_point_id)
        usage_point = app.DB.get_usage_point(self.usage_point_id)

        offpeak_hours_enedis = ""
        offpeak_hours = []
        if (
                hasattr(usage_point, "offpeak_hours_0") and usage_point.offpeak_hours_0 is not None or
                hasattr(usage_point, "offpeak_hours_1") and usage_point.offpeak_hours_1 is not None or
                hasattr(usage_point, "offpeak_hours_2") and usage_point.offpeak_hours_2 is not None or
                hasattr(usage_point, "offpeak_hours_3") and usage_point.offpeak_hours_3 is not None or
                hasattr(usage_point, "offpeak_hours_4") and usage_point.offpeak_hours_4 is not None or
                hasattr(usage_point, "offpeak_hours_5") and usage_point.offpeak_hours_5 is not None or
                hasattr(usage_point, "offpeak_hours_6") and usage_point.offpeak_hours_6 is not None
        ):
            offpeak_hours_enedis = (
                f"Lundi ({usage_point.offpeak_hours_0});" 
                f"Mardi ({usage_point.offpeak_hours_1});"  
                f"Mercredi ({usage_point.offpeak_hours_2});"  
                f"Jeudi ({usage_point.offpeak_hours_3});" 
                f"Vendredi ({usage_point.offpeak_hours_4});"  
                f"Samedi ({usage_point.offpeak_hours_5});" 
                f"Dimanche ({usage_point.offpeak_hours_6});"
            )

            usage_point = app.DB.get_usage_point(self.usage_point_id)
            idx = 0
            while idx <= 6:
                _offpeak_hours = []
                for offpeak_hours_data in getattr(usage_point, f"offpeak_hours_{idx}").split(";"):
                    _offpeak_hours.append(offpeak_hours_data.split("-"))
                offpeak_hours.append(_offpeak_hours)
                idx = idx + 1

        yesterday = datetime.combine(now - relativedelta(days=1), datetime.max.time())
        previous_week = datetime.combine(yesterday - relativedelta(days=7), datetime.min.time())
        yesterday_last_year = yesterday - relativedelta(years=1)

        info = {
            "yesterday": yesterday.strftime(self.date_format),
            "previous_week": previous_week.strftime(self.date_format),
            "yesterday_last_year": yesterday_last_year.strftime(self.date_format)
        }

        # DAILY DATA
        begin = datetime.combine(yesterday, datetime.min.time())
        end = datetime.combine(yesterday, datetime.max.time())
        day_idx = 0
        daily_obj = []
        while day_idx < 7:
            day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
            if day:
                daily_obj.append({
                    "date": day[0].date,
                    "value": day[0].value
                })
            else:
                daily_obj.append({
                    "date": begin,
                    "value": 0
                })
            begin = begin - timedelta(days=1)
            end = end - timedelta(days=1)
            day_idx = day_idx + 1

        # current_week
        app.LOG.log(" - current_week")
        current_week = 0
        begin = datetime.combine(now - relativedelta(weeks=1), datetime.min.time())
        end = datetime.combine(yesterday, datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_week = current_week + data.value
        info["current_week"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # last_week
        app.LOG.log(" - last_week")
        last_week = 0
        # begin = datetime.combine(yesterday - relativedelta(weeks=1), datetime.min.time())
        # end = datetime.combine(yesterday - relativedelta(weeks=1), datetime.max.time())
        # day_idx = 0
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        #     if day:
        #         for data in day:
        #             last_week = last_week + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        begin = datetime.combine(now - relativedelta(weeks=2), datetime.min.time())
        end = datetime.combine(yesterday - relativedelta(weeks=1), datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            last_week = last_week + data.value
        info["last_week"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # current_week_evolution
        app.LOG.log(" - current_week_evolution")
        if current_week != 0:
            current_week_evolution = (current_week - last_week) * 100 / current_week
        else:
            current_week_evolution = 0

        # yesterday_evolution
        app.LOG.log(" - yesterday_evolution")
        begin = datetime.combine(yesterday, datetime.min.time())
        end = datetime.combine(now, datetime.max.time())
        yesterday_data = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        info["yesterday_data"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }
        begin = datetime.combine(yesterday - timedelta(days=1), datetime.min.time())
        end = datetime.combine(now - timedelta(days=1), datetime.max.time())
        yesterday_1_data = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        info["yesterday_1_data"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }
        if yesterday_data and yesterday_1_data and yesterday_data[0].value != 0 and yesterday_1_data[0].value != 0:
            yesterday_evolution = (yesterday_data[0].value - yesterday_1_data[0].value) * 100 / yesterday_data[0].value
        else:
            yesterday_evolution = 0

        # current_week_last_year
        app.LOG.log(" - current_week_last_year")
        current_week_last_year = 0
        # begin = datetime.combine(yesterday - relativedelta(years=1), datetime.min.time())
        # end = datetime.combine(yesterday - relativedelta(years=1), datetime.max.time())
        # day_idx = 0
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        #     if day:
        #         for data in day:
        #             current_week_last_year = current_week_last_year + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        begin = datetime.combine((now - timedelta(weeks=1)) - relativedelta(years=1), datetime.min.time())
        end = datetime.combine(yesterday - relativedelta(years=1), datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_week_last_year = current_week_last_year + data.value
        info["current_week_last_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # last_month
        app.LOG.log(" - last_month")
        last_month = 0
        begin = datetime.combine((now.replace(day=1) - timedelta(days=1)).replace(day=1), datetime.min.time())
        end = datetime.combine(yesterday.replace(day=1) - timedelta(days=1), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            last_month = last_month + day.value
        info["last_month"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # current_month
        app.LOG.log(" - current_month")
        current_month = 0
        begin = datetime.combine(now.replace(day=1), datetime.min.time())
        end = yesterday
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_month = current_month + day.value
        info["current_month"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # current_month_last_year
        app.LOG.log(" - current_month_last_year")
        current_month_last_year = 0
        begin = begin - relativedelta(years=1)
        end = end - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_month_last_year = current_month_last_year + day.value
        info["current_month_last_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # current_month_evolution
        app.LOG.log(" - current_month_evolution")
        if last_month != 0:
            current_month_evolution = (current_month - current_month_last_year) * 100 / last_month
        else:
            current_month_evolution = 0

        # last_month_last_year
        app.LOG.log(" - last_month_last_year")
        last_month_last_year = 0
        begin = datetime.combine(
            (now.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time()) - relativedelta(years=1)
        end = datetime.combine(
            yesterday.replace(day=1) - timedelta(days=1),
            datetime.max.time()) - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            last_month_last_year = last_month_last_year + day.value
        info["last_month_last_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # monthly_evolution
        app.LOG.log(" - monthly_evolution")
        if last_month != 0:
            monthly_evolution = (last_month - last_month_last_year) * 100 / last_month
        else:
            monthly_evolution = 0

        # current_year
        app.LOG.log(" - current_year")
        current_year = 0
        begin = datetime.combine(now.replace(month=1).replace(day=1), datetime.min.time())
        end = yesterday
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_year = current_year + day.value
        info["current_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # current_year_last_year
        app.LOG.log(" - current_year_last_year")
        current_year_last_year = 0
        begin = datetime.combine(begin - relativedelta(years=1), datetime.min.time())
        end = end - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            current_year_last_year = current_year_last_year + day.value
        info["current_year_last_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # last_year
        app.LOG.log(" - last_year")
        last_year = 0
        begin = datetime.combine(now.replace(month=1).replace(day=1) - relativedelta(years=1),
                                 datetime.min.time())
        last_day_of_month = calendar.monthrange(int(begin.strftime("%Y")), 12)[1]
        end = datetime.combine(begin.replace(day=last_day_of_month).replace(month=12), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type):
            last_year = last_year + day.value
        info["last_year"] = {
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

        # DETAIL DATA
        app.LOG.log(" - yesterday_hp / yesterday_hc")
        yesterday_hp = 0
        yesterday_hc = 0
        begin = datetime.combine(yesterday, datetime.min.time())
        end = datetime.combine(now, datetime.max.time())
        for day in app.DB.get_detail_range(self.usage_point_id, begin, end, self.mesure_type):
            if day.measure_type == "HP":
                yesterday_hp = yesterday_hp + (day.value / (60 / day.interval))
            if day.measure_type == "HC":
                yesterday_hc = yesterday_hc + (day.value / (60 / day.interval))
        info["yesterday_hp_hc"] = {
            "begin": begin.strftime(self.date_format_detail),
            "end": end.strftime(self.date_format_detail)
        }


        app.LOG.log(" - dailyweek_hp / dailyweek_hc")
        dailyweek_hp = {}
        dailyweek_hc = {}
        # begin = datetime.combine(now - timedelta(weeks=1), datetime.min.time())
        # end = datetime.combine(yesterday, datetime.max.time())
        # day_idx = 0
        # last_date = 0
        # for data in app.DB.get_detail_range(self.usage_point_id, begin, end, self.mesure_type):
        #     if last_date != data.date.strftime("%d"):
        #         day_idx = day_idx + 1
        #     date = data.date
        #     value = data.value
        #     if data.measure_type == "HP":
        #         if day_idx not in dailyweek_hp:
        #             dailyweek_hp[day_idx] = {
        #                 "date": date,
        #                 "value": value / (60 / data.interval),
        #             }
        #         else:
        #             dailyweek_hp[day_idx]["value"] = dailyweek_hp[day_idx]["value"] + data.value
        #     if data.measure_type == "HC":
        #         if day_idx not in dailyweek_hc:
        #             dailyweek_hc[day_idx] = {
        #                 "date": date,
        #                 "value": value / (60 / data.interval),
        #             }
        #         else:
        #             dailyweek_hc[day_idx]["value"] = dailyweek_hc[day_idx]["value"] + data.value
        #     last_date = data.date.strftime("%d")
        # info["dailyweek_hp_hc"] = {
        #     "begin": begin.strftime(self.date_format_detail),
        #     "end": end.strftime(self.date_format_detail)
        # }

        begin = datetime.combine(yesterday - timedelta(days=1), datetime.min.time())
        end = datetime.combine(yesterday, datetime.max.time())
        day_idx = 0
        while day_idx < 7:
            detail_range = app.DB.get_detail_range(self.usage_point_id, begin, end, self.mesure_type)
            if not detail_range:
                dailyweek_hp[day_idx] = {
                    "date": begin,
                    "value": 0,
                }
                dailyweek_hc[day_idx] = {
                    "date": begin,
                    "value": 0,
                }
            else:
                for day in detail_range:
                    date = day.date
                    value = day.value
                    if day.measure_type == "HP":
                        if day_idx not in dailyweek_hp:
                            dailyweek_hp[day_idx] = {
                                "date": date,
                                "value": value / (60 / day.interval),
                            }
                        else:
                            dailyweek_hp[day_idx]["value"] = dailyweek_hp[day_idx]["value"] + day.value
                    if day.measure_type == "HC":
                        if day_idx not in dailyweek_hc:
                            dailyweek_hc[day_idx] = {
                                "date": date,
                                "value": value / (60 / day.interval),
                            }
                        else:
                            dailyweek_hc[day_idx]["value"] = dailyweek_hc[day_idx]["value"] + day.value
            day_idx = day_idx + 1
            begin = begin - timedelta(days=1)
            end = end - timedelta(days=1)

        # detail_range = app.DB.get_detail_range(self.usage_point_id, begin, end, self.mesure_type)
        # for day in detail_range:
        #     if last_date != day.date.strftime("%d"):
        #         day_idx = day_idx + 1
        #     date = day.date
        #     value = day.value
        #     if day.measure_type == "HP":
        #         if day_idx not in dailyweek_hp:
        #             dailyweek_hp[day_idx] = {
        #                 "date": date,
        #                 "value": value / (60 / day.interval),
        #             }
        #         else:
        #             dailyweek_hp[day_idx]["value"] = dailyweek_hp[day_idx]["value"] + day.value
        #     if day.measure_type == "HC":
        #         if day_idx not in dailyweek_hc:
        #             dailyweek_hc[day_idx] = {
        #                 "date": date,
        #                 "value": value / (60 / day.interval),
        #             }
        #         else:
        #             dailyweek_hc[day_idx]["value"] = dailyweek_hc[day_idx]["value"] + day.value
        #     last_date = day.date.strftime("%d")

        app.LOG.log(" - peak_offpeak_percent_hp / peak_offpeak_percent_hc")
        peak_offpeak_percent_hp = 0
        peak_offpeak_percent_hc = 0
        begin = yesterday - relativedelta(years=1)
        end = yesterday
        for day in app.DB.get_detail_range(self.usage_point_id, begin, end, self.mesure_type):
            if day.measure_type == "HP":
                peak_offpeak_percent_hp = peak_offpeak_percent_hp + (day.value / (60 / day.interval))
            if day.measure_type == "HC":
                peak_offpeak_percent_hc = peak_offpeak_percent_hc + (day.value / (60 / day.interval))
        if peak_offpeak_percent_hp != 0:
            peak_offpeak_percent = (peak_offpeak_percent_hp - peak_offpeak_percent_hc) * 100 / peak_offpeak_percent_hp
        else:
            peak_offpeak_percent = 0
        info["peak_offpeak_percent_hp_hc"] = {
            "begin": begin.strftime(self.date_format_detail),
            "end": end.strftime(self.date_format_detail)
        }

        yesterdayLastYear = app.DB.get_daily_date(self.usage_point_id, yesterday_last_year)
        print(daily_obj)
        config = {
            f"attributes": json.dumps(
                {
                    "numPDL": self.usage_point_id,
                    "activationDate": contract.last_activation_date.strftime(self.date_format_detail),
                    "lastUpdate": now.strftime(self.date_format_detail),
                    "timeLastCall": now.strftime(self.date_format_detail),
                    "yesterdayDate": daily_obj[0]["date"].strftime(self.date_format),
                    "yesterday": convert_kw(daily_obj[0]["value"]),
                    "yesterdayLastYearDate": (now - relativedelta(years=1)).strftime(self.date_format),
                    "yesterdayLastYear": convert_kw(yesterdayLastYear.value) if hasattr(yesterdayLastYear, "value") else 0,
                    "daily": [
                        convert_kw(daily_obj[0]["value"]),
                        convert_kw(daily_obj[1]["value"]),
                        convert_kw(daily_obj[2]["value"]),
                        convert_kw(daily_obj[3]["value"]),
                        convert_kw(daily_obj[4]["value"]),
                        convert_kw(daily_obj[5]["value"]),
                        convert_kw(daily_obj[6]["value"])
                    ],
                    "current_week": convert_kw(current_week),
                    "last_week": convert_kw(last_week),
                    "day_1": convert_kw(daily_obj[0]["value"]),
                    "day_2": convert_kw(daily_obj[1]["value"]),
                    "day_3": convert_kw(daily_obj[2]["value"]),
                    "day_4": convert_kw(daily_obj[3]["value"]),
                    "day_5": convert_kw(daily_obj[4]["value"]),
                    "day_6": convert_kw(daily_obj[5]["value"]),
                    "day_7": convert_kw(daily_obj[6]["value"]),
                    "current_week_last_year": convert_kw(current_week_last_year),
                    "last_month": convert_kw(last_month),
                    "current_month": convert_kw(current_month),
                    "current_month_last_year": convert_kw(current_month_last_year),
                    "last_month_last_year": convert_kw(last_month_last_year),
                    "last_year": convert_kw(last_year),
                    "current_year": convert_kw(current_year),
                    "current_year_last_year": convert_kw(current_year_last_year),
                    "dailyweek": [
                        daily_obj[0]["date"].strftime(self.date_format),
                        daily_obj[1]["date"].strftime(self.date_format),
                        daily_obj[2]["date"].strftime(self.date_format),
                        daily_obj[3]["date"].strftime(self.date_format),
                        daily_obj[4]["date"].strftime(self.date_format),
                        daily_obj[5]["date"].strftime(self.date_format),
                        daily_obj[6]["date"].strftime(self.date_format),
                    ],
                    "dailyweek_cost": [
                        convert_kw_to_euro(daily_obj[0]["value"], price_base),
                        convert_kw_to_euro(daily_obj[1]["value"], price_base),
                        convert_kw_to_euro(daily_obj[2]["value"], price_base),
                        convert_kw_to_euro(daily_obj[3]["value"], price_base),
                        convert_kw_to_euro(daily_obj[4]["value"], price_base),
                        convert_kw_to_euro(daily_obj[5]["value"], price_base),
                        convert_kw_to_euro(daily_obj[6]["value"], price_base),
                    ],
                    "dailyweek_costHP": [
                        convert_kw_to_euro(dailyweek_hp[0]["value"], price_hp) if 0 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[1]["value"], price_hp) if 1 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[2]["value"], price_hp) if 2 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[3]["value"], price_hp) if 3 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[4]["value"], price_hp) if 4 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[5]["value"], price_hp) if 5 in dailyweek_hp else 0,
                        convert_kw_to_euro(dailyweek_hp[6]["value"], price_hp) if 6 in dailyweek_hp else 0,
                    ],
                    "dailyweek_HP": [
                        convert_kw(dailyweek_hp[0]["value"]) if 0 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[1]["value"]) if 1 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[2]["value"]) if 2 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[3]["value"]) if 3 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[4]["value"]) if 4 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[5]["value"]) if 5 in dailyweek_hp else 0,
                        convert_kw(dailyweek_hp[6]["value"]) if 6 in dailyweek_hp else 0,
                    ],
                    "daily_cost": convert_kw_to_euro(daily_obj[0]["value"], price_base),
                    "yesterday_HP_cost": convert_kw_to_euro(yesterday_hp, price_hp),
                    "yesterday_HP": convert_kw(yesterday_hp),
                    "day_1_HP": dailyweek_hp[0]["value"] if 0 in dailyweek_hp else 0,
                    "day_2_HP": dailyweek_hp[1]["value"] if 1 in dailyweek_hp else 0,
                    "day_3_HP": dailyweek_hp[2]["value"] if 2 in dailyweek_hp else 0,
                    "day_4_HP": dailyweek_hp[3]["value"] if 3 in dailyweek_hp else 0,
                    "day_5_HP": dailyweek_hp[4]["value"] if 4 in dailyweek_hp else 0,
                    "day_6_HP": dailyweek_hp[5]["value"] if 5 in dailyweek_hp else 0,
                    "day_7_HP": dailyweek_hp[6]["value"] if 6 in dailyweek_hp else 0,
                    "dailyweek_costHC": [
                        convert_kw_to_euro(dailyweek_hc[0]["value"], price_hc) if 0 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[1]["value"], price_hc) if 1 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[2]["value"], price_hc) if 2 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[3]["value"], price_hc) if 3 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[4]["value"], price_hc) if 4 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[5]["value"], price_hc) if 5 in dailyweek_hc else 0,
                        convert_kw_to_euro(dailyweek_hc[6]["value"], price_hc) if 6 in dailyweek_hc else 0,
                    ],
                    "dailyweek_HC": [
                        convert_kw(dailyweek_hc[0]["value"] if 0 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[1]["value"] if 1 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[2]["value"] if 2 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[3]["value"] if 3 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[4]["value"] if 4 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[5]["value"] if 5 in dailyweek_hc else 0),
                        convert_kw(dailyweek_hc[6]["value"] if 6 in dailyweek_hc else 0),
                    ],
                    "yesterday_HC_cost": convert_kw_to_euro(yesterday_hc, price_hc),
                    "yesterday_HC": convert_kw(yesterday_hc),
                    "day_1_HC": dailyweek_hc[0]["value"] if 0 in dailyweek_hc else 0,
                    "day_2_HC": dailyweek_hc[1]["value"] if 1 in dailyweek_hc else 0,
                    "day_3_HC": dailyweek_hc[2]["value"] if 2 in dailyweek_hc else 0,
                    "day_4_HC": dailyweek_hc[3]["value"] if 3 in dailyweek_hc else 0,
                    "day_5_HC": dailyweek_hc[4]["value"] if 4 in dailyweek_hc else 0,
                    "day_6_HC": dailyweek_hc[5]["value"] if 5 in dailyweek_hc else 0,
                    "day_7_HC": dailyweek_hc[6]["value"] if 6 in dailyweek_hc else 0,
                    "peak_offpeak_percent": round(peak_offpeak_percent, 2),
                    "monthly_evolution":  round(monthly_evolution, 2),
                    "current_week_evolution": round(current_week_evolution, 2),
                    "current_month_evolution": round(current_month_evolution, 2),
                    "yesterday_evolution": round(yesterday_evolution, 2),
                    "friendly_name": f"myelectricaldata.{self.usage_point_id}",
                    "errorLastCall": "",
                    "errorLastCallInterne": "",
                    "current_week_number": yesterday.strftime("%V"),
                    "offpeak_hours_enedis": offpeak_hours_enedis,
                    "offpeak_hours": offpeak_hours,
                    "subscribed_power": f"{contract.subscribed_power}"
                })
        }

        for key, value in info.items():
            config[f"info/{key}"] = json.dumps(value)
        app.MQTT.publish_multiple(config, self.topic)
