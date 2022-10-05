import json

from models.query import Query
from models.log import log, debug, critical
from config import URL
from dependencies import CACHE


class Address:

    def __init__(self, headers, usage_point_id, config):
        self.cache = CACHE
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config

    def run(self):

        name = "addresses"
        endpoint = f"{name}/{self.usage_point_id}"
        if "cache" in self.config and self.config["cache"]:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"

        response = Query(endpoint=target, headers=self.headers).get()
        if response.status_code == 200:
            try:
                response_json = json.loads(response.text)
                addresse = response_json["customer"]["usage_points"][0]
                self.cache.insert_addresse(
                    usage_point_id=self.usage_point_id,
                    addresse=json.dumps(addresse),
                )
            except LookupError:
                addresse = {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }
            return addresse
        else:
            return {
                "error": True,
                "description": "Erreur lors de la récupération du contrat."
            }

    def get(self):
        current_cache = self.cache.get_addresse(usage_point_id=self.usage_point_id)
        if current_cache is None:
            # No cache
            log(f" => No cache")
            return self.run()
        else:
            # Refresh cache
            if "refresh_addresse" in self.config and self.config["refresh_addresse"]:
                log(f" => Refresh Cache")
                return self.run()
            else:
                # Get data in cache
                log(f" => Query Cache")
                addresse = json.loads(current_cache[1])
                self.cache.insert_addresse(
                    usage_point_id=self.usage_point_id,
                    addresse=addresse,
                )
                return addresse