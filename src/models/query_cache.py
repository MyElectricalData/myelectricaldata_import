import json
import logging

from config import URL
from dependencies import get_version
from models.query import Query


class Cache:
    def __init__(self, usage_point_id, headers=None):
        self.url = URL
        self.headers = headers
        self.usage_point_id = usage_point_id

    def reset(self):
        target = f"{self.url}/cache/{self.usage_point_id}"
        response = Query(endpoint=target, headers=self.headers).delete()
        if response.status_code == 200:
            try:
                status = json.loads(response.text)
                for key, value in status.items():
                    logging.info(f"{key}: {value}")
                status["version"] = get_version()
                return status
            except LookupError:
                return {"error": True, "description": "Erreur lors du reset du cache."}
        else:
            return {"error": True, "description": "Erreur lors du reset du cache."}
