"""Query contract from gateway."""

import datetime
import json
import logging
import re
import traceback

from config import CODE_200_SUCCESS, URL
from database.contracts import DatabaseContracts
from database.usage_points import DatabaseUsagePoints
from models.query import Query


class Contract:
    """Query contract from gateway."""

    def __init__(self, headers, usage_point_id, config):
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = config

    def run(self):
        """Run the contract query process."""
        name = "contracts"
        endpoint = f"{name}/{self.usage_point_id}"
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"

        query_response = Query(endpoint=target, headers=self.headers).get()
        if query_response.status_code == CODE_200_SUCCESS:
            try:
                response_json = json.loads(query_response.text)
                response = response_json["customer"]["usage_points"][0]
                usage_point = response["usage_point"]
                contracts = response["contracts"]
                response = contracts
                response.update(usage_point)

                if contracts["offpeak_hours"] is not None:
                    offpeak_hours = re.search(r"HC \((.*)\)", contracts["offpeak_hours"]).group(1)
                else:
                    offpeak_hours = ""
                if "last_activation_date" in contracts and contracts["last_activation_date"] is not None:
                    last_activation_date = (
                        datetime.datetime.strptime(contracts["last_activation_date"], "%Y-%m-%d%z")
                    ).replace(tzinfo=None)
                else:
                    last_activation_date = contracts["last_activation_date"]
                if (
                    "last_distribution_tariff_change_date" in contracts
                    and contracts["last_distribution_tariff_change_date"] is not None
                ):
                    last_distribution_tariff_change_date = (
                        datetime.datetime.strptime(
                            contracts["last_distribution_tariff_change_date"],
                            "%Y-%m-%d%z",
                        )
                    ).replace(tzinfo=None)
                else:
                    last_distribution_tariff_change_date = contracts["last_distribution_tariff_change_date"]
                DatabaseContracts(self.usage_point_id).set(
                    {
                        "usage_point_status": usage_point["usage_point_status"],
                        "meter_type": usage_point["meter_type"],
                        "segment": contracts["segment"],
                        "subscribed_power": contracts["subscribed_power"],
                        "last_activation_date": last_activation_date,
                        "distribution_tariff": contracts["distribution_tariff"],
                        "offpeak_hours_0": offpeak_hours,
                        "offpeak_hours_1": offpeak_hours,
                        "offpeak_hours_2": offpeak_hours,
                        "offpeak_hours_3": offpeak_hours,
                        "offpeak_hours_4": offpeak_hours,
                        "offpeak_hours_5": offpeak_hours,
                        "offpeak_hours_6": offpeak_hours,
                        "contract_status": contracts["contract_status"],
                        "last_distribution_tariff_change_date": last_distribution_tariff_change_date,
                    }
                )
            except Exception as e:
                logging.error(e)
                traceback.print_exc()
                response = {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat.",
                }
            return response
        else:
            return {
                "error": True,
                "description": json.loads(query_response.text)["detail"],
            }

    def get(self):
        current_cache = DatabaseContracts(self.usage_point_id).get()
        if not current_cache:
            # No cache
            logging.info(" =>  Pas de cache")
            result = self.run()
        elif hasattr(self.usage_point_config, "refresh_contract") and self.usage_point_config.refresh_contract:
            logging.info(" =>  Mise à jour du cache")
            result = self.run()
            self.usage_point_config.refresh_contract = False
            DatabaseUsagePoints(self.usage_point_id).set(self.usage_point_config.__dict__)
        else:
            # Get data in cache
            logging.info(" =>  Récupération du cache")
            result = {}
            for column in current_cache.__table__.columns:
                result[column.name] = str(getattr(current_cache, column.name))
            logging.debug(f" => {result}")
        if "error" not in result:
            for key, value in result.items():
                logging.info(f"{key}: {value}")
        else:
            logging.error(result)
        return result
