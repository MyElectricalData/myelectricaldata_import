import __main__ as app
import datetime
import json
import re

from sqlalchemy.sql import func

from dependencies import *
from models.query import Query

from config import URL


class Contract:

    def __init__(self, headers, usage_point_id, config):
        self.db = app.DB
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = config

    def run(self):

        name = "contracts"
        endpoint = f"{name}/{self.usage_point_id}"
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"

        query_response = Query(endpoint=target, headers=self.headers).get()
        if query_response.status_code == 200:
            try:
                response_json = json.loads(query_response.text)
                response = response_json["customer"]["usage_points"][0]
                usage_point = response["usage_point"]
                contracts = response["contracts"]
                if contracts['offpeak_hours'] is not None:
                    offpeak_hours = re.search('HC \((.*)\)', contracts['offpeak_hours']).group(1)
                else:
                    offpeak_hours = ""
                last_activation_date = (
                    datetime.datetime.strptime(contracts['last_activation_date'], '%Y-%m-%d%z')
                ).replace(tzinfo=None)
                last_distribution_tariff_change_date = (
                    datetime.datetime.strptime(contracts['last_distribution_tariff_change_date'], '%Y-%m-%d%z')
                ).replace(tzinfo=None)
                self.db.set_contract(self.usage_point_id, {
                    "usage_point_status": usage_point["usage_point_status"],
                    "meter_type": usage_point["meter_type"],
                    "segment": contracts['segment'],
                    "subscribed_power": contracts['subscribed_power'],
                    "last_activation_date": last_activation_date,
                    "distribution_tariff": contracts['distribution_tariff'],
                    "offpeak_hours_0": offpeak_hours,
                    "offpeak_hours_1": offpeak_hours,
                    "offpeak_hours_2": offpeak_hours,
                    "offpeak_hours_3": offpeak_hours,
                    "offpeak_hours_4": offpeak_hours,
                    "offpeak_hours_5": offpeak_hours,
                    "offpeak_hours_6": offpeak_hours,
                    "contract_status": contracts['contract_status'],
                    "last_distribution_tariff_change_date": last_distribution_tariff_change_date
                })
            except Exception as e:
                app.LOG.error(e)
                response = {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }
            return response
        else:
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"]
            }

    def get(self):
        current_cache = self.db.get_contract(usage_point_id=self.usage_point_id)
        if not current_cache:
            # No cache
            app.LOG.log(f" => No cache")
            result = self.run()
        else:
            # Refresh cache
            if hasattr(self.usage_point_config, "refresh_contract") and self.usage_point_config.refresh_contract:
                app.LOG.log(f" => Refresh Cache")
                result = self.run()
            else:
                # Get data in cache
                app.LOG.log(f" => Query Cache")
                result = {}
                for column in current_cache.__table__.columns:
                    result[column.name] = str(getattr(current_cache, column.name))
                app.LOG.debug(f" => {result}")
        if "error" not in result:
            for key, value in result.items():
                app.LOG.log(f"{key}: {value}")
        else:
            app.LOG.error(result)
        return result
