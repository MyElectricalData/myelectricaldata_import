import json
import logging
import traceback

from config import URL
from dependencies import title
from init import CONFIG, DB
from models.query import Query


class Address:
    def __init__(self, headers, usage_point_id):
        self.config = CONFIG
        self.db = DB
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = self.config.usage_point_id_config(self.usage_point_id)

    def run(self):
        name = "addresses"
        endpoint = f"{name}/{self.usage_point_id}"
        if hasattr(self.usage_point_config, "cache") and self.usage_point_config.cache:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"

        response = Query(endpoint=target, headers=self.headers).get()
        if response.status_code == 200:
            try:
                response_json = json.loads(response.text)
                response = response_json["customer"]["usage_points"][0]
                usage_point = response["usage_point"]
                usage_point_addresses = usage_point["usage_point_addresses"]
                response = usage_point_addresses
                response.update(usage_point)
                self.db.set_addresse(
                    self.usage_point_id,
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
                    },
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
        current_cache = self.db.get_addresse(usage_point_id=self.usage_point_id)
        if not current_cache:
            # No cache
            logging.info(" =>  Pas de cache")
            result = self.run()
        else:
            # Refresh cache
            if hasattr(self.usage_point_config, "refresh_addresse") and self.usage_point_config.refresh_addresse:
                logging.info(" =>  Mise à jour du cache")
                result = self.run()
                self.usage_point_config.refresh_addresse = False
                DB.set_usage_point(self.usage_point_id, self.usage_point_config.__dict__)
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
