import requests
import os
import json
from datetime import datetime

from .log import *


class Query(object):

    def __init__(self, endpoint, headers=None):
        self.endpoint = endpoint
        if not headers:
            self.headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }

    def get(self, headers=None, params=None):
        if headers is None:
            headers = self.headers
        response = {}
        debug(f"[GET] Endpoint {self.endpoint}")
        debug(f" - url : {self.endpoint}")
        debug(f" - headers : {headers}")
        debug(f" - params : {params}")
        try:
            response = requests.request('GET', headers=headers, params=params, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
            return response
        except Exception as e:
            error(e)
            print(str(e))

    def post(self, headers=None, params=None, data=None):
        if headers is None:
            headers = self.headers
        response = {}
        debug(f"[POST] Endpoint {self.endpoint}")
        debug(f" - url : {self.endpoint}")
        debug(f" - headers : {headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        try:
            response = requests.request('POST', headers=headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def delete(self, headers=None, params=None, data=None):
        if headers is None:
            headers = self.headers
        response = {}
        debug(f"[DELETE] Endpoint {self.endpoint}")
        debug(f" - headers : {headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        try:
            response = requests.request('DELETE', headers=headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def update(self, headers=None, params=None, data=None):
        if headers is None:
            headers = self.headers
        response = {}
        debug(f"[UPDATE] Endpoint {self.endpoint}")
        debug(f" - headers : {headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        try:
            response = requests.request('UPDATE', headers=headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def put(self, path, headers=None, params=None, data=None):
        if headers is None:
            headers = self.headers
        response = {}
        debug(f"[PUT] Endpoint {self.endpoint}")
        debug(f" - headers : {headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        try:
            response = requests.request('PUT', headers=headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response