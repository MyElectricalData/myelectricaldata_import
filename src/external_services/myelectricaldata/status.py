"""Class representing the status of MyElectricalData."""

import datetime
import inspect
import json
import logging
import traceback

from config.main import APP_CONFIG
from const import CODE_200_SUCCESS, URL
from database.usage_points import DatabaseUsagePoints
from models.query import Query
from utils import get_version


class Status:
    """Class representing the status of MyElectricalData."""

    def __init__(self, headers=None):
        self.url = URL
        self.headers = headers

    def ping(self):
        """Ping the MyElectricalData endpoint to check its availability."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            target = f"{self.url}/ping"
            status = {
                "version": get_version(),
                "status": False,
                "information": "MyElectricalData injoignable.",
            }
            try:
                response = Query(endpoint=target, headers=self.headers).get()
                if hasattr(response, "status_code") and response.status_code == CODE_200_SUCCESS:
                    status = json.loads(response.text)
                    for key, value in status.items():
                        logging.debug(f"{key}: {value}")
                    status["version"] = get_version()
                return status
            except LookupError:
                return status

    def status(self, usage_point_id):
        """Retrieve the status of a usage point.

        Args:
            usage_point_id (str): The ID of the usage point.

        Returns:
            dict: The status of the usage point.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            usage_point_id_config = DatabaseUsagePoints(usage_point_id).get()
            target = f"{self.url}/valid_access/{usage_point_id}"
            if hasattr(usage_point_id_config, "cache") and usage_point_id_config.cache:
                target += "/cache"
            response = Query(endpoint=target, headers=self.headers).get()
            if response:
                status = json.loads(response.text)
                if response.status_code == CODE_200_SUCCESS:
                    try:
                        for key, value in status.items():
                            logging.info(f"{key}: {value}")
                        DatabaseUsagePoints(usage_point_id).update(
                            consentement_expiration=datetime.datetime.strptime(
                                status["consent_expiration_date"], "%Y-%m-%dT%H:%M:%S"
                            ).replace(tzinfo=datetime.timezone.utc),
                            call_number=status["call_number"],
                            quota_limit=status["quota_limit"],
                            quota_reached=status["quota_reached"],
                            quota_reset_at=datetime.datetime.strptime(
                                status["quota_reset_at"], "%Y-%m-%dT%H:%M:%S.%f"
                            ).replace(tzinfo=datetime.timezone.utc),
                            ban=status["ban"],
                        )
                        return status
                    except Exception as e:
                        if APP_CONFIG.debug:
                            traceback.print_exc()
                        logging.error(e)
                        return {
                            "error": True,
                            "description": "Erreur lors de la récupération du statut du compte.",
                        }
                else:
                    if APP_CONFIG.debug:
                        traceback.print_exc()
                    logging.error(status["detail"])
                    return {"error": True, "description": status["detail"]}
            else:
                if APP_CONFIG.debug:
                    traceback.print_exc()
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "description": json.loads(response.text),
                }
