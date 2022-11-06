import __main__ as app
import json
import sys
from datetime import datetime

from datetime import datetime
from dateutil.relativedelta import relativedelta

from models.mqtt import Mqtt

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

        self.topic = f"{self.discovery_prefix}/myelectricaldata/{self.usage_point_id}"

    def export(self, price_base, price_hp, price_hc):
        config = {
            f"{self.topic}/config": json.dumps(
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
        app.MQTT.publish_multiple(config)
        app.MQTT.publish_multiple({
            f"{self.topic}/state": round(app.DB.get_daily_last(self.usage_point_id, self.mesure_type).value / 1000, 1)
        })

        now = datetime.now()
        contract = app.DB.get_contract(self.usage_point_id)
        all_data = {}
        dailyObj = app.DB.get_daily_all(self.usage_point_id)
        dataObj = app.DB.get_detail_all(self.usage_point_id)
        for data in dailyObj:
            all_data[data.date] = data.value
        yesterday = now - relativedelta(days=1)
        yesterday_last_year = yesterday - relativedelta(years=1)
        config = {
            f"{self.topic}/attributes": json.dumps(
            {
             "numPDL": self.usage_point_id,
             "activationDate": contract.last_activation_date.strftime(self.date_format_detail),
             "lastUpdate": now.strftime(self.date_format_detail),
             "timeLastCall": now.strftime(self.date_format_detail),
             "yesterdayDate": yesterday.strftime(self.date_format_detail),
             "yesterday": all_data[yesterday.strftime(self.date_format)] if yesterday.strftime(self.date_format) in all_data else 0,
             "yesterdayLastYearDate": yesterday_last_year.strftime(self.date_format_detail),
             "yesterdayLastYear": all_data[yesterday_last_year.strftime(self.date_format)] if yesterday_last_year.strftime(self.date_format) in all_data else 0,
             "last_week": round(
                 (
                         dailyObj[0].value +
                         dailyObj[1].value +
                         dailyObj[2].value +
                         dailyObj[3].value +
                         dailyObj[4].value +
                         dailyObj[5].value +
                         dailyObj[6].value
                 ), 1) / 1000,
             "daily": [
                  round(dailyObj[0].value / 1000, 1),
                  round(dailyObj[1].value / 1000, 1),
                  round(dailyObj[2].value / 1000, 1),
                  round(dailyObj[3].value / 1000, 1),
                  round(dailyObj[4].value / 1000, 1),
                  round(dailyObj[5].value / 1000, 1),
                  round(dailyObj[6].value / 1000, 1)
             ],
             "current_week": 218.34300000000002,
             "day_1": round(dailyObj[0].value / 1000, 1),
             "day_2": round(dailyObj[1].value / 1000, 1),
             "day_3": round(dailyObj[2].value / 1000, 1),
             "day_4": round(dailyObj[3].value / 1000, 1),
             "day_5": round(dailyObj[4].value / 1000, 1),
             "day_6": round(dailyObj[5].value / 1000, 1),
             "day_7": round(dailyObj[6].value / 1000, 1),
             "current_week_last_year": "374.72",
             "last_month": 1040.9719999999998,
             "current_month": "184.37",
             "current_month_last_year": "326.4",
             "last_month_last_year": "1434.2",
             "last_year": 17776.88800000002,
             "current_year": "13675.53",
             "current_year_last_year": "16572.85",
             "dailyweek": [
                 dailyObj[0].date.strftime(self.date_format),
                 dailyObj[1].date.strftime(self.date_format),
                 dailyObj[2].date.strftime(self.date_format),
                 dailyObj[3].date.strftime(self.date_format),
                 dailyObj[4].date.strftime(self.date_format),
                 dailyObj[5].date.strftime(self.date_format),
                 dailyObj[6].date.strftime(self.date_format),
             ],
             "dailyweek_cost": [
              round(dailyObj[0].value / 1000 * price_base, 1),
              round(dailyObj[1].value / 1000 * price_base, 1),
              round(dailyObj[2].value / 1000 * price_base, 1),
              round(dailyObj[3].value / 1000 * price_base, 1),
              round(dailyObj[4].value / 1000 * price_base, 1),
              round(dailyObj[5].value / 1000 * price_base, 1),
              round(dailyObj[6].value / 1000 * price_base, 1),
             ],
             "dailyweek_costHP": [
              "4.8",
              "3.77",
              "4.3",
              "4.76",
              "3.94",
              "3.98",
              "3.33"
             ],
             "dailyweek_HP": [
              "32.91",
              "25.88",
              "29.52",
              "32.63",
              "27.03",
              "27.3",
              "22.85"
             ],
             "day_1_HP": 65830,
             "daily_cost": round(dailyObj[0].value / 1000 * price_base, 1),
             "yesterday_HP_cost": "4.802",
             "yesterday_HP": "32.914",
             "day_2_HP": 51768,
             "day_3_HP": 59052,
             "day_4_HP": 65262,
             "day_5_HP": 54074,
             "day_6_HP": 54604,
             "day_7_HP": 45716,
             "dailyweek_costHC": [
              "1.21",
              "1.02",
              "0.95",
              "0.9",
              "0.85",
              "0.92",
              "1.72"
             ],
             "dailyweek_HC": [
              "8.35",
              "7.0",
              "6.56",
              "6.22",
              "5.83",
              "6.35",
              "11.81"
             ],
             "day_1_HC": 16702,
             "yesterday_HC_cost": "1.218",
             "yesterday_HC": "8.35",
             "day_2_HC": 14016,
             "day_3_HC": 13136,
             "day_4_HC": 12458,
             "day_5_HC": 11668,
             "day_6_HC": 12716,
             "day_7_HC": 23638,
             "peak_offpeak_percent": 71.75,
             "monthly_evolution": -27.41,
             "current_week_evolution": -41.73,
             "current_month_evolution": -43.51,
             "yesterday_evolution": -31.87,
             "friendly_name": f"myelectricaldata.{self.usage_point_id}",
             "errorLastCall": "",
             "errorLastCallInterne": "",
             "current_week_number": now.strftime("%V"),
             "offpeak_hours_enedis": "HC (22H38-6H38)",
             "offpeak_hours": [
              [
               "22H38",
               "00H00"
              ],
              [
               "00H00",
               "6H38"
              ]
             ],
             "subscribed_power": f"{contract.subscribed_power}"
            })
        }
        app.MQTT.publish_multiple(config)

