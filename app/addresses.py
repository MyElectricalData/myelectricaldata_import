import requests
import json
from dateutil.relativedelta import *

from importlib import import_module
main = import_module("main")
f = import_module("function")

def getAddresses(client):
    pdl = main.pdl
    url = main.url
    headers = main.headers

    data = {
        "type": "addresses",
        "usage_point_id": str(pdl),
    }
    addresses = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()
    customer = addresses["customer"]
    f.publish(client, f"{pdl}/details/customer_id", str(customer["customer_id"]))
    for usage_points in customer['usage_points']:
        for usage_point_key, usage_point_data in usage_points['usage_point'].items():
            if isinstance(usage_point_data, dict):
                for usage_point_data_key, usage_point_data_data in usage_point_data.items():
                    f.publish(client, f"{pdl}/details/usage_points/usage_point/{usage_point_key}/{usage_point_data_key}",
                            str(usage_point_data_data))
            else:
                f.publish(client, f"{pdl}/details/usage_points/usage_point/{usage_point_key}", str(usage_point_data))
