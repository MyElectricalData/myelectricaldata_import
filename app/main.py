import os
import time
from dateutil.relativedelta import *
from datetime import datetime
from distutils.util import strtobool
import sqlite3
import locale
from pprint import pprint
import yaml
import json
import influxdb_client
from influxdb_client.client.write_api import ASYNCHRONOUS
from collections import namedtuple

from importlib import import_module

f = import_module("function")
addr = import_module("addresses")
cont = import_module("contract")
day = import_module("daily")
detail = import_module("detail")
ha = import_module("home_assistant")
myenedis = import_module("myenedis")
influx = import_module("influxdb")

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

url = "https://enedisgateway.tech/api"

fail_count = 24

fichier = open("/app/VERSION", "r")
VERSION = fichier.read()
fichier.close()

with open(r'/data/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

api_no_result = []


def init_database(cur):
    ## CONFIG
    cur.execute('''CREATE TABLE config (
                        key TEXT PRIMARY KEY,
                        value json NOT NULL)''')
    cur.execute('''CREATE UNIQUE INDEX idx_config_key
                    ON config (key)''')

    ## ADDRESSES
    cur.execute('''CREATE TABLE addresses (
                        pdl TEXT PRIMARY KEY,
                        json json NOT NULL, 
                        count INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_pdl_addresses
                    ON addresses (pdl)''')

    ## CONTRACT
    cur.execute('''CREATE TABLE contracts (
                        pdl TEXT PRIMARY KEY,
                        json json NOT NULL, 
                        count INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_pdl_contracts
                    ON contracts (pdl)''')
    ## CONSUMPTION
    # DAILY
    cur.execute('''CREATE TABLE consumption_daily (
                        pdl TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL, 
                        fail INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_date_consumption
                    ON consumption_daily (date)''')

    # DETAIL
    cur.execute('''CREATE TABLE consumption_detail (
                        pdl TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL, 
                        interval INTEGER NOT NULL, 
                        measure_type TEXT NOT NULL, 
                        fail INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_date_consumption_detail
                    ON consumption_detail (date)''')
    ## PRODUCTION
    # DAILY
    cur.execute('''CREATE TABLE production_daily (
                        pdl TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL, 
                        fail INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_date_production 
                    ON production_daily (date)''')
    # DETAIL
    cur.execute('''CREATE TABLE production_detail (
                        pdl TEXT NOT NULL, 
                        date TEXT NOT NULL, 
                        value INTEGER NOT NULL, 
                        interval INTEGER NOT NULL,                        
                        fail INTEGER)''')
    cur.execute('''CREATE UNIQUE INDEX idx_date_production_detail
                    ON production_detail (date)''')

    ## Default Config
    config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
    config = {
        "day": datetime.now().strftime('%Y-%m-%d'),
        "call_number": 0,
        "max_call": 15
    }
    cur.execute(config_query, ["config", json.dumps(config)])


def run(pdl, pdl_config):
    f.logLine()
    f.title(pdl)

    global offpeak_hours

    headers = {
        'Content-Type': 'application/json',
        'Authorization': pdl_config['token'],
        'call-service': "enedisgateway2mqtt",
        'version': VERSION
    }

    f.logLine()
    f.log("Get contract :")
    contract = cont.getContract(headers, client, cur, con, pdl, pdl_config)
    f.log(contract, "debug")
    if "error_code" in contract:
        f.publish(client, f"error", str(1))
        for key, data in contract["detail"].items():
            f.publish(client, f"errorMsg/{key}", str(data))
        f.log("-- Stop import --")
    else:
        f.publish(client, f"error", str(0))

        for pdl, contract_data in contract.items():
            for key, data in contract_data.items():
                if key == "last_activation_date":
                    last_activation_date = data
                if key == "offpeak_hours":
                    offpeak_hours = data
                if "home_assistant" in config and "discovery" in config['home_assistant'] and config['home_assistant'][
                    'discovery'] == True:
                    ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=key, value=data)

        if pdl_config['addresses'] == True:
            f.logLine()
            f.log("Get Addresses :")
            addresse = addr.getAddresses(headers, client, con, cur, pdl, pdl_config)
            if "error_code" in addresse:
                f.publish(client, f"addresses/error", str(1))
                for key, data in addresse["detail"].items():
                    f.publish(client, f"addresses/errorMsg/{key}", str(data))
            else:
                f.publish(client, f"addresses/error", str(0))

        if pdl_config['consumption'] == True:
            f.logLine()
            f.log("Get Consumption :")
            ha_discovery_consumption = day.getDaily(headers, cur, con, client, pdl, pdl_config, "consumption",
                                                    last_activation_date)
            f.logLine1()
            f.log("                        SUCCESS : Consumption daily imported")
            f.logLine1()
            if config['home_assistant']['discovery'] == True:
                f.logLine()
                f.log("Home Assistant auto-discovery (Consumption) :")
                for pdl, data in ha_discovery_consumption.items():
                    for name, sensor_data in data.items():
                        if "attributes" in sensor_data:
                            attributes = sensor_data['attributes']
                        else:
                            attributes = None
                        if "unit_of_meas" in sensor_data:
                            unit_of_meas = sensor_data['unit_of_meas']
                        else:
                            unit_of_meas = None
                        if "device_class" in sensor_data:
                            device_class = sensor_data['device_class']
                        else:
                            device_class = None
                        if "state_class" in sensor_data:
                            state_class = sensor_data['state_class']
                        else:
                            state_class = None
                        if "value" in sensor_data:
                            ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name,
                                               value=sensor_data['value'],
                                               attributes=attributes, unit_of_meas=unit_of_meas,
                                               device_class=device_class, state_class=state_class)
            f.log(" => HA Sensor updated")
        # f.logLine()

        if pdl_config['consumption_detail'] == True:
            f.log("Get Consumption Detail:")
            ha_discovery_consumption = detail.getDetail(headers, cur, con, client, pdl, pdl_config, "consumption",
                                                        last_activation_date, offpeak_hours)
            f.logLine1()
            f.log("                   SUCCESS : Consumption detail imported")
            f.logLine1()
            if config['home_assistant']['discovery'] == True:
                f.logLine()
                f.log("Home Assistant auto-discovery (Consumption Detail) :")
                for pdl, data in ha_discovery_consumption.items():
                    for name, sensor_data in data.items():
                        if "attributes" in sensor_data:
                            attributes = sensor_data['attributes']
                        else:
                            attributes = None
                        if "unit_of_meas" in sensor_data:
                            unit_of_meas = sensor_data['unit_of_meas']
                        else:
                            unit_of_meas = None
                        if "device_class" in sensor_data:
                            device_class = sensor_data['device_class']
                        else:
                            device_class = None
                        if "state_class" in sensor_data:
                            state_class = sensor_data['state_class']
                        else:
                            state_class = None
                        if "value" in sensor_data:
                            ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name,
                                               value=sensor_data['value'],
                                               attributes=attributes, unit_of_meas=unit_of_meas,
                                               device_class=device_class, state_class=state_class)
                f.log(" => HA Sensor updated")
        # f.logLine()

        if pdl_config['production'] == True:
            f.logLine()
            f.log("Get production :")
            ha_discovery_production = day.getDaily(headers, cur, con, client, pdl, pdl_config, "production",
                                                   last_activation_date)
            f.logLine1()
            f.log("             SUCCESS : Production daily imported")
            f.logLine1()
            if config['home_assistant']['discovery'] == True:
                f.logLine()
                f.log("Home Assistant auto-discovery (Production) :")
                for pdl, data in ha_discovery_production.items():
                    for name, sensor_data in data.items():
                        if "attributes" in sensor_data:
                            attributes = sensor_data['attributes']
                        else:
                            attributes = None
                        if "unit_of_meas" in sensor_data:
                            unit_of_meas = sensor_data['unit_of_meas']
                        else:
                            unit_of_meas = None
                        if "device_class" in sensor_data:
                            device_class = sensor_data['device_class']
                        else:
                            device_class = None
                        if "state_class" in sensor_data:
                            state_class = sensor_data['state_class']
                        else:
                            state_class = None
                        ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name, value=sensor_data['value'],
                                           attributes=attributes, unit_of_meas=unit_of_meas,
                                           device_class=device_class, state_class=state_class)
                f.log(" => HA Sensor updated")

        if pdl_config['production_detail'] == True:
            f.logLine()
            f.log("Get production Detail:")
            ha_discovery_consumption = detail.getDetail(headers, cur, con, client, pdl, pdl_config, "production",
                                                        last_activation_date, offpeak_hours)
            f.logLine1()
            f.log("              SUCCESS : Production detail imported")
            f.logLine1()
            if config['home_assistant']['discovery'] == True:
                f.logLine()
                f.log("Home Assistant auto-discovery (Production Detail) :")
                for pdl, data in ha_discovery_consumption.items():
                    for name, sensor_data in data.items():
                        if "attributes" in sensor_data:
                            attributes = sensor_data['attributes']
                        else:
                            attributes = None
                        if "unit_of_meas" in sensor_data:
                            unit_of_meas = sensor_data['unit_of_meas']
                        else:
                            unit_of_meas = None
                        if "device_class" in sensor_data:
                            device_class = sensor_data['device_class']
                        else:
                            device_class = None
                        if "state_class" in sensor_data:
                            state_class = sensor_data['state_class']
                        else:
                            state_class = None
                        if "value" in sensor_data:
                            ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name,
                                               value=sensor_data['value'],
                                               attributes=attributes, unit_of_meas=unit_of_meas,
                                               device_class=device_class, state_class=state_class)
                f.log(" => HA Sensor updated")

        if "influxdb" in config and config["influxdb"] != {}:
            f.logLine()
            f.log("Push data in influxdb")
            influx.influxdb_insert(cur, con, pdl, pdl_config, influxdb_api)
            f.log(" => Data exported")

        if "home_assistant" in config and "card_myenedis" in config['home_assistant'] and config['home_assistant'][
            'card_myenedis'] == True:
            f.logLine()
            f.log("Generate Sensor for myEnedis card")
            my_enedis_data = myenedis.myEnedis(cur, con, client, pdl, pdl_config, last_activation_date, offpeak_hours)
            for pdl, data in my_enedis_data.items():
                for name, sensor_data in data.items():
                    if "attributes" in sensor_data:
                        attributes = sensor_data['attributes']
                    else:
                        attributes = None
                    if "unit_of_meas" in sensor_data:
                        unit_of_meas = sensor_data['unit_of_meas']
                    else:
                        unit_of_meas = None
                    if "device_class" in sensor_data:
                        device_class = sensor_data['device_class']
                    else:
                        device_class = None
                    if "state_class" in sensor_data:
                        state_class = sensor_data['state_class']
                    else:
                        state_class = None
                    if "value" in sensor_data:
                        ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name,
                                           value=sensor_data['value'],
                                           attributes=attributes, unit_of_meas=unit_of_meas,
                                           device_class=device_class, state_class=state_class)
            f.log(" => Sensor generated")

        query = f"SELECT * FROM consumption_daily WHERE pdl == '{pdl}' AND fail > {fail_count} ORDER BY date"
        rows = con.execute(query)
        if rows.fetchone() is not None:
            f.logLine()
            f.log(f"Consumption data not found on enedis (after {fail_count} retry) :")
            # pprint(rows.fetchall())
            # pprint(rows)
            for row in rows:
                f.log(f"{row[0]} => {row[1]}")
    con.commit()

    f.logLine()
    f.log("IMPORT FINISH")
    f.logLine()


if __name__ == '__main__':

    default = {
        "wipe_cache": False,
        "cycle": 3600,
        "debug": False,
        "*mqtt": {
            "*host": "X.X.X.X",
            "port": 1883,
            "username": "",
            "password": "",
            "prefix": "enedis_gateway",
            "client_id": "enedis_gateway",
            "retain": True,
            "qos": 0
        },
        "home_assistant": {
            "discovery": False,
            "discovery_prefix": "homeassistant",
            "card_myenedis": False
        },
        "*enedis_gateway": {
            "*pdl": {
                "*token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                "plan": "BASE",
                "consumption": True,
                "consumption_detail": True,
                "consumption_price_hc": 0,
                "consumption_price_hp": 0,
                "consumption_price_base": 0,
                "production": False,
                "production_detail": False,
                "offpeak_hours": 0,
                "addresses": True,
                "refresh_contract": False,
                "refresh_addresses": False
            }
        }
    }

    lost_params = []
    # CHECK GLOBAL CONFIGURATION
    for id, data in default.items():
        isDict = False
        if isinstance(default[id], dict):
            isDict = True
        name = id
        mandatory = False
        if id.startswith('*'):
            mandatory = True
            name = id[1:]
        if mandatory == True and not name in config:
            lost_params.append(name.upper())
        elif not isDict:
            if not name in config:
                config[name] = data

    # CHECK MQTT CONFIGURATION
    list = "*mqtt"
    for id, data in default[list].items():
        name = id
        mandatory = False
        if list.startswith('*'):
            list = list[1:]
        if id.startswith('*'):
            mandatory = True
            name = id[1:]
        if mandatory == True and not name in config[list]:
            lost_params.append(f"{list}.{name.upper()}")
        else:
            if not name in config[list]:
                config[list][name] = data

    # CHECK HOME ASSISTANT CONFIGURATION
    list = "home_assistant"
    for id, data in default[list].items():
        name = id
        mandatory = False
        if list.startswith('*'):
            list = list[1:]
        if id.startswith('*'):
            mandatory = True
            name = id[1:]
        if mandatory == True and not name in config[list]:
            lost_params.append(f"{list}.{name.upper()}")
        else:
            if not name in config[list]:
                config[list][name] = data

    # CHECK ENEDIS GATEWAY CONFIGURATION
    if not "enedis_gateway" in config:
        lost_params.append("enedis_gateway")
    else:
        if not isinstance(config["enedis_gateway"], dict):
            lost_params.append("enedis_gateway.PDL")
        else:
            for pdl, pdl_data in config["enedis_gateway"].items():
                if len(str(pdl)) != 14:
                    lost_params.append(f"PDL must be 14 characters ({pdl} => {len(str(pdl))})")
                if not isinstance(config["enedis_gateway"][pdl], dict):
                    lost_params.append(f"enedis_gateway.{pdl}.TOKEN")
                else:
                    for id, data in default['*enedis_gateway']['*pdl'].items():
                        name = id
                        mandatory = False
                        if id.startswith('*'):
                            mandatory = True
                            name = id[1:]
                        if mandatory == True and not name in config["enedis_gateway"][pdl]:
                            lost_params.append(f"enedis_gateway.{pdl}.{name.upper()}")
                        else:
                            if not name in config["enedis_gateway"][pdl]:
                                config["enedis_gateway"][pdl][name] = data

    if lost_params != []:
        f.log(f'Some mandatory parameters are missing :', "ERROR")
        for param in lost_params:
            f.log(f'- {param}', "ERROR")
        f.log("", "ERROR")
        f.log("You can get list of parameters here :", "ERROR")
        f.log(f" => https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file", "ERROR")
        f.log("-- Stop application --", "CRITICAL")

    pprint(config)

    quit()

    if not "debug" in config:
        config['debug'] = False

    if not "mqtt" in config:
        f.log("MQTT Configuration is mandatory", "CRITICAL")
    else:
        if not "host" in config['mqtt']:
            f.log("MQTT host is mandatory", "CRITICAL")
        else:
            if not "port" in config['mqtt']:
                config['mqtt'] = default['mqtt']['port']
            if not "username" in config['mqtt']:
                config['username'] = ''
            if not "port" in config['mqtt']:
                config['mqtt'] = 1883
            if not "port" in config['mqtt']:
                config['mqtt'] = 1883
            if not "port" in config['mqtt']:
                config['mqtt'] = 1883

    f.logLine()
    if "mqtt" in config:
        f.log("MQTT")
        for id, value in config['mqtt'].items():
            if id == "password":
                value = "** hidden **"
            f.log(f" - {id} : {value}")
    else:
        f.log("MQTT Configuration missing !", "CRITICAL")

    if "home_assistant" in config:
        f.logLine()
        f.log("Home Assistant")
        for id, value in config['home_assistant'].items():
            f.log(f" - {id} : {value}")

    if "influxdb" in config:
        f.logLine()
        f.log("InfluxDB")
        for id, value in config['influxdb'].items():
            if id == "token":
                value = "** hidden **"
            f.log(f" - {id} : {value}")

    if "enedis_gateway" in config:
        f.logLine()
        f.log("Enedis Gateway")
        for pdl, data in config['enedis_gateway'].items():
            f.log(f" - {pdl}")
            for id, value in data.items():
                if id == "token":
                    value = "** hidden **"
                f.log(f"     {id} : {value}")
    else:
        f.log("Enedis Gateway Configuration missing !", "CRITICAL")
    f.logLine()

    # SQLlite
    f.log("Check database/cache")

    if not os.path.exists('/data'):
        os.mkdir('/data')

    if "wipe_cache" in config and config["wipe_cache"] == True:
        if os.path.exists('/data/enedisgateway.db'):
            f.logLine()
            f.log(" => Reset Cache")
            os.remove("/data/enedisgateway.db")

    if not os.path.exists('/data/enedisgateway.db'):
        f.log(" => Init SQLite Database")
        con = sqlite3.connect('/data/enedisgateway.db', timeout=10)
        cur = con.cursor()
        init_database(cur)

    else:
        f.log(" => Connect to SQLite Database")
        con = sqlite3.connect('/data/enedisgateway.db', timeout=10)
        cur = con.cursor()

        # Check database structure
        try:

            config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
            cur.execute(config_query, ["lastUpdate", datetime.now()])
            con.commit()

            list_tables = ["config", "addresses", "contracts", "consumption_daily", "consumption_detail",
                           "production_daily", "production_detail"]

            query = f"SELECT name FROM sqlite_master WHERE type='table';"
            cur.execute(query)
            query_result = cur.fetchall()
            tables = []
            for table in query_result:
                tables.append(str(table).replace("('", "").replace("',)", ''))
            for tab in list_tables:
                if not tab in tables:
                    msg = f"Table {tab} is missing"
                    f.log(msg)
                    raise msg
            cur.execute("INSERT OR REPLACE INTO config VALUES (?,?)", [0, 0])
            cur.execute("INSERT OR REPLACE INTO addresses VALUES (?,?,?)", [0, 0, 0])
            cur.execute("INSERT OR REPLACE INTO contracts VALUES (?,?,?)", [0, 0, 0])
            cur.execute("INSERT OR REPLACE INTO consumption_daily VALUES (?,?,?,?)", [0, '1970-01-01', 0, 0])
            cur.execute("INSERT OR REPLACE INTO consumption_detail VALUES (?,?,?,?,?,?)",
                        [0, '1970-01-01', 0, 0, "", 0])
            cur.execute("INSERT OR REPLACE INTO production_daily VALUES (?,?,?,?)", [0, '1970-01-01', 0, 0])
            cur.execute("INSERT OR REPLACE INTO production_detail VALUES (?,?,?,?,?)", [0, '1970-01-01', 0, 0, 0])
            cur.execute("DELETE FROM config WHERE key = 0")
            cur.execute("DELETE FROM addresses WHERE pdl = 0")
            cur.execute("DELETE FROM contracts WHERE pdl = 0")
            cur.execute("DELETE FROM consumption_daily WHERE pdl = 0")
            cur.execute("DELETE FROM consumption_detail WHERE pdl = 0")
            cur.execute("DELETE FROM production_daily WHERE pdl = 0")
            cur.execute("DELETE FROM production_detail WHERE pdl = 0")
        except Exception as e:
            f.log("=====> ERROR : Exception <======")
            f.log(e)
            f.log('<!> Database structure is invalid <!>')
            f.log(" => Reset database")
            con.close()
            os.remove("/data/enedisgateway.db")
            f.log(" => Reconnect")
            con = sqlite3.connect('/data/enedisgateway.db', timeout=10)
            cur = con.cursor()
            init_database(cur)

    # MQTT
    f.logLine()
    client = f.connect_mqtt()
    client.loop_start()

    # INFLUXDB
    if "influxdb" in config and config["influxdb"] != {}:
        f.logLine()
        f.log("InfluxDB connect :")
        influxdb = influxdb_client.InfluxDBClient(
            url=f"http://{config['influxdb']['host']}:{config['influxdb']['port']}",
            token=config['influxdb']['token'],
            org=config['influxdb']['org']
        )
        health = influxdb.health()
        if health.status == "pass":
            f.log(" => Connection success")
        else:
            f.log(" => Connection failed", "CRITICAL")

        influxdb_api = influxdb.write_api(write_options=ASYNCHRONOUS)

    while True:

        for pdl, pdl_config in config['enedis_gateway'].items():
            run(pdl, pdl_config)

        con.close()
        time.sleep(config['cycle'])

# lost_params = []
# for id, config_data in default.items():
#     isDict = False
#     if isinstance(default[id], dict):
#         isDict = True
#     mandatory = False
#     if id.startswith('*'):
#         mandatory = True
#         id = id[1:]
#     if mandatory == True and not id in config:
#         lost_params.append(id)
#     if isDict == True:
#         for id_1, data_1 in config_data.items():
#             isDict = False
#             if isinstance(config_data[id_1], dict):
#                 isDict = True
#             mandatory = False
#             if id_1.startswith('*'):
#                 mandatory = True
#                 id_1 = f"{id}.{id_1[1:]}"
#             if mandatory == True and not id_1 in config[id]:
#                 lost_params.append(id_1)
#         if isDict == True:
#             for id_2, data_2 in data_1.items():
#                 mandatory = False
#                 if id_2.startswith('*'):
#                     mandatory = True
#                     id_2 = f"{id_1}.{id_2[1:]}"
#                 if mandatory == True and not id_2 in config[id]:
#                     lost_params.append(id_2)
#                 # else:
#                 #     if not id_2 in config[id][id_1]:
#                 #         config[id][id_1] = data_2
#         else:
#             if not id_1 in config[id]:
#                 config[id] = data_1
#     else:
#         if not id in config:
#             config[id] = config_data
