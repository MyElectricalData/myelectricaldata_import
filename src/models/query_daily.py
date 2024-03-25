"""The 'Daily' class represents a daily data retrieval and manipulation process for a specific usage point."""

import json
import logging
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from config import (
    CODE_200_SUCCESS,
    CODE_400_BAD_REQUEST,
    CODE_403_FORBIDDEN,
    CODE_409_CONFLICT,
    CODE_500_INTERNAL_SERVER_ERROR,
    DAILY_MAX_DAYS,
    TIMEZONE_UTC,
    URL,
)
from database.contracts import DatabaseContracts
from database.daily import DatabaseDaily
from database.usage_points import DatabaseUsagePoints
from dependencies import daterange
from models.query import Query
from models.stat import Stat


class Daily:
    """The 'Daily' class represents a daily data retrieval and manipulation process for a specific usage point.

    It provides methods for fetching, resetting, deleting, and blacklisting daily data.

    Attributes:
        config (dict): The configuration settings.
        db (object): The database object.
        url (str): The base URL for API requests.
        max_daily (int): The maximum number of days to retrieve data for.
        date_format (str): The format of dates.
        date_detail_format (str): The format of detailed dates.
        headers (dict): The headers for API requests.
        usage_point_id (str): The ID of the usage point.
        usage_point_config (object): The configuration settings for the usage point.
        contract (object): The contract associated with the usage point.
        daily_max_days (int): The maximum number of days for daily data.
        max_days_date (datetime): The maximum date for retrieving data.
        activation_date (datetime): The activation date for retrieving data.
        measure_type (str): The type of measurement (consumption or production).
        base_price (float): The base price for the measurement type.

    Methods:
        run(begin, end):
            Retrieves and stores daily data for a specified date range.

        get():
            Retrieves and returns all available daily data for the usage point.

        reset(date=None):
            Resets the daily data for the usage point, optionally for a specific date.

        delete(date=None):
            Deletes the daily data for the usage point, optionally for a specific date.

        fetch(date):
            Fetches and returns the daily data for a specific date.

        blacklist(date, action):
            Adds or removes a date from the blacklist for the usage point.

    Note:
        The 'Daily' class relies on the 'Query' class for making API requests and the 'Stat' class for retrieving additional statistics.

    Example usage:
        headers = {"Authorization": "Bearer token"}
        usage_point_id = "1234567890"
        daily = Daily(headers, usage_point_id)
        data = daily.get()
        for item in data:
            print(item)
    """

    def __init__(self, headers, usage_point_id, measure_type="consumption"):
        self.url = URL
        self.max_daily = 1095
        self.date_format = "%Y-%m-%d"
        self.date_detail_format = "%Y-%m-%d %H:%M:%S"
        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = DatabaseUsagePoints(self.usage_point_id).get()
        self.contract = DatabaseContracts(self.usage_point_id).get()
        self.daily_max_days = int(DAILY_MAX_DAYS)
        self.max_days_date = datetime.now(tz=TIMEZONE_UTC) - timedelta(days=self.daily_max_days)
        if (
            measure_type == "consumption"
            and hasattr(self.usage_point_config, "consumption_max_date")
            and self.usage_point_config.consumption_max_date != ""
            and self.usage_point_config.consumption_max_date is not None
        ):
            self.activation_date = self.usage_point_config.consumption_max_date
        elif (
            measure_type == "production"
            and hasattr(self.usage_point_config, "production_max_date")
            and self.usage_point_config.production_max_date != ""
            and self.usage_point_config.production_max_date is not None
        ):
            self.activation_date = self.usage_point_config.production_max_date
        elif (
            hasattr(self.contract, "last_activation_date")
            and self.contract.last_activation_date != ""
            and self.contract.last_activation_date is not None
        ):
            self.activation_date = self.contract.last_activation_date
        else:
            self.activation_date = self.max_days_date
        self.measure_type = measure_type
        self.base_price = 0
        if measure_type == "consumption":
            if hasattr(self.usage_point_config, "consumption_price_base"):
                self.base_price = self.usage_point_config.consumption_price_base
        elif hasattr(self.usage_point_config, "production_price"):
            self.base_price = self.usage_point_config.production_price

    def run(self, begin, end):
        """Retrieves and stores daily data for a specified date range."""
        begin_str = begin.strftime(self.date_format)
        end_str = end.strftime(self.date_format)
        logging.info(f"Récupération des données : {begin_str} => {end_str}")
        endpoint = f"daily_{self.measure_type}/{self.usage_point_id}/start/{begin_str}/end/{end_str}"
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        try:
            current_data = DatabaseDaily(self.usage_point_id, self.measure_type).get(begin, end)
            if not current_data["missing_data"]:
                logging.info(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({"date": date, "value": data["value"]})
                return output
            else:
                logging.info(f" Chargement des données depuis MyElectricalData {begin_str} => {end_str}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
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
                else:
                    blacklist = 0
                    max_histo = datetime.combine(datetime.now(tz=TIMEZONE_UTC), datetime.max.time()) - timedelta(
                        days=1
                    )
                    if hasattr(data, "status_code"):
                        if data.status_code == CODE_200_SUCCESS:
                            meter_reading = json.loads(data.text)["meter_reading"]
                            interval_reading = meter_reading["interval_reading"]
                            interval_reading_tmp = {}
                            for interval_reading_data in interval_reading:
                                interval_reading_tmp[interval_reading_data["date"]] = interval_reading_data["value"]
                            for single_date in daterange(begin, end):
                                single_date_tz = single_date.replace(tzinfo=TIMEZONE_UTC)
                                max_histo = max_histo.replace(tzinfo=TIMEZONE_UTC)
                                if single_date_tz < max_histo:
                                    if single_date_tz.strftime(self.date_format) in interval_reading_tmp:
                                        # FOUND
                                        DatabaseDaily(self.usage_point_id, self.measure_type).insert(
                                            date=datetime.combine(single_date_tz, datetime.min.time()),
                                            value=interval_reading_tmp[single_date_tz.strftime(self.date_format)],
                                            blacklist=blacklist,
                                        )
                                    else:
                                        # NOT FOUND
                                        DatabaseDaily(self.usage_point_id, self.measure_type).fail_increment(
                                            date=datetime.combine(single_date_tz, datetime.min.time()),
                                        )
                            return interval_reading
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
        """Generate a range of dates between a start date and an end date.

        Parameters:
            start_date (datetime.date): The start date of the range.
            end_date (datetime.date): The end date of the range.

        Yields:
            datetime.date: The next date in the range.

        Example:
            >>> start_date = datetime.date(2021, 1, 1)
            >>> end_date = datetime.date(2021, 1, 5)
            >>> for date in daterange(start_date, end_date):
            ...     print(date)
            ...
            2021-01-01
            2021-01-02
            2021-01-03
            2021-01-04

        Note:
            The end date is exclusive, meaning it is not included in the range.
        """
        end = datetime.combine((datetime.now(tz=TIMEZONE_UTC) + timedelta(days=2)), datetime.max.time()).astimezone(
            TIMEZONE_UTC
        )
        begin = datetime.combine(end - relativedelta(days=self.max_daily), datetime.min.time()).astimezone(
            TIMEZONE_UTC
        )
        finish = True
        result = []
        print(self.activation_date, begin)
        self.activation_date = self.activation_date.astimezone(TIMEZONE_UTC)
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
                begin = begin - relativedelta(months=self.max_daily)
                end = end - relativedelta(months=self.max_daily)
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
                logging.error("Echec de la récupération des données")
                logging.error(f'=> {response["description"]}')
                logging.error(f"=> {begin.strftime(self.date_format)} -> {end.strftime(self.date_format)}")
            if "status_code" in response and (
                response["status_code"] == CODE_409_CONFLICT or response["status_code"] == CODE_400_BAD_REQUEST
            ):
                finish = False
                logging.error("Arrêt de la récupération des données suite à une erreur.")
                logging.error(
                    "Prochain lancement à "
                    f"{datetime.now(tz=TIMEZONE_UTC) + timedelta(seconds=self.config.get('cycle'))}"
                )
        return result

    def reset(self, date=None):
        """Resets the daily data for the usage point, optionally for a specific date."""
        if date is not None:
            date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
        DatabaseDaily(self.usage_point_id, self.measure_type).reset(date)
        return True

    def delete(self, date=None):
        """Deletes the daily data for the usage point, optionally for a specific date."""
        if date is not None:
            date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
        DatabaseDaily(self.usage_point_id, self.measure_type).delete(date)
        return True

    def fetch(self, date):
        """Fetches and returns the daily data for a specific date."""
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
                "fail_count": DatabaseDaily(self.usage_point_id, date, self.measure_type).get_fail_count(),
            }
        for item in result:
            if date.strftime(self.date_format) in item["date"]:
                print(Stat(self.usage_point_id, self.measure_type).get_daily(date, "hc"))
                item["hc"] = Stat(self.usage_point_id, self.measure_type).get_daily(date, "hc")
                item["hp"] = Stat(self.usage_point_id, self.measure_type).get_daily(date, "hp")
                return item
        return {
            "error": True,
            "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})",
            "fail_count": DatabaseDaily(self.usage_point_id, date, self.measure_type).get_fail_count(),
        }

    def blacklist(self, date, action):
        """Adds or removes a date from the blacklist for the usage point."""
        if date is not None:
            date = datetime.strptime(date, self.date_format).astimezone(TIMEZONE_UTC)
        DatabaseDaily(self.usage_point_id, date, self.measure_type).blacklist(date, action)
        return True
