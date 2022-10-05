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
        else:
            self.headers = headers

    def get(self, params=None):
        debug(f"[GET] Endpoint {self.endpoint}")
        debug(f" - url : {self.endpoint}")
        debug(f" - headers : {self.headers}")
        debug(f" - params : {params}")
        response = {}
        try:
            response = requests.request('GET', headers=self.headers, params=params, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(e)
            print(str(e))
        return response

    def post(self, params=None, data=None):
        debug(f"[POST] Endpoint {self.endpoint}")
        debug(f" - url : {self.endpoint}")
        debug(f" - headers : {self.headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('POST', headers=self.headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def delete(self, params=None, data=None):
        debug(f"[DELETE] Endpoint {self.endpoint}")
        debug(f" - headers : {self.headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('DELETE', headers=self.headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
            return response
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def update(self, params=None, data=None):
        debug(f"[UPDATE] Endpoint {self.endpoint}")
        debug(f" - headers : {self.headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('UPDATE', headers=self.headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
            return response
        except Exception as e:
            error(response)
            print(str(e))
        return response

    def put(self, path, params=None, data=None):
        debug(f"[PUT] Endpoint {self.endpoint}")
        debug(f" - headers : {self.headers}")
        debug(f" - params : {params}")
        debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('PUT', headers=self.headers, params=params, data=data, url=self.endpoint)
            debug(f"[RESPONSE] : status_code {response.status_code}")
            debug(f" => {response.text}")
        except Exception as e:
            error(response)
            print(str(e))
        return response