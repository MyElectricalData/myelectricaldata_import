import json
import logging
import re
from datetime import datetime, timedelta

from config import DETAIL_MAX_DAYS, URL
from init import CONFIG, DB
from models.database import ConsumptionDetail, ProductionDetail
from models.query import Query


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


class Detail:
    def __init__(self, headers, usage_point_id, measure_type="consumption"):
        self.config = CONFIG
        self.db = DB
        self.url = URL
        self.max_detail = 7
        self.date_format = "%Y-%m-%d"
        self.date_detail_format = "%Y-%m-%d %H:%M:%S"
        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = self.db.get_usage_point(self.usage_point_id)
        self.contract = self.db.get_contract(self.usage_point_id)
        self.daily_max_days = int(DETAIL_MAX_DAYS)
        self.max_days_date = datetime.utcnow() - timedelta(days=self.daily_max_days)
        if (
            measure_type == "consumption"
            and hasattr(self.usage_point_config, "consumption_detail_max_date")
            and self.usage_point_config.consumption_detail_max_date != ""
            and self.usage_point_config.consumption_detail_max_date is not None
        ):
            self.activation_date = self.usage_point_config.consumption_detail_max_date
        elif (
            measure_type == "production"
            and hasattr(self.usage_point_config, "production_detail_max_date")
            and self.usage_point_config.production_detail_max_date != ""
            and self.usage_point_config.production_detail_max_date is not None
        ):
            self.activation_date = self.usage_point_config.production_detail_max_date
        elif (
            hasattr(self.contract, "last_activation_date")
            and self.contract.last_activation_date != ""
            and self.contract.last_activation_date is not None
        ):
            self.activation_date = self.contract.last_activation_date
        else:
            self.activation_date = self.max_days_date
        self.offpeak_hours = {
            0: self.usage_point_config.offpeak_hours_0,
            1: self.usage_point_config.offpeak_hours_1,
            2: self.usage_point_config.offpeak_hours_2,
            3: self.usage_point_config.offpeak_hours_3,
            4: self.usage_point_config.offpeak_hours_4,
            5: self.usage_point_config.offpeak_hours_5,
            6: self.usage_point_config.offpeak_hours_6,
        }
        self.measure_type = measure_type
        self.base_price = 0
        if measure_type == "consumption":
            self.detail_table = ConsumptionDetail
            if hasattr(self.usage_point_config, "consumption_price_base"):
                self.base_price = self.usage_point_config.consumption_price_base
        else:
            self.detail_table = ProductionDetail
            if hasattr(self.usage_point_config, "production_price"):
                self.base_price = self.usage_point_config.production_price

    def run(self, begin, end):
        if begin.strftime(self.date_format) == end.strftime(self.date_format):
            end = end + timedelta(days=1)
        begin_str = begin.strftime(self.date_format)
        end_str = end.strftime(self.date_format)
        logging.info(f"Récupération des données : {begin_str} => {end_str}")
        endpoint = f"{self.measure_type}_load_curve/{self.usage_point_id}/start/{begin_str}/end/{end_str}"
        # if begin <= (datetime.now() - timedelta(days=8)):
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        try:
            current_data = self.db.get_detail(self.usage_point_id, begin, end, self.measure_type)
            # current_week = datetime.now() - timedelta(days=self.max_detail + 1)
            # last_week = False
            # if current_week <= begin:
            #     last_week = True
            # if not current_data["missing_data"] and not last_week:
            if not current_data["missing_data"]:
                logging.info(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({"date": date, "value": data["value"]})
                return output
            else:
                logging.info(f" Chargement des données depuis MyElectricalData {begin_str} => {end_str}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                if hasattr(data, "status_code"):
                    if data.status_code == 403:
                        if hasattr(data, "text"):
                            description = json.loads(data.text)["detail"]
                        else:
                            description = data
                        if hasattr(data, "status_code"):
                            status_code = data.status_code
                        else:
                            status_code = 500
                        return {
                            "error": True,
                            "description": description,
                            "status_code": status_code,
                            "exit": True,
                        }
                    if data.status_code == 200:
                        meter_reading = json.loads(data.text)["meter_reading"]
                        for interval_reading in meter_reading["interval_reading"]:
                            value = interval_reading["value"]
                            interval = re.findall(r"\d+", interval_reading["interval_length"])[0]
                            date = interval_reading["date"]
                            date_object = datetime.strptime(date, self.date_detail_format)
                            # CHANGE DATE TO BEGIN RANGE
                            date = date_object - timedelta(minutes=int(interval))
                            # date = date.strftime(self.date_detail_format)
                            # print(date)
                            # GET WEEKDAY
                            # date_days = date_object.weekday()
                            # date_hour_minute = date_object.strftime('%H:%M')
                            # measure_type = "HP"
                            # day_offpeak_hours = self.offpeak_hours[date_days]
                            # if day_offpeak_hours is not None:
                            #     for offpeak_hour in day_offpeak_hours.split(";"):
                            #         if offpeak_hour != "None" and offpeak_hour != "" and offpeak_hour is not None:
                            #             offpeak_begin = offpeak_hour.split("-")[0].replace('h', ':').replace('H', ':')
                            #             # FORMAT HOUR WITH 2 DIGIT
                            #             offpeak_begin = datetime.strptime(offpeak_begin, '%H:%M')
                            #             offpeak_begin = datetime.strftime(offpeak_begin, '%H:%M')
                            #             offpeak_stop = offpeak_hour.split("-")[1].replace('h', ':').replace('H', ':')
                            #             # FORMAT HOUR WITH 2 DIGIT
                            #             offpeak_stop = datetime.strptime(offpeak_stop, '%H:%M')
                            #             offpeak_stop = datetime.strftime(offpeak_stop, '%H:%M')
                            #             result = is_between(date_hour_minute, (offpeak_begin, offpeak_stop))
                            #             if result:
                            #                 measure_type = "HC"
                            self.db.insert_detail(
                                usage_point_id=self.usage_point_id,
                                date=date,
                                value=value,
                                interval=interval,
                                measure_type="",
                                blacklist=0,
                                mesure_type=self.measure_type,
                            )
                        return meter_reading["interval_reading"]
                    else:
                        return {
                            "error": True,
                            "description": json.loads(data.text)["detail"],
                            "status_code": data.status_code,
                        }
                else:
                    if hasattr(data, "text"):
                        description = json.loads(data.text)["detail"]
                    else:
                        description = data
                    if hasattr(data, "status_code"):
                        status_code = data.status_code
                    else:
                        status_code = 500
                    return {
                        "error": True,
                        "description": description,
                        "status_code": status_code,
                    }
        except Exception as e:
            logging.exception(e)
            logging.error(e)

    def get(self):
        end = datetime.combine((datetime.now() + timedelta(days=2)), datetime.max.time())
        begin = datetime.combine(end - timedelta(days=self.max_detail), datetime.min.time())
        finish = True
        result = []
        while finish:
            if self.max_days_date > begin:
                # Max day reached
                begin = self.max_days_date
                finish = False
                response = self.run(begin, end)
            elif self.activation_date and self.activation_date > begin:
                # Activation date reached
                begin = self.activation_date
                finish = False
                response = self.run(begin, end)
            else:
                response = self.run(begin, end)
                begin = begin - timedelta(days=self.max_detail)
                end = end - timedelta(days=self.max_detail)
            if "exit" in response:
                finish = False
                response = {
                    "error": True,
                    "description": response["description"],
                    "status_code": response["status_code"],
                }
            if response is not None:
                result = [*result, *response]
            else:
                response = {
                    "error": True,
                    "description": "MyElectricalData est indisponible.",
                }
            if "error" in response and response["error"]:
                logging.error("Echec de la récupération des données.")
                logging.error(f' => {response["description"]}')
                logging.error(f" => {begin.strftime(self.date_format)} -> {end.strftime(self.date_format)}")
            if "status_code" in response and (response["status_code"] == 409 or response["status_code"] == 400):
                finish = False
                logging.error("Arrêt de la récupération des données suite à une erreur.")
                logging.error(f"Prochain lancement à {datetime.now() + timedelta(seconds=self.config.get('cycle'))}")
        return result

    def reset_daily(self, date):
        begin = datetime.combine(datetime.strptime(date, self.date_format), datetime.min.time())
        end = datetime.combine(datetime.strptime(date, self.date_format), datetime.max.time())
        self.db.reset_detail_range(self.usage_point_id, begin, end, self.measure_type)
        return True

    def delete_daily(self, date):
        begin = datetime.combine(datetime.strptime(date, self.date_format), datetime.min.time())
        end = datetime.combine(datetime.strptime(date, self.date_format), datetime.max.time())
        self.db.delete_detail_range(self.usage_point_id, begin, end, self.measure_type)
        return True

    def reset(self, date=None):
        if date is not None:
            date = datetime.strptime(date, self.date_detail_format)
        self.db.reset_detail(self.usage_point_id, date, self.measure_type)
        return True

    def delete(self, date=None):
        if date is not None:
            date = datetime.strptime(date, self.date_detail_format)
        self.db.delete_detail(self.usage_point_id, date, self.measure_type)
        return True

    def fetch(self, date):
        if date is not None:
            date = datetime.strptime(date, self.date_format)
        result = self.run(
            datetime.combine(date - timedelta(days=2), datetime.min.time()),
            datetime.combine(date + timedelta(days=2), datetime.min.time()),
        )
        if "error" in result and result["error"]:
            return {
                "error": True,
                "notif": result["description"],
                "fail_count": self.db.get_detail_fail_count(self.usage_point_id, date, self.measure_type),
            }

        for item in result:
            if type(item["date"]) == str:
                item["date"] = datetime.strptime(item["date"], self.date_detail_format)
            result_date = item["date"].strftime(self.date_format)
            if date.strftime(self.date_format) in result_date:
                item["date"] = result_date
                return item

        return {
            "error": True,
            "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})",
            "fail_count": self.db.get_detail_fail_count(self.usage_point_id, date, self.measure_type),
        }


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time > time_range[0] or time <= time_range[1]
    return time_range[0] < time <= time_range[1]
