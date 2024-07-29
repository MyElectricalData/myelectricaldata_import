"""Manage local cache."""

import inspect
import json
import logging

from config.main import APP_CONFIG
from const import CODE_200_SUCCESS, URL
from models.query import Query
from utils import get_version


class Cache:
    """Manage local cache."""

    def __init__(self, usage_point_id, headers=None):
        self.url = URL
        self.headers = headers
        self.usage_point_id = usage_point_id

    def reset(self):
        """Reset local cache."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            target = f"{self.url}/cache/{self.usage_point_id}"
            response = Query(endpoint=target, headers=self.headers).delete()
            if response.status_code == CODE_200_SUCCESS:
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
