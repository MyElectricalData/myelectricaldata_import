import json

import datetime
import sys

from dateutil.relativedelta import relativedelta
import pytz
from mergedeep import Strategy, merge

import __main__
from dependencies import *
from config import URL, DAILY_MAX_DAYS
from models.query import Query


class ConsumptionDaily:

    def __init__(self, headers, usage_point_id, config, activation_date):

        self.cache = __main__.CACHE
        self.url = URL
        self.max_daily = 36

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config
        if activation_date:
            self.activation_date = datetime.datetime.strptime(activation_date, "%Y-%m-%d%z").replace(tzinfo=None)
        else:
            self.activation_date = activation_date

        self.daily_max_days = DAILY_MAX_DAYS
        self.max_days_date = datetime.datetime.utcnow() - relativedelta(days=self.daily_max_days)

        self.base_price = self.config['consumption_price_base']

    def run(self, begin, end, cache=True):
        begin = begin.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        log(f"Récupération des données : {begin} => {end}")
        endpoint = f"daily_consumption/{self.usage_point_id}/start/{begin}/end/{end}"
        if "cache" in self.config and self.config["cache"] and cache:
            endpoint += "/cache"
        try:
            current_data = self.cache.get_consumption_daily(usage_point_id=self.usage_point_id, begin=begin, end=end)
            if not current_data["missing_data"]:
                log(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({'date': date, "value": data["value"]})
                return output
            else:
                log(f" => Chargement des données depuis MyElectricalData {begin} => {end}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                fail = 0
                if data.status_code == 200:
                    meter_reading = json.loads(data.text)['meter_reading']
                    # debug(meter_reading["interval_reading"])
                    for interval_reading in meter_reading["interval_reading"]:
                        value = interval_reading["value"]
                        date = interval_reading["date"]
                        self.cache.insert_consumption_daily(usage_point_id=self.usage_point_id, date=date, value=value, fail=fail)
                    return meter_reading["interval_reading"]
                else:
                    return {
                        "error": True,
                        "description": "Erreur lors de la récupération de la consommation journalière."
                    }
        except Exception as e:
            logError(e)

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
                result = [*result, *response]
            elif self.max_days_date > begin:
                # Max day reached
                begin = self.max_days_date
                finish = False
                response = self.run(begin, end)
                result = [*result, *response]
            else:
                if count == 0:
                    response = self.run(begin, end, cache=False)
                else:
                    response = self.run(begin, end)
                result = [*result, *response]
                begin = begin - relativedelta(days=self.max_daily)
                end = end - relativedelta(days=self.max_daily)

            if "error" in response and response["error"]:
                logError(["Echec de la récupération des données.", f' => {response["description"]}',
                          f" => {begin.strftime('%Y-%m-%d')} -> {end.strftime('%Y-%m-%d')}"])

            count += 1

        return result
