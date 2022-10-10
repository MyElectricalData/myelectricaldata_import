import json
import re

import datetime
import sys

from dateutil.relativedelta import relativedelta
import pytz
from mergedeep import Strategy, merge

import __main__
from config import URL, DETAIL_MAX_DAYS
from dependencies import *
from models.query import Query


class ConsumptionDetail:

    def __init__(self, headers, usage_point_id, config, activation_date, offpeak_hours):

        self.cache = __main__.CACHE
        self.url = URL
        self.max_detail = 7

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config
        if activation_date:
            self.activation_date = datetime.datetime.strptime(activation_date, "%Y-%m-%d%z").replace(tzinfo=None)
        else:
            self.activation_date = activation_date

        if offpeak_hours:
            self.offpeak_hours = re.search('HC \((.*)\)', offpeak_hours).group(1).split(";")
        else:
            self.offpeak_hours = []

        self.daily_max_days = DETAIL_MAX_DAYS
        self.max_days_date = datetime.datetime.utcnow() - relativedelta(days=self.daily_max_days)

        self.base_price = self.config['consumption_price_base']

    def run(self, begin, end, cache=True):
        begin = begin.strftime('%Y-%m-%d')
        end = end.strftime('%Y-%m-%d')
        log(f"Récupération des données : {begin} => {end}")
        endpoint = f"consumption_load_curve/{self.usage_point_id}/start/{begin}/end/{end}"
        if "cache" in self.config and self.config["cache"] and cache:
            endpoint += "/cache"
        try:
            current_data = self.cache.get_consumption_detail(usage_point_id=self.usage_point_id, begin=begin, end=end)
            if not current_data["missing_data"] and cache:
                log(" => Toutes les données sont déjà en cache.")
                output = []
                for date, data in current_data["date"].items():
                    output.append({'date': date, "value": data["value"]})
                return output
            else:
                log(f" => Chargement des données depuis MyElectricalData {begin} => {end}")
                data = Query(endpoint=f"{self.url}/{endpoint}/", headers=self.headers).get()
                if data.status_code == 200:
                    meter_reading = json.loads(data.text)['meter_reading']
                    for interval_reading in meter_reading["interval_reading"]:
                        value = interval_reading["value"]
                        interval = re.findall(r'\d+', interval_reading['interval_length'])[0]
                        date = interval_reading["date"]
                        dateObject = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                        dateHourMinute = dateObject.strftime('%H:%M')
                        measure_type = "HP"
                        if self.offpeak_hours:
                            for offpeak_hour in self.offpeak_hours:
                                offpeak_begin = offpeak_hour.split("-")[0].replace('h', ':').replace('H', ':')
                                # FORMAT HOUR WITH 2 DIGIT
                                offpeak_begin = datetime.datetime.strptime(offpeak_begin, '%H:%M')
                                offpeak_begin = datetime.datetime.strftime(offpeak_begin, '%H:%M')
                                offpeak_stop = offpeak_hour.split("-")[1].replace('h', ':').replace('H', ':')
                                # FORMAT HOUR WITH 2 DIGIT
                                offpeak_stop = datetime.datetime.strptime(offpeak_stop, '%H:%M')
                                offpeak_stop = datetime.datetime.strftime(offpeak_stop, '%H:%M')
                                result = is_between(dateHourMinute, (offpeak_begin, offpeak_stop))
                                if result == True:
                                    measure_type = "HC"
                        self.cache.insert_consumption_detail(
                            usage_point_id=self.usage_point_id,
                            date=date, value=value,
                            interval=interval,
                            measure_type=measure_type,
                            fail=0
                        )
                    return meter_reading["interval_reading"]
                else:
                    return {
                        "error": True,
                        "description": "Erreur lors de la récupération de la consommation détaillé.",
                        "result": data
                    }
        except Exception as e:
            logError(e)

    def get(self):

        # REMOVE TODAY
        begin = datetime.datetime.now() - relativedelta(days=self.max_detail)
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
                begin = begin - relativedelta(days=self.max_detail)
                end = end - relativedelta(days=self.max_detail)

            if "error" in response and response["error"]:
                logError([
                    "Echec de la récupération des données.",
                    f' => {response["description"]}',
                    f" => {begin.strftime('%Y-%m-%d')} -> {end.strftime('%Y-%m-%d')}",
                    f"",
                    f"Result :",
                    f"{response['result']}",
                    f"{response['result'].text}",
                ])

            count += 1


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]
