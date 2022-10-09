import json

import __main__
from config import URL
from dependencies import *
from models.query import Query


class Contract:

    def __init__(self, headers, usage_point_id, config):
        self.cache = __main__.CACHE
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config

    def run(self):

        name = "contracts"
        endpoint = f"{name}/{self.usage_point_id}"
        if "cache" in self.config and self.config["cache"]:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"

        query_response = Query(endpoint=target, headers=self.headers).get()
        if query_response.status_code == 200:
            try:
                response_json = json.loads(query_response.text)
                reponse = response_json["customer"]["usage_points"][0]
                self.cache.insert_contract(
                    usage_point_id=self.usage_point_id,
                    contract=json.dumps(reponse),
                )
            except LookupError:
                reponse = {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }
            return reponse
        else:
            return {
                "error": True,
                "description": "Erreur lors de la récupération du contrat."
            }

    def get(self):
        current_cache = self.cache.get_contract(usage_point_id=self.usage_point_id)
        if current_cache is None:
            # No cache
            log(f" => No cache")
            result = self.run()
        else:
            # Refresh cache
            if "refresh_contract" in self.config and self.config["refresh_contract"]:
                log(f" => Refresh Cache")
                result = self.run()
            else:
                # Get data in cache
                log(f" => Query Cache")
                value = current_cache[1]
                logDebug(f" => {value}")
                result = json.loads(value)
        if "error" not in result:
            for key, value in result["contracts"].items():
                log(f"{key}: {value}")
        return result
