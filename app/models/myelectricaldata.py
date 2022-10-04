import json
import sys

from models.config import get_version
from models.query import Query
from models.log import log, debug, critical


class MyElectricalData:

    def __init__(self, cache, url, usage_point_id, config):
        self.cache = cache
        self.url = url
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': config['token'],
            'call-service': "myelectricaldata",
            'version': get_version()
        }

        self.usage_point_id = usage_point_id
        self.config = config

    def contract(self):

        def do():
            response = Query(endpoint=target, headers=self.headers).get(headers=self.headers)
            if response.status_code == 200:
                self.cache.insert_contract(
                    usage_point_id=self.usage_point_id,
                    contract=response.text,
                )
                return response.text
            else:
                return {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }

        name = "contracts"
        endpoint = f"{name}/{self.usage_point_id}"
        if "cache" in self.config and self.config["cache"]:
            endpoint += "/cache"
        target = f"{self.url}/{endpoint}"
        current_cache = self.cache.get_contract(usage_point_id=self.usage_point_id)
        if current_cache is None:
            # No cache
            log(f" => No cache : {target}")
            return do()
        else:
            # Refresh cache
            if "refresh_contract" in self.config and self.config["refresh_contract"]:
                log(f" => Refresh Cache : {target}")
                return do()
            else:
                # Get data in cache
                log(f" => Query Cache")
                contract = json.loads(current_cache[1])
                self.cache.insert_contract(
                    usage_point_id=self.usage_point_id,
                    contract=contract,
                )
                return contract

