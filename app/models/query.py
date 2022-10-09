import requests
import os
import json
from datetime import datetime

from dependencies import *


class Query(object):

    def __init__(self, endpoint, headers=None):
        self.endpoint = endpoint
        if not headers:
            self.headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        else:
            self.headers = headers

    def get(self, params=None):
        logDebug(f"[GET] Endpoint {self.endpoint}")
        logDebug(f" - url : {self.endpoint}")
        logDebug(f" - headers : {self.headers}")
        logDebug(f" - params : {params}")
        response = {}
        try:
            response = requests.request('GET', headers=self.headers, params=params, url=self.endpoint)
            logDebug(f"[RESPONSE] : status_code {response.status_code}")
            logDebug(f" => {response.text}")
        except Exception as e:
            logging.error(e)
            print(str(e))
        return response

    def post(self, params=None, data=None):
        logDebug(f"[POST] Endpoint {self.endpoint}")
        logDebug(f" - url : {self.endpoint}")
        logDebug(f" - headers : {self.headers}")
        logDebug(f" - params : {params}")
        logDebug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('POST', headers=self.headers, params=params, data=data, url=self.endpoint)
            logDebug(f"[RESPONSE] : status_code {response.status_code}")
            logDebug(f" => {response.text}")
        except Exception as e:
            logging.error(response)
            print(str(e))
        return response

    def delete(self, params=None, data=None):
        logDebug(f"[DELETE] Endpoint {self.endpoint}")
        logDebug(f" - headers : {self.headers}")
        logDebug(f" - params : {params}")
        logDebug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('DELETE', headers=self.headers, params=params, data=data, url=self.endpoint)
            logDebug(f"[RESPONSE] : status_code {response.status_code}")
            logDebug(f" => {response.text}")
            return response
        except Exception as e:
            logging.error(response)
            print(str(e))
        return response

    def update(self, params=None, data=None):
        logDebug(f"[UPDATE] Endpoint {self.endpoint}")
        logDebug(f" - headers : {self.headers}")
        logDebug(f" - params : {params}")
        logDebug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('UPDATE', headers=self.headers, params=params, data=data, url=self.endpoint)
            logDebug(f"[RESPONSE] : status_code {response.status_code}")
            logDebug(f" => {response.text}")
            return response
        except Exception as e:
            logging.error(response)
            print(str(e))
        return response

    def put(self, path, params=None, data=None):
        logDebug(f"[PUT] Endpoint {self.endpoint}")
        logDebug(f" - headers : {self.headers}")
        logDebug(f" - params : {params}")
        logDebug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('PUT', headers=self.headers, params=params, data=data, url=self.endpoint)
            logDebug(f"[RESPONSE] : status_code {response.status_code}")
            logDebug(f" => {response.text}")
        except Exception as e:
            logging.error(response)
            print(str(e))
        return response