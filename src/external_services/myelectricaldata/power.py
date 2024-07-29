"""Model to manage the power consumption data."""

import inspect
import json
import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from config.main import APP_CONFIG
from const import (
    CODE_200_SUCCESS,
    CODE_404_NOT_FOUND,
    CODE_500_INTERNAL_SERVER_ERROR,
    DAILY_MAX_DAYS,
    TIMEZONE,
    TIMEZONE_UTC,
    URL,
)
from database.contracts import DatabaseContracts
from database.max_power import DatabaseMaxPower
from database.usage_points import DatabaseUsagePoints
from models.query import Query
from utils import daterange


class Power:
    """Class to manage the power consumption data."""

    def __init__(self, headers, usage_point_id):
        self.url = URL
        self.max_daily = 1095
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = DatabaseUsagePoints(self.usage_point_id).get()
        self.contract = DatabaseContracts(self.usage_point_id).get()
        self.daily_max_days = DAILY_MAX_DAYS
        self.max_days_date = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=self.daily_max_days)
        if (
            hasattr(self.usage_point_config, "consumption_max_date")
            and self.usage_point_config.consumption_max_date != ""
            and self.usage_point_config.consumption_max_date is not None
        ):
            self.activation_date = self.usage_point_config.consumption_max_date
        elif (
            hasattr(self.contract, "last_activation_date")
            and self.contract.last_activation_date != ""
            and self.contract.last_activation_date is not None
        ):
            self.activation_date = self.contract.last_activation_date
        else:
            self.activation_date = self.max_days_date
        self.activation_date = self.activation_date.astimezone(TIMEZONE_UTC)
        self.power = DatabaseMaxPower(self.usage_point_id)

    def run(self, begin, end):  # noqa: C901, PLR0915
        """Run the query to get the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            begin_str = begin.strftime(self.date_format)
            end_str = end.strftime(self.date_format)
            logging.info(f"Récupération des données : {begin_str} => {end_str}")
            endpoint = f"daily_consumption_max_power/{self.usage_point_id}/start/{begin_str}/end/{end_str}"
            if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
                endpoint += "/cache"
            try:
                current_data = DatabaseMaxPower(self.usage_point_id).get_power(begin, end)
                if not current_data["missing_data"]:
                    logging.info(" => Toutes les données sont déjà en cache.")
                    output = []
                    for date, data in current_data["date"].items():
                        output.append({"date": date, "value": data["value"]})
                    return output
                else:
                    logging.info(" Chargement des données depuis MyElectricalData %s => %s", begin_str, end_str)
                    data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                    blacklist = 0
                    max_histo = datetime.combine(datetime.now(tz=TIMEZONE_UTC), datetime.max.time()) - timedelta(
                        days=1
                    )
                    if hasattr(data, "status_code"):
                        if data.status_code == CODE_200_SUCCESS:
                            meter_reading = json.loads(data.text)["meter_reading"]
                            if meter_reading is not None and "interval_reading" in meter_reading:
                                interval_reading = meter_reading["interval_reading"]
                                interval_reading_tmp = {}
                                for interval_reading_data in interval_reading:
                                    date_1 = datetime.strptime(
                                        interval_reading_data["date"], self.date_format_detail
                                    ).astimezone(TIMEZONE_UTC)
                                    date = datetime.combine(date_1, datetime.min.time())
                                    interval_reading_tmp[date.strftime(self.date_format)] = {
                                        "date": date_1,
                                        "value": interval_reading_data["value"],
                                    }
                                for single_date in daterange(begin, end):
                                    single_date_tz: datetime = single_date.replace(tzinfo=TIMEZONE_UTC)
                                    max_histo = max_histo.replace(tzinfo=TIMEZONE_UTC)
                                    if single_date_tz < max_histo:
                                        if single_date_tz.strftime(self.date_format) in interval_reading_tmp:
                                            # FOUND
                                            single_date_value = interval_reading_tmp[
                                                single_date_tz.strftime(self.date_format)
                                            ]
                                            self.power.insert(
                                                date=datetime.combine(single_date_tz, datetime.min.time()),
                                                event_date=single_date_value["date"],
                                                value=single_date_value["value"],
                                                blacklist=blacklist,
                                            )
                                        else:
                                            # NOT FOUND
                                            self.power.daily_fail_increment(
                                                date=datetime.combine(single_date, datetime.min.time()),
                                            )
                                return interval_reading
                            return {
                                "error": True,
                                "description": "Données non disponibles.",
                                "status_code": CODE_404_NOT_FOUND,
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
        """Get the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            end = datetime.combine((datetime.now(tz=TIMEZONE) + timedelta(days=2)), datetime.max.time()).astimezone(
                TIMEZONE
            )
            begin = datetime.combine(end - relativedelta(days=self.max_daily), datetime.min.time()).astimezone(
                TIMEZONE
            )
            result = []
            self.activation_date = self.activation_date.astimezone(TIMEZONE)
            response = self.run(begin, end)
            if response is None or ("error" in response and response.get("error", False)):
                logging.error("Echec de la récupération des données")
                if "description" in response:
                    logging.error(f'=> {response["description"]}')
                logging.error(f"=> {begin.strftime(self.date_format)} -> {end.strftime(self.date_format)}")
            return result

    def reset(self, date=None):
        """Reset the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if date is not None:
                date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
            DatabaseMaxPower(self.usage_point_id).reset_daily(date)
            return True

    def delete(self, date=None):
        """Delete the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if date is not None:
                date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
            DatabaseMaxPower(self.usage_point_id).delete_daily(date)
            return True

    def blacklist(self, date, action):
        """Blacklist the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if date is not None:
                date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
            DatabaseMaxPower(self.usage_point_id).blacklist_daily(date, action)
            return True

    def fetch(self, date):
        """Fetch the daily power consumption data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if date is not None:
                date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
            result = self.run(
                date - timedelta(days=1),
                date + timedelta(days=1),
            )
            if "error" in result and result.get("error"):
                return {
                    "error": True,
                    "notif": result["description"],
                    "fail_count": DatabaseMaxPower(self.usage_point_id).get_fail_count(date),
                }
            for item in result:
                target_date = (
                    datetime.strptime(item["date"], self.date_format_detail)
                    .astimezone(TIMEZONE_UTC)
                    .strftime(self.date_format)
                )
                event_date = (
                    datetime.strptime(item["date"], self.date_format_detail)
                    .astimezone(TIMEZONE_UTC)
                    .strftime("%H:%M:%S")
                )
                if date.strftime(self.date_format) == target_date:
                    item["date"] = target_date
                    item["event_date"] = event_date
                    return item
            return {
                "error": True,
                "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})",
                "fail_count": DatabaseMaxPower(self.usage_point_id).get_fail_count(date),
            }
