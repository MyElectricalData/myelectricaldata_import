import datetime
import json

import __main__ as app
from config import DAILY_MAX_DAYS, URL
from dependencies import *
from models.query import Query

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


class Daily:

    def __init__(self, headers, usage_point_id, measure_type="consumption"):
        self.db = app.DB
        self.url = URL
        self.max_daily = 36
        self.date_format = '%Y-%m-%d'
        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = self.db.get_usage_point(self.usage_point_id)
        self.contract = self.db.get_contract(self.usage_point_id)
        self.daily_max_days = DAILY_MAX_DAYS
        self.max_days_date = datetime.datetime.utcnow() - datetime.timedelta(days=self.daily_max_days)
        if measure_type == "consumption" and hasattr(self.usage_point_config, "consumption_max_date"):
            self.activation_date = self.usage_point_config.consumption_max_date
        elif measure_type == "production" and hasattr(self.usage_point_config, "production_max_date"):
            self.activation_date = self.usage_point_config.production_max_date
        elif hasattr(self.contract, "last_activation_date"):
            self.activation_date = self.contract.last_activation_date
        else:
            self.activation_date = self.max_days_date
        self.measure_type = measure_type
        self.base_price = 0
        if measure_type == "consumption":
            if hasattr(self.usage_point_config, "consumption_price_base"):
                self.base_price = self.usage_point_config.consumption_price_base
        else:
            if hasattr(self.usage_point_config, "production_price"):
                self.base_price = self.usage_point_config.production_price

    def run(self, begin, end):
        begin_str = begin.strftime(self.date_format)
        end_str = end.strftime(self.date_format)
        app.LOG.log(f"Récupération des données : {begin_str} => {end_str}")
        endpoint = f"daily_{self.measure_type}/{self.usage_point_id}/start/{begin_str}/end/{end_str}"
        # if begin < datetime.datetime.now() - datetime.timedelta(days=7):
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        try:
            current_data = self.db.get_daily(self.usage_point_id, begin, end, self.measure_type)
            if not current_data["missing_data"]:
                app.LOG.log(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({'date': date, "value": data["value"]})
                return output
            else:
                app.LOG.log(f" => Chargement des données depuis MyElectricalData {begin_str} => {end_str}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                blacklist = 0
                if hasattr(data, "status_code"):
                    if data.status_code == 200:
                        meter_reading = json.loads(data.text)['meter_reading']
                        interval_reading = meter_reading["interval_reading"]
                        interval_reading_tmp = {}
                        for interval_reading_data in interval_reading:
                            interval_reading_tmp[interval_reading_data["date"]] = interval_reading_data["value"]
                        for single_date in daterange(begin, end):
                            if single_date.strftime(self.date_format) in interval_reading_tmp:
                                # FOUND
                                self.db.insert_daily(
                                    usage_point_id=self.usage_point_id,
                                    date=datetime.datetime.combine(single_date, datetime.datetime.min.time()),
                                    value=interval_reading_tmp[single_date.strftime(self.date_format)],
                                    blacklist=blacklist,
                                    measurement_direction=self.measure_type
                                )
                            else:
                                # NOT FOUND
                                self.db.daily_fail_increment(
                                    usage_point_id=self.usage_point_id,
                                    date=datetime.datetime.combine(single_date, datetime.datetime.min.time()),
                                    measurement_direction=self.measure_type
                                )
                        return interval_reading
                    else:
                        return {
                            "error": True,
                            "description": json.loads(data.text)["detail"],
                            "status_code": data.status_code
                        }
                else:
                    return {
                        "error": True,
                        "description": json.loads(data.text)["detail"],
                        "status_code": data.status_code
                    }
        except Exception as e:
            app.LOG.exception(e)
            app.LOG.error(e)

    def get(self):

        # REMOVE TODAY
        begin = datetime.datetime.now() - datetime.timedelta(days=self.max_daily)
        end = datetime.datetime.now()
        finish = True
        result = []
        count = 0

        while finish:

            if self.activation_date and self.activation_date > begin:
                # Activation date reached
                begin = self.activation_date
                finish = False
                response = self.run(begin, end)
            elif self.max_days_date > begin:
                # Max day reached
                begin = self.max_days_date
                finish = False
                response = self.run(begin, end)
            else:
                response = self.run(begin, end)
                begin = begin - datetime.timedelta(days=self.max_daily)
                end = end - datetime.timedelta(days=self.max_daily)
            if response is not None:
                result = [*result, *response]
            else:
                response = {
                    "error": True,
                    "description": "MyElectricalData est indisponible."
                }
                app.LOG.error(error)
            if "error" in response and response["error"]:
                error = [
                    "Echec de la récupération des données.",
                    f' => {response["description"]}',
                    f" => {begin.strftime(self.date_format)} -> {end.strftime(self.date_format)}",
                ]
                app.LOG.error(error)

            if "status_code" in response and (response["status_code"] == 409 or response["status_code"] == 400):
                finish = False
                error = ["Arrêt de la récupération des données suite à une erreur.",
                        f"Prochain lancement à {datetime.datetime.now() + datetime.timedelta(seconds=app.CONFIG.get('cycle'))}"]
                app.LOG.warning(error)

            count += 1
        return result

    def reset(self, date=None):
        if date is not None:
            date = datetime.datetime.strptime(date, self.date_format)
        self.db.delete_daily(self.usage_point_id, date, self.measure_type)
        return True

    def fetch(self, date):
        if date is not None:
            date = datetime.datetime.strptime(date, self.date_format)
        result = self.run(
            date - datetime.timedelta(days=1),
            date + datetime.timedelta(days=1),
        )
        if "error" in result and result["error"]:
            return {
                "error": True,
                "notif": result['description'],
                "fail_count": self.db.get_daily_fail_count(self.usage_point_id, date, self.measure_type)
            }
        for item in result:
            if date.strftime(self.date_format) in item['date']:
                return item
        return {
            "error": True,
            "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})",
            "fail_count": self.db.get_daily_fail_count(self.usage_point_id, date, self.measure_type)
        }

    def blacklist(self, date, action):
        if date is not None:
            date = datetime.datetime.strptime(date, self.date_format)
        self.db.blacklist_daily(self.usage_point_id, date, action, self.measure_type)
        return True
