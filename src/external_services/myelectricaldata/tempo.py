"""Fetch tempo data from gateway and store it in the database."""
import inspect
import json
import logging
import traceback
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from config.main import APP_CONFIG
from const import CODE_200_SUCCESS, TIMEZONE, URL
from database.tempo import DatabaseTempo
from models.query import Query
from utils import title


class Tempo:
    """Fetches tempo data from gateway and stores it in the database."""

    def __init__(self):
        self.url = URL
        self.valid_date = datetime.combine(datetime.now(tz=TIMEZONE) + relativedelta(days=1), datetime.min.time())
        self.display_nb_day = 10
        self.nb_check_day = 31
        self.total_tempo_days = {
            "red": 22,
            "white": 43,
            "blue": 300,
        }

    def run(self):
        """Runs the tempo data retrieval process.

        Args:
            None

        Returns:
            A dictionary containing the retrieved tempo data.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            start = (datetime.now(tz=TIMEZONE) - relativedelta(years=3)).strftime("%Y-%m-%d")
            end = (datetime.now(tz=TIMEZONE) + relativedelta(days=2)).strftime("%Y-%m-%d")
            target = f"{self.url}/rte/tempo/{start}/{end}"
            query_response = Query(endpoint=target).get()
            if query_response.status_code == CODE_200_SUCCESS:
                try:
                    response_json: dict = json.loads(query_response.text)
                    for date, color in response_json.items():
                        date_obj = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=TIMEZONE)
                        DatabaseTempo().set(date_obj, color)
                    response = response_json
                except Exception as e:
                    logging.error(e)
                    traceback.print_exc()
                    response = {
                        "error": True,
                        "description": "Erreur lors de la récupération de données Tempo.",
                    }
                return response
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }

    def get(self):
        """Retrieves tempo data from the database.

        Args:
            None

        Returns:
            A dictionary containing the tempo data.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            data = DatabaseTempo().get()
            output = {}
            for d in data:
                if hasattr(d, "date") and hasattr(d, "color"):
                    output[d.date] = d.color
            return output

    def fetch(self):
        """Fetches tempo data from the database or retrieves it from the cache if available.

        Args:
            None

        Returns:
            A dictionary containing the tempo data.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            current_cache = DatabaseTempo().get()
            result = {}
            if not current_cache:
                # No cache
                title("No cache")
                result = self.run()
            else:
                valid_date = self.valid_date
                missing_date = False
                for i in range(self.nb_check_day):
                    if current_cache[i].date != valid_date:
                        missing_date = True
                    valid_date = valid_date - relativedelta(days=1)
                if missing_date:
                    result = self.run()
                else:
                    logging.info(" => Toutes les données sont déjà en cache.")
            if "error" not in result:
                if len(result) > 0:
                    i = 0
                    for key, value in result.items():
                        if i < self.display_nb_day:
                            logging.info(f"{key}: {value}")
                            i += 1
                    logging.info("...")
            else:
                logging.error(result)
                return "OK"
            return result

    def calc_day(self):
        """Calculates the number of days left for each color based on the current date.

        Args:
            None

        Returns:
            A dictionary containing the number of days left for each color.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            now = datetime.now(tz=TIMEZONE)
            begin = datetime.combine(now.replace(month=9, day=1), datetime.min.time()).astimezone(TIMEZONE)
            if now < begin:
                begin = begin.replace(year=int(now.strftime("%Y")) - 1)
            end = datetime.combine(begin - timedelta(hours=5), datetime.max.time()).replace(
                year=int(begin.strftime("%Y")) + 1
            )
            current_tempo_day = DatabaseTempo().get_range(begin=begin, end=end)
            result = self.total_tempo_days
            for day in current_tempo_day:
                result[day.color.lower()] -= 1
            DatabaseTempo().set_config("days", result)
            logging.info(" => OK")
            return result

    def fetch_day(self):
        """Fetches tempo days data from the API and updates the database.

        Args:
            None

        Returns:
            A dictionary containing the tempo days data.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            target = f"{self.url}/edf/tempo/days"
            query_response = Query(endpoint=target).get()
            if query_response.status_code == CODE_200_SUCCESS:
                try:
                    response_json = json.loads(query_response.text)
                    DatabaseTempo().set_config("days", response_json)
                    response = {"error": False, "description": "", "items": response_json}
                    logging.info(" => Toutes les valeurs sont mises à jour.")
                except Exception as e:
                    logging.error(e)
                    traceback.print_exc()
                    response = {
                        "error": True,
                        "description": "Erreur lors de la récupération de jours Tempo.",
                    }
                return response
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }

    def fetch_price(self):
        """Fetches tempo price data from the API and updates the database.

        Args:
            None

        Returns:
            A dictionary containing the tempo price data.

        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            target = f"{self.url}/edf/tempo/price"
            query_response = Query(endpoint=target).get()
            if query_response.status_code == CODE_200_SUCCESS:
                try:
                    response_json = json.loads(query_response.text)
                    DatabaseTempo().set_config("price", response_json)
                    response = {"error": False, "description": "", "items": response_json}
                    logging.info(" => Toutes les valeurs sont misent à jours.")
                except Exception as e:
                    logging.error(e)
                    traceback.print_exc()
                    response = {
                        "error": True,
                        "description": "Erreur lors de la récupération de jours Tempo.",
                    }
                return response
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }
