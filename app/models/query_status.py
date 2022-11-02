import json

import __main__ as app
from config import URL
from dependencies import *
from models.log import Log
from models.query import Query


class Status:

    def __init__(self, headers=None):
        self.log = Log()
        self.url = URL
        self.headers = headers

    def ping(self):

        target = f"{self.url}/ping"
        response = Query(endpoint=target, headers=self.headers).get()
        if response.status_code == 200:
            try:
                status = json.loads(response.text)
                for key, value in status.items():
                    self.log.log(f"{key}: {value}")
                return status
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

    def status(self, usage_point_id):

        target = f"{self.url}/valid_access/{usage_point_id}"
        response = Query(endpoint=target, headers=self.headers).get()
        if response.status_code == 200:
            try:
                status = json.loads(response.text)
                for key, value in status.items():
                    app.LOG.log(f"{key}: {value}")
                return status
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
