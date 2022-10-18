import __main__ as app
import datetime
import json

from dateutil.relativedelta import relativedelta
from dependencies import *
from models.query import Query

from config import URL, DAILY_MAX_DAYS


class ProductionDaily:

    def __init__(self, headers, usage_point_id, config, activation_date=None):

        self.cache = app.CACHE
        self.url = URL
        self.max_daily = 36

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config

        if activation_date is not None:
            self.activation_date = datetime.datetime.strptime(activation_date, "%Y-%m-%d%z").replace(tzinfo=None)
        else:
            self.activation_date = activation_date

        self.daily_max_days = DAILY_MAX_DAYS
        self.max_days_date = datetime.datetime.utcnow() - relativedelta(days=self.daily_max_days)

        if "production_price" in self.config:
            self.base_price = self.config['production_price']
        else:
            self.base_price = 0

    def run(self, begin, end, cache=True):
        begin = begin.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        app.LOG.log(f"Récupération des données : {begin} => {end}")
        endpoint = f"daily_production/{self.usage_point_id}/start/{begin}/end/{end}"
        if "cache" in self.config and self.config["cache"] and cache:
            endpoint += "/cache"
        try:
            current_data = self.cache.get_production_daily(usage_point_id=self.usage_point_id, begin=begin, end=end)
            if not current_data["missing_data"]:
                app.LOG.log(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({'date': date, "value": data["value"]})
                return output
            else:
                app.LOG.log(f" => Chargement des données depuis MyElectricalData {begin} => {end}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                blacklist = 0
                if hasattr(data, "status_code"):
                    if data.status_code == 200:
                        meter_reading = json.loads(data.text)['meter_reading']
                        for interval_reading in meter_reading["interval_reading"]:
                            value = interval_reading["value"]
                            date = interval_reading["date"]
                            self.cache.insert_production_daily(usage_point_id=self.usage_point_id, date=date,
                                                               value=value,
                                                               blacklist=blacklist)
                        return meter_reading["interval_reading"]
                    else:
                        return {
                            "error": True,
                            "description": json.loads(data.text)["detail"],
                            # "enedis": data.text
                        }
                else:
                    return {
                        "error": True,
                        "description": json.loads(data.text)["detail"],
                        # "enedis": data.text
                    }
        except Exception as e:
            app.LOG.error(e)

    def get(self):

        # REMOVE TODAY
        begin = datetime.datetime.now() - relativedelta(days=self.max_daily)
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
                if count == 0:
                    response = self.run(begin, end, cache=False)
                else:
                    response = self.run(begin, end)
                begin = begin - relativedelta(days=self.max_daily)
                end = end - relativedelta(days=self.max_daily)
            if response is not None:
                result = [*result, *response]
            else:
                response = {
                    "error": True,
                    "description": "MyElectricalData est indisponible."
                }

            if "error" in response and response["error"]:
                error = [
                    "Echec de la récupération des données.",
                    f' => {response["description"]}',
                    f" => {begin.strftime('%Y-%m-%d')} -> {end.strftime('%Y-%m-%d')}",
                ]
                app.LOG.error(error)

            count += 1
        return result

    def reset(self, date=None):
        self.cache.delete_production_daily(usage_point_id=self.usage_point_id, date=date)
        return True

    def fetch(self, date):
        result = self.run(datetime.datetime.strptime(date, "%Y-%m-%d") - relativedelta(days=1),
                          datetime.datetime.strptime(date, "%Y-%m-%d") + relativedelta(days=1), True)
        print(result)
        if "error" in result and result["error"]:
            return {
                "error": True,
                "notif": result['description']
            }
        for item in result:
            if date in item['date']:
                return item
        return {
            "error": True,
            "notif": f"Aucune donnée n'est disponible chez Enedis sur cette date ({date})"
        }

    def blacklist(self, date, action):
        app.LOG.show(self.cache.blacklist_production_daily(self.usage_point_id, date, action))
        return True
