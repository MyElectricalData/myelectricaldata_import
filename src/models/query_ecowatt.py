import ast
import json
import logging
import traceback
from datetime import datetime

from dateutil.relativedelta import relativedelta

from config import URL
from dependencies import title
from init import CONFIG, DB
from models.query import Query


class Ecowatt:
    def __init__(self):
        self.config = CONFIG
        self.db = DB
        self.url = URL
        self.valid_date = datetime.combine(datetime.now() + relativedelta(days=2), datetime.min.time())

    def run(self):
        start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
        end = (datetime.now() + relativedelta(days=3)).strftime("%Y-%m-%d")
        target = f"{self.url}/rte/ecowatt/{start}/{end}"
        query_response = Query(endpoint=target).get()
        if query_response.status_code == 200:
            try:
                response_json = json.loads(query_response.text)
                for date, data in response_json.items():
                    date = datetime.strptime(date, "%Y-%m-%d")
                    self.db.set_ecowatt(date, data["value"], data["message"], str(data["detail"]))
                response = response_json
            except Exception as e:
                logging.error(e)
                traceback.print_exc()
                response = {
                    "error": True,
                    "description": "Erreur lors de la récupération des données Ecowatt.",
                }
            return response
        else:
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }

    def get(self):
        data = self.db.get_ecowatt()
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
        current_cache = self.db.get_ecowatt()
        result = {}
        if not current_cache:
            # No cache
            title(f"No cache")
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
