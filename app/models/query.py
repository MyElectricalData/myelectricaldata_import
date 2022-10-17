import requests
import __main__ as app

from dependencies import *


class Query(object):

    def __init__(self, endpoint, headers=None):
        self.endpoint = endpoint
        self.timeout = 60
        if not headers:
            self.headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        else:
            self.headers = headers

    def get(self, params=None):
        app.LOG.debug(f"[GET] Endpoint {self.endpoint}")
        app.LOG.debug(f" - url : {self.endpoint}")
        app.LOG.debug(f" - headers : {self.headers}")
        app.LOG.debug(f" - params : {params}")
        response = {}
        try:
            response = requests.request('GET', headers=self.headers, params=params, url=self.endpoint,
                                        timeout=self.timeout)
            app.LOG.debug(f"[RESPONSE] : status_code {response.status_code}")
            app.LOG.debug(f" => {response.text}...")
        except Exception as e:
            app.LOG.error(e)
        return response

    def post(self, params=None, data=None):
        app.LOG.debug(f"[POST] Endpoint {self.endpoint}")
        app.LOG.debug(f" - url : {self.endpoint}")
        app.LOG.debug(f" - headers : {self.headers}")
        app.LOG.debug(f" - params : {params}")
        app.LOG.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('POST', headers=self.headers, params=params, data=data, url=self.endpoint,
                                        timeout=self.timeout)
            app.LOG.debug(f"[RESPONSE] : status_code {response.status_code}")
            app.LOG.debug(f" => {response.text}...")
        except Exception as e:
            app.LOG.error(response)
        return response

    def delete(self, params=None, data=None):
        app.LOG.debug(f"[DELETE] Endpoint {self.endpoint}")
        app.LOG.debug(f" - headers : {self.headers}")
        app.LOG.debug(f" - params : {params}")
        app.LOG.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('DELETE', headers=self.headers, params=params, data=data, url=self.endpoint,
                                        timeout=self.timeout)
            app.LOG.debug(f"[RESPONSE] : status_code {response.status_code}")
            app.LOG.debug(f" => {response.text}...")
            return response
        except Exception as e:
            app.LOG.error(response)
        return response

    def update(self, params=None, data=None):
        app.LOG.debug(f"[UPDATE] Endpoint {self.endpoint}")
        app.LOG.debug(f" - headers : {self.headers}")
        app.LOG.debug(f" - params : {params}")
        app.LOG.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('UPDATE', headers=self.headers, params=params, data=data, url=self.endpoint,
                                        timeout=self.timeout)
            app.LOG.debug(f"[RESPONSE] : status_code {response.status_code}")
            app.LOG.debug(f" => {response.text}...")
            return response
        except Exception as e:
            app.LOG.error(response)
        return response

    def put(self, params=None, data=None):
        app.LOG.debug(f"[PUT] Endpoint {self.endpoint}")
        app.LOG.debug(f" - headers : {self.headers}")
        app.LOG.debug(f" - params : {params}")
        app.LOG.debug(f" - data : {data}")
        response = {}
        try:
            response = requests.request('PUT', headers=self.headers, params=params, data=data, url=self.endpoint,
                                        timeout=self.timeout)
            app.LOG.debug(f"[RESPONSE] : status_code {response.status_code}")
            app.LOG.debug(f" => {response.text}...")
        except Exception as e:
            app.LOG.error(response)
        return response
