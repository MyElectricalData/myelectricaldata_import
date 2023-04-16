import __main__ as app
import json
import re
import traceback
from datetime import datetime
from dateutil.relativedelta import relativedelta

# from dependencies import *
from models.query import Query

from config import URL


class Ecowatt:

    def __init__(self):
        self.db = app.DB
        self.url = URL
        self.valid_date = datetime.combine(datetime.now() + relativedelta(days=1), datetime.min.time())

    def run(self):
        start = (datetime.now() - relativedelta(years=3)).strftime("%Y-%m-%d")
        end = (datetime.now() + relativedelta(days=2)).strftime("%Y-%m-%d")
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
                app.LOG.error(e)
                traceback.print_exc()
                response = {
                    "error": True,
                    "description": "Erreur lors de la récupération des données Ecowatt."
                }
            return response
        else:
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"]
            }

    def get(self):
        current_cache = self.db.get_ecowatt()
        result = {}
        if not current_cache:
            # No cache
            app.LOG.log(f" => No cache")
            result = self.run()
        else:
            last_item = current_cache[0]
            if last_item.date < self.valid_date:
                result = self.run()
            else:
                app.LOG.log(" => Toutes les données sont déjà en cache")
        if "error" not in result:
            for key, value in result.items():
                app.LOG.log(f"{key}: {value['message']}")
        else:
            app.LOG.error(result)
            return "OK"
        return result
