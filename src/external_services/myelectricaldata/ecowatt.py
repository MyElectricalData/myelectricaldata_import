"""Fetch and store Ecowatt data."""

import ast
import inspect
import json
import logging
import traceback
from datetime import datetime

from dateutil.relativedelta import relativedelta

from config.main import APP_CONFIG
from const import CODE_200_SUCCESS, TIMEZONE, URL
from database.ecowatt import DatabaseEcowatt
from models.query import Query
from utils import title


class Ecowatt:
    """Class for fetching and storing Ecowatt data."""

    def __init__(self):
        self.url = URL
        self.valid_date = datetime.combine(datetime.now(tz=TIMEZONE) + relativedelta(days=2), datetime.min.time())

    def run(self):
        """Fetches Ecowatt data from the API and stores it in the database."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            start = (datetime.now(tz=TIMEZONE) - relativedelta(years=3)).strftime("%Y-%m-%d")
            end = (datetime.now(tz=TIMEZONE) + relativedelta(days=3)).strftime("%Y-%m-%d")
            target = f"{self.url}/rte/ecowatt/{start}/{end}"
            query_response = Query(endpoint=target).get()
            if query_response.status_code == CODE_200_SUCCESS:
                try:
                    response_json = json.loads(query_response.text)
                    for date, data in response_json.items():
                        date_obj = datetime.strptime(date, "%Y-%m-%d").astimezone(TIMEZONE)
                        DatabaseEcowatt().set(date_obj, data["value"], data["message"], str(data["detail"]))
                    response = response_json
                except Exception as e:
                    logging.error(e)
                    traceback.print_exc()
                    response = {
                        "error": True,
                        "description": "Erreur lors de la récupération des données Ecowatt.",
                    }
                return response
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }

    def get(self):
        """Retrieve Ecowatt data from the database and format it as a dictionary."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            data = DatabaseEcowatt().get()
            output = {}
            for d in data:
                if hasattr(d, "date") and hasattr(d, "value") and hasattr(d, "message") and hasattr(d, "detail"):
                    output[d.date] = {
                        "value": d.value,
                        "message": d.message,
                        "detail": ast.literal_eval(d.detail),
                    }
            return output

    def fetch(self):
        """Fetches Ecowatt data and returns the result."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            current_cache = DatabaseEcowatt().get()
            result = {}
            if not current_cache:
                title("No cache")
                result = self.run()
            else:
                last_item = current_cache[0]
                if last_item.date < self.valid_date:
                    result = self.run()
                else:
                    logging.info(" => Toutes les données sont déjà en cache.")
            if "error" not in result:
                for key, value in result.items():
                    logging.info(f"{key}: {value['message']}")
            else:
                logging.error(result)
                return "OK"
            return result
