import requests
import json
from dateutil.relativedelta import *
import base64
from pprint import pprint

from importlib import import_module
main = import_module("main")
f = import_module("function")

def getAddresses(client, cur):
    pdl = main.pdl
    url = main.url
    headers = main.headers

    data = {
        "type": "addresses",
        "usage_point_id": str(pdl),
    }

    query = f"SELECT * FROM addresses WHERE pdl = '{pdl}'"
    cur.execute(query)
    query_result = cur.fetchone()
    if query_result is None:
        addresses = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()
        addresses_b64 = str(addresses)
        addresses_b64 = addresses_b64.encode('ascii')
        addresses_b64 = base64.b64encode(addresses_b64)
        cur.execute(f"INSERT OR REPLACE INTO addresses VALUES ('{pdl}','{addresses_b64}')")
    else:
        addresses = json.loads(query_result[1])

    pprint(addresses)
    quit()

    if not "customer" in addresses:
        f.publish(client, f"{pdl}/consumption/current_year/error", str(1))
        for key, value in addresses.items():
            f.publish(client, f"{pdl}/consumption/current_year/errorMsg/{key}", str(value))
    else:
        customer = addresses["customer"]
        f.publish(client, f"{pdl}/customer_id", str(customer["customer_id"]))
        for usage_points in customer['usage_points']:
            for usage_point_key, usage_point_data in usage_points['usage_point'].items():
                if isinstance(usage_point_data, dict):
                    for usage_point_data_key, usage_point_data_data in usage_point_data.items():
                        f.publish(client, f"{pdl}/addresses/{usage_point_key}/{usage_point_data_key}",
                                str(usage_point_data_data))
                else:
                    f.publish(client, f"{pdl}/addresses/{usage_point_key}", str(usage_point_data))
