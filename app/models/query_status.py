import json

from models.query import Query
from models.log import log, debug, critical
from config import URL
from dependencies import CACHE

class Status:

    def __init__(self, headers):
        self.cache = CACHE
        self.url = URL

        self.endpoint = "ping"

        self.headers = headers

    def get(self):

        target = f"{self.url}/ping"
        response = Query(endpoint=target, headers=self.headers).get()
        if response.status_code == 200:
            try:
                return json.loads(response.text)
            except LookupError:
                return {
                    "error": True,
                    "description": "Erreur lors de la récupération du contrat."
                }
        else:
            return {
                "error": True,
                "description": "Erreur lors de la récupération du contrat."
            }