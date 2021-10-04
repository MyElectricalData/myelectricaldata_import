import requests
import json
from dateutil.relativedelta import *

from importlib import import_module
main = import_module("main")
f = import_module("function")

def getContract(client):
    pdl = main.pdl
    headers = main.headers
    url = main.url

    ha_discovery = {
        pdl: {}
    }

    data = {
        "type": "contracts",
        "usage_point_id": str(pdl),
    }
    contract = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()
    if "customer" in contract:
        customer = contract["customer"]
        f.publish(client, f"{pdl}/customer_id", str(customer["customer_id"]))
        for usage_points in customer['usage_points']:
            for usage_point_key, usage_point_data in usage_points['usage_point'].items():
                f.publish(client, f"{pdl}/contract/{usage_point_key}", str(usage_point_data))
            for contracts_key, contracts_data in usage_points['contracts'].items():
                f.publish(client, f"{pdl}/contract/{contracts_key}", str(contracts_data))
                if contracts_key == "last_distribution_tariff_change_date":
                    f.publish(client, f"{pdl}/last_distribution_tariff_change_date", str(contracts_data))
                    ha_discovery[pdl]["last_distribution_tariff_change_date"] = str(contracts_data)
                if contracts_key == "last_activation_date":
                    f.publish(client, f"{pdl}/last_activation_date", str(contracts_data))
                    ha_discovery[pdl]["last_activation_date"] = str(contracts_data)
                if contracts_key == "subscribed_power":
                    f.publish(client, f"{pdl}/subscribed_power", str(contracts_data.split()[0]))
                    ha_discovery[pdl]["subscribed_power"] = str(contracts_data.split()[0])
                if contracts_key == "offpeak_hours":
                    offpeak_hours = contracts_data[contracts_data.find("(") + 1:contracts_data.find(")")].split(';')
                    ha_discovery[pdl]["offpeak_hours"] = str(contracts_data)
                    index = 0
                    for oh in offpeak_hours:
                        f.publish(client, f"{pdl}/offpeak_hours/{index}/start", str(oh.split('-')[0]))
                        f.publish(client, f"{pdl}/offpeak_hours/{index}/stop", str(oh.split('-')[1]))
                        index = index + 1
                    f.publish(client, f"{pdl}/offpeak_hours", str(contracts_data))
    else:
        ha_discovery = {
            "error": True,
            "errorMsg": contract
        }
    return ha_discovery
