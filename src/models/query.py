import logging

import requests

from dependencies import str2bool
from init import CONFIG


class Query(object):
    def __init__(self, endpoint, headers=None):
        self.endpoint = endpoint
        self.timeout = 60
        check_ssl = CONFIG.get("ssl")
        if check_ssl and "gateway" in check_ssl:
            self.ssl_valid = str2bool(check_ssl["gateway"])
        else:
            self.ssl_valid = True
        if not headers:
            self.headers = {"Content-Type": "application/x-www-form-urlencoded"}
        else:
            self.headers = headers

    def get(self, params=None):
        logging.debug(f"[GET] Endpoint {self.endpoint}")
        logging.debug(f" - url : {self.endpoint}")
        logging.debug(f" - headers : {self.headers}")
        logging.debug(f" - params : {params}")
        response = {}
        try:
            response = requests.request(
                "GET",
                headers=self.headers,
                params=params,
                url=self.endpoint,
                timeout=self.timeout,
                verify=self.ssl_valid,
            )
            logging.debug(f"[RESPONSE] : status_code {response.status_code}")
            logging.debug(f" => {response.text}...")
        except Exception as e:
            logging.error(e)
        return response

    def post(self, params=None, data=None):
        logging.debug(f"[POST] Endpoint {self.endpoint}")
        logging.debug(f" - url : {self.endpoint}")
        logging.debug(f" - headers : {self.headers}")
        logging.debug(f" - params : {params}")
        logging.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request(
                "POST",
                headers=self.headers,
                params=params,
                data=data,
                url=self.endpoint,
                timeout=self.timeout,
                verify=self.ssl_valid,
            )
            logging.debug(f"[RESPONSE] : status_code {response.status_code}")
            logging.debug(f" => {response.text}...")
        except Exception as e:
            logging.error(response)
        return response

    def delete(self, params=None, data=None):
        logging.debug(f"[DELETE] Endpoint {self.endpoint}")
        logging.debug(f" - headers : {self.headers}")
        logging.debug(f" - params : {params}")
        logging.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request(
                "DELETE",
                headers=self.headers,
                params=params,
                data=data,
                url=self.endpoint,
                timeout=self.timeout,
                verify=self.ssl_valid,
            )
            logging.debug(f"[RESPONSE] : status_code {response.status_code}")
            logging.debug(f" => {response.text}...")
            return response
        except Exception as e:
            logging.error(response)
        return response

    def update(self, params=None, data=None):
        logging.debug(f"[UPDATE] Endpoint {self.endpoint}")
        logging.debug(f" - headers : {self.headers}")
        logging.debug(f" - params : {params}")
        logging.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request(
                "UPDATE",
                headers=self.headers,
                params=params,
                data=data,
                url=self.endpoint,
                timeout=self.timeout,
                verify=self.ssl_valid,
            )
            logging.debug(f"[RESPONSE] : status_code {response.status_code}")
            logging.debug(f" => {response.text}...")
            return response
        except Exception as e:
            logging.error(response)
        return response

    def put(self, params=None, data=None):
        logging.debug(f"[PUT] Endpoint {self.endpoint}")
        logging.debug(f" - headers : {self.headers}")
        logging.debug(f" - params : {params}")
        logging.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request(
                "PUT",
                headers=self.headers,
                params=params,
                data=data,
                url=self.endpoint,
                timeout=self.timeout,
                verify=self.ssl_valid,
            )
            logging.debug(f"[RESPONSE] : status_code {response.status_code}")
            logging.debug(f" => {response.text}...")
        except Exception as e:
            logging.error(response)
        return response
