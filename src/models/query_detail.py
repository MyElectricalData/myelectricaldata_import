import json
import logging
import re
from datetime import datetime, timedelta

from config import (
    CODE_200_SUCCESS,
    CODE_400_BAD_REQUEST,
    CODE_403_FORBIDDEN,
    CODE_409_CONFLICT,
    CODE_500_INTERNAL_SERVER_ERROR,
    DETAIL_MAX_DAYS,
    TIMEZONE_UTC,
    URL,
)
from database.contracts import DatabaseContracts
from database.detail import DatabaseDetail
from database.usage_points import DatabaseUsagePoints
from db_schema import ConsumptionDetail, ProductionDetail
from models.query import Query


class Detail:
    """Manage detail data."""

    def __init__(self, headers, usage_point_id, measure_type="consumption"):
        self.url = URL
        self.max_detail = 7
        self.date_format = "%Y-%m-%d"
        self.date_detail_format = "%Y-%m-%d %H:%M:%S"
        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = DatabaseUsagePoints(self.usage_point_id).get()
        self.contract = DatabaseContracts(self.usage_point_id).get()
        self.daily_max_days = int(DETAIL_MAX_DAYS)
        self.max_days_date = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=self.daily_max_days)
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
        self.activation_date = self.activation_date.replace(tzinfo=TIMEZONE_UTC)
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
        """Run the detail query."""
        if begin.strftime(self.date_format) == end.strftime(self.date_format):
            end = end + timedelta(days=1)
        begin_str = begin.strftime(self.date_format)
        end_str = end.strftime(self.date_format)
        logging.info(f"Récupération des données : {begin_str} => {end_str}")
        endpoint = f"{self.measure_type}_load_curve/{self.usage_point_id}/start/{begin_str}/end/{end_str}"
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        try:
            current_data = DatabaseDetail(self.usage_point_id, self.measure_type).get(begin, end)
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
                    if data.status_code == CODE_403_FORBIDDEN:
                        if hasattr(data, "text"):
                            description = json.loads(data.text)["detail"]
                        else:
                            description = data
                        if hasattr(data, "status_code"):
                            status_code = data.status_code
                        else:
                            status_code = CODE_500_INTERNAL_SERVER_ERROR
                        return {
                            "error": True,
                            "description": description,
                            "status_code": status_code,
                            "exit": True,
                        }
                    if data.status_code == CODE_200_SUCCESS:
                        meter_reading = json.loads(data.text)["meter_reading"]
                        for interval_reading in meter_reading["interval_reading"]:
                            value = interval_reading["value"]
                            interval = re.findall(r"\d+", interval_reading["interval_length"])[0]
                            date = interval_reading["date"]
                            date_object = datetime.strptime(date, self.date_detail_format).astimezone(TIMEZONE_UTC)
                            # CHANGE DATE TO BEGIN RANGE
                            date = date_object - timedelta(minutes=int(interval))
                            DatabaseDetail(self.usage_point_id, self.measure_type).insert(
                                date=date,
                                value=value,
                                interval=interval,
                                blacklist=0,
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
                        status_code = CODE_500_INTERNAL_SERVER_ERROR
                    return {
                        "error": True,
                        "description": description,
                        "status_code": status_code,
                    }
        except Exception as e:
            logging.exception(e)
            logging.error(e)

    def get(self):
        """Get the detail data."""
        end = datetime.combine((datetime.now(tz=TIMEZONE_UTC) + timedelta(days=2)), datetime.max.time()).replace(
            tzinfo=TIMEZONE_UTC
        )
        begin = datetime.combine(end - timedelta(days=self.max_detail), datetime.min.time()).replace(
            tzinfo=TIMEZONE_UTC
        )
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
            if "error" in response and response.get("error"):
                logging.error("Echec de la récupération des données.")
                logging.error(" => %s", response["description"])
                logging.error(" => %s -> %s", begin.strftime(self.date_format), end.strftime(self.date_format))
            if "status_code" in response and (
                response["status_code"] == CODE_409_CONFLICT or response["status_code"] == CODE_400_BAD_REQUEST
            ):
                finish = False
                logging.error("Arrêt de la récupération des données suite à une erreur.")
                logging.error(
                    "Prochain lancement à %s",
                    datetime.now(tz=TIMEZONE_UTC) + timedelta(seconds=self.config.get("cycle")),
                )
        return result

    def reset_daily(self, date):
        """Reset the detail for a specific date."""
        begin = datetime.combine(
            datetime.strptime(date, self.date_format).replace(tzinfo=TIMEZONE_UTC), datetime.min.time()
        ).astimezone(TIMEZONE_UTC)
        end = datetime.combine(
            datetime.strptime(date, self.date_format).replace(tzinfo=TIMEZONE_UTC), datetime.max.time()
        ).astimezone(TIMEZONE_UTC)
        DatabaseDetail(self.usage_point_id, self.measure_type).reset_range(begin, end)
        return True

    def delete_daily(self, date):
        """Delete the detail for a specific date."""
        begin = datetime.combine(
            datetime.strptime(date, self.date_format).replace(tzinfo=TIMEZONE_UTC), datetime.min.time()
        ).astimezone(TIMEZONE_UTC)
        end = datetime.combine(
            datetime.strptime(date, self.date_format).replace(tzinfo=TIMEZONE_UTC), datetime.max.time()
        ).astimezone(TIMEZONE_UTC)
        DatabaseDetail(self.usage_point_id, self.measure_type).delete_range(begin, end)
        return True

    def reset(self, date=None):
        """Reset the detail for a specific date."""
        if date is not None:
            date = datetime.strptime(date, self.date_detail_format).astimezone(TIMEZONE_UTC)
        DatabaseDetail(self.usage_point_id, self.measure_type).reset(date)
        return True

    def delete(self, date=None):
        """Delete the detail for a specific date."""
        if date is not None:
            date = datetime.strptime(date, self.date_detail_format).astimezone(TIMEZONE_UTC)
        DatabaseDetail(self.usage_point_id, self.measure_type).delete(date)
        return True

    def fetch(self, date):
        """Fetch the detail for a specific date."""
        if date is not None:
            date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
        result = self.run(
            datetime.combine(date - timedelta(days=2), datetime.min.time()),
            datetime.combine(date + timedelta(days=2), datetime.min.time()),
        )
        if result.get("error"):
            return {
                "error": True,
                "notif": result["description"],
                "fail_count": DatabaseDetail(self.usage_point_id, self.measure_type).get_fail_count(date),
            }

        for item in result:
            if isinstance(item["date"], str):
                item["date"] = datetime.strptime(item["date"], self.date_detail_format).astimezone(TIMEZONE_UTC)
            result_date = item["date"].strftime(self.date_format)
            if date.strftime(self.date_format) in result_date:
                item["date"] = result_date
                return item

        return {
            "error": True,
            "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})",
            "fail_count": DatabaseDetail(self.usage_point_id, self.measure_type).get_fail_count(date),
        }
