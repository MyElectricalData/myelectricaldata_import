import json
from importlib import import_module

main = import_module("main")
f = import_module("function")

def getAddresses(headers, client, con, cur, pdl, pdl_config):

    def queryApi(url, headers, data, count=0):
        addresses = f.apiRequest(cur, con, pdl, type="POST", url=f"{url}", headers=headers, data=json.dumps(data))
        if not "error_code" in addresses:
            query = f"INSERT OR REPLACE INTO addresses VALUES (?,?,?)"
            cur.execute(query, [pdl, json.dumps(addresses), count])
            con.commit()
        return addresses

    url = main.url

    data = {
        "type": "addresses",
        "usage_point_id": str(pdl),
    }

    ha_discovery = {
        pdl: {}
    }

    query = f"SELECT * FROM addresses WHERE pdl = '{pdl}'"
    cur.execute(query)
    query_result = cur.fetchone()
    if query_result is None:
        f.log(" => Query API")
        addresses = queryApi(url, headers, data)
    else:
        if pdl_config['refresh_addresses'] == True:
            f.log(" => Query API (Refresh Cache)")
            addresses = queryApi(url, headers, data, 0)
        else:
            f.log(f" => Query Cache")
            addresses = json.loads(query_result[1])
            query = f"INSERT OR REPLACE INTO addresses VALUES (?,?,?)"
            cur.execute(query, [pdl, json.dumps(addresses), 0])
            con.commit()


    if 'error_code' in addresses:
        f.log(addresses['description'])
        ha_discovery = {
            "error_code": True,
            "detail": {
                "message": addresses['description']
            }
        }
        f.publish(client, f"{pdl}/addresses/error", str(1))
        for key, value in addresses.items():
            f.publish(client, f"{pdl}/addresses/errorMsg/{key}", str(value))
    else:
        if "customer" in addresses:
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
        else:
            ha_discovery = {
                "error_code": True,
                "detail": {
                    "message": addresses
                }
            }

    return ha_discovery
