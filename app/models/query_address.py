import json

import __main__ as app
from config import URL
from dependencies import *
from models.query import Query


class Address:

    def __init__(self, headers, usage_point_id, config):
        self.db = app.DB
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.usage_point_config = config

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
                self.db.set_addresse(self.usage_point_id, {
                    "usage_points": str(usage_point["usage_point_id"]) if usage_point["usage_point_id"] is not None else "",
                    "street": str(usage_point_addresses["street"]) if usage_point_addresses["street"] is not None else "",
                    "locality": str(usage_point_addresses["locality"]) if usage_point_addresses["locality"] is not None else "",
                    "postal_code": str(usage_point_addresses["postal_code"]) if usage_point_addresses["postal_code"] is not None else "",
                    "insee_code": str(usage_point_addresses["insee_code"]) if usage_point_addresses["insee_code"] is not None else "",
                    "city": str(usage_point_addresses["city"]) if usage_point_addresses["city"] is not None else "",
                    "country": str(usage_point_addresses["country"]) if usage_point_addresses["country"] is not None else "",
                    "geo_points": str(usage_point_addresses["geo_points"]) if usage_point_addresses["geo_points"] is not None else "",
                })
            except LookupError:
                response = {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }
            return response
        else:
            return {
                "error": True,
                "description": json.loads(response.text)["detail"]
            }

    def get(self):
        current_cache = self.db.get_addresse(usage_point_id=self.usage_point_id)
        if not current_cache:
            # No cache
            app.LOG.log(f" => No cache")
            result = self.run()
        else:
            # Refresh cache
            if hasattr(self.usage_point_config, "refresh_addresse") and self.usage_point_config.refresh_addresse:
                app.LOG.log(f" => Refresh Cache")
                result = self.run()
                self.usage_point_config.refresh_addresse = False
                app.DB.set_usage_point(self.usage_point_id, self.usage_point_config.__dict__)
            else:
                # Get data in cache
                app.LOG.log(f" => Query Cache")
                result = {}
                for column in current_cache.__table__.columns:
                    result[column.name] = str(getattr(current_cache, column.name))
                app.LOG.debug(f" => {result}")
        if "error" not in result:
            for key, value in result.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        app.LOG.log(f"  {k}: {v}")
                else:
                    app.LOG.log(f"{key}: {value}")

        return result
