"""Fetch address data from the API and store it in the database."""

import inspect
import json
import logging
import traceback

from config.main import APP_CONFIG
from const import CODE_200_SUCCESS, URL
from database.addresses import DatabaseAddresses
from database.usage_points import DatabaseUsagePoints
from models.query import Query


class Address:
    """Fetch address data from the API and store it in the database."""

    def __init__(self, headers, usage_point_id):
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = APP_CONFIG.usage_point_id_config(self.usage_point_id)

    def run(self):
        """Run the address query process."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            name = "addresses"
            endpoint = f"{name}/{self.usage_point_id}"
            if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
                endpoint += "/cache"
            target = f"{self.url}/{endpoint}"

            response = Query(endpoint=target, headers=self.headers).get()
            if response.status_code == CODE_200_SUCCESS:
                try:
                    response_json = json.loads(response.text)
                    response = response_json["customer"]["usage_points"][0]
                    usage_point = response["usage_point"]
                    usage_point_addresses = usage_point["usage_point_addresses"]
                    response = usage_point_addresses
                    response.update(usage_point)
                    DatabaseAddresses(self.usage_point_id).set(
                        {
                            "usage_points": str(usage_point["usage_point_id"])
                            if usage_point["usage_point_id"] is not None
                            else "",
                            "street": str(usage_point_addresses["street"])
                            if usage_point_addresses["street"] is not None
                            else "",
                            "locality": str(usage_point_addresses["locality"])
                            if usage_point_addresses["locality"] is not None
                            else "",
                            "postal_code": str(usage_point_addresses["postal_code"])
                            if usage_point_addresses["postal_code"] is not None
                            else "",
                            "insee_code": str(usage_point_addresses["insee_code"])
                            if usage_point_addresses["insee_code"] is not None
                            else "",
                            "city": str(usage_point_addresses["city"])
                            if usage_point_addresses["city"] is not None
                            else "",
                            "country": str(usage_point_addresses["country"])
                            if usage_point_addresses["country"] is not None
                            else "",
                            "geo_points": str(usage_point_addresses["geo_points"])
                            if usage_point_addresses["geo_points"] is not None
                            else "",
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
                return {"error": True, "description": json.loads(response.text)["detail"]}

    def get(self):
        """Retrieve address data from the database and format it as a dictionary."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            current_cache = DatabaseAddresses(self.usage_point_id).get()
            if not current_cache:
                # No cache
                logging.info(" =>  Pas de cache")
                result = self.run()
            elif hasattr(self.usage_point_config, "refresh_addresse") and self.usage_point_config.refresh_addresse:
                logging.info(" =>  Mise à jour du cache")
                result = self.run()
                self.usage_point_config.refresh_addresse = False
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
                    if key != "usage_point_addresses":
                        logging.info(f"{key}: {value}")
            else:
                logging.error(result)
            return result
