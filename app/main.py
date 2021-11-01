import os
import time
from dateutil.relativedelta import *
from datetime import datetime
from distutils.util import strtobool
import sqlite3
import locale
from pprint import pprint
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

########################################################################################################################
# AUTHENTIFICATION
if "ACCESS_TOKEN" in os.environ:
    accessToken = os.environ['ACCESS_TOKEN']
else:
    accessToken = ""
if "PDL" in os.environ:
    pdl = os.environ['PDL']
else:
    pdl = ""

########################################################################################################################
# MQTT
if "MQTT_HOST" in os.environ:
    broker = os.environ['MQTT_HOST']
else:
    broker = ""
if "MQTT_PORT" in os.environ:
    port = int(os.environ['MQTT_PORT'])
else:
    port = 1883
if "MQTT_PREFIX" in os.environ:
    prefix = os.environ['MQTT_PREFIX']
else:
    prefix = "enedis_gateway"
if "MQTT_CLIENT_ID" in os.environ:
    client_id = os.environ['MQTT_CLIENT_ID']
else:
    client_id = "enedis_gateway"
if "MQTT_USERNAME" in os.environ:
    username = os.environ['MQTT_USERNAME']
else:
    username = ""
if "MQTT_PASSWORD" in os.environ:
    password = os.environ['MQTT_PASSWORD']
else:
    password: ""
if "RETAIN" in os.environ:
    retain = bool(strtobool(os.environ['RETAIN']))
else:
    retain = False
if "QOS" in os.environ:
    qos = int(os.environ['QOS'])
else:
    qos = 0
########################################################################################################################
# HOME ASSISTANT
if "HA_AUTODISCOVERY" in os.environ:
    ha_autodiscovery = bool(strtobool(os.environ['HA_AUTODISCOVERY']))
else:
    ha_autodiscovery = False
if "HA_AUTODISCOVERY_PREFIX" in os.environ:
    ha_autodiscovery_prefix = str(os.environ['HA_AUTODISCOVERY_PREFIX'])
else:
    ha_autodiscovery_prefix = "homeassistant"

########################################################################################################################
# CONSUMPTION
if "GET_CONSUMPTION" in os.environ:
    get_consumption = bool(strtobool(os.environ['GET_CONSUMPTION']))
else:
    get_consumption = True
if "GET_CONSUMPTION_DETAIL" in os.environ:
    get_consumption_detail = bool(strtobool(os.environ['GET_CONSUMPTION_DETAIL']))
else:
    get_consumption_detail = True
if "CONSUMPTION_PRICE_BASE" in os.environ:
    consumption_price_base = float(os.environ['CONSUMPTION_PRICE_BASE'])
else:
    consumption_price_base = 0
if "CONSUMPTION_PRICE_HC" in os.environ:
    consumption_price_hc = float(os.environ['CONSUMPTION_PRICE_HC'])
else:
    consumption_price_hc = 0
if "CONSUMPTION_PRICE_HP" in os.environ:
    consumption_price_hp = float(os.environ['CONSUMPTION_PRICE_HP'])
else:
    consumption_price_hp = 0

########################################################################################################################
# PRODUCTION
if "GET_PRODUCTION" in os.environ:
    get_production = bool(strtobool(os.environ['GET_PRODUCTION']))
else:
    get_production = False
if "GET_PRODUCTION_DETAIL" in os.environ:
    get_production_detail = bool(strtobool(os.environ['GET_PRODUCTION_DETAIL']))
else:
    get_production_detail = False
# if "PRODUCTION_PRICE" in os.environ:
#     production_price = float(os.environ['PRODUCTION_PRICE'])
# else:
#     production_price = 0

########################################################################################################################
# HC/HP
if "OFFPEAK_HOURS" in os.environ:
    offpeak_hours = str(os.environ['OFFPEAK_HOURS'])
else:
    offpeak_hours = None

########################################################################################################################
# ADDRESSES
if "ADDRESSES" in os.environ:
    addresses = bool(strtobool(os.environ['ADDRESSES']))
else:
    addresses = True

########################################################################################################################
# CYCLE
if "CYCLE" in os.environ:
    cycle = int(os.environ['CYCLE'])
    if cycle < 3600:
        cycle = 3600
else:
    cycle = 3600

########################################################################################################################
# REFRESH_CONTRACT
if "REFRESH_CONTRACT" in os.environ:
    refresh_contract = bool(strtobool(os.environ['REFRESH_CONTRACT']))
else:
    refresh_contract = False

########################################################################################################################
# REFRESH_ADDRESSES
if "REFRESH_ADDRESSES" in os.environ:
    refresh_addresses = bool(strtobool(os.environ['REFRESH_ADDRESSES']))
else:
    refresh_addresses = False

########################################################################################################################
# WIPE_CACHE
if "WIPE_CACHE" in os.environ:
    wipe_cache = bool(strtobool(os.environ['WIPE_CACHE']))
else:
    wipe_cache = False

########################################################################################################################
# DEBUG
if "DEBUG" in os.environ:
    debug = bool(strtobool(os.environ['DEBUG']))
else:
    debug = False

########################################################################################################################
# CURRENT_PLAN
if "CURRENT_PLAN" in os.environ:
    current_plan = str(os.environ['CURRENT_PLAN'])
else:
    current_plan = "BASE"

########################################################################################################################
# CARD MYENEDIS
if "CARD_MYENEDIS" in os.environ:
    card_myenedis = bool(strtobool(os.environ['CARD_MYENEDIS']))
else:
    card_myenedis = False

########################################################################################################################
# INFLUXDB_ENABLE
if "INFLUXDB_ENABLE" in os.environ:
    influxdb_enable = bool(strtobool(os.environ['INFLUXDB_ENABLE']))
else:
    influxdb_enable = False
########################################################################################################################
# INFLUXDB_HOST
if "INFLUXDB_HOST" in os.environ:
    influxdb_host = str(os.environ['INFLUXDB_HOST'])
else:
    influxdb_host = ""
########################################################################################################################
# INFLUXDB_PORT
if "INFLUXDB_PORT" in os.environ:
    influxdb_port = str(os.environ['INFLUXDB_PORT'])
else:
    influxdb_port = 8086
########################################################################################################################
# INFLUXDB_TOKEN
if "INFLUXDB_TOKEN" in os.environ:
    influxdb_token = str(os.environ['INFLUXDB_TOKEN'])
else:
    influxdb_token = ""
########################################################################################################################
# INFLUXDB_ORG
if "INFLUXDB_ORG" in os.environ:
    influxdb_org = str(os.environ['INFLUXDB_ORG'])
else:
    influxdb_org = ""
########################################################################################################################
# INFLUXDB_BUCKET
if "INFLUXDB_BUCKET" in os.environ:
    influxdb_bucket = str(os.environ['INFLUXDB_BUCKET'])
else:
    influxdb_bucket = ""

api_no_result = []

headers = {
    'Content-Type': 'application/json',
    'Authorization': accessToken,
    'call-service': "enedisgateway2mqtt",
    'version': VERSION
}

def init_database(cur):
    f.log("Initialise database")

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
    # cur.execute('''CREATE TABLE consumption_detail_try (
    #                     pdl TEXT NOT NULL,
    #                     date TEXT NOT NULL,
    #                     try INTEGER)''')
    # cur.execute('''CREATE UNIQUE INDEX idx_date_consumption_detail_try
    #                 ON consumption_detail_try (date)''')
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

def run():

    global offpeak_hours

    while True:

        # SQLlite
        if not os.path.exists('/data'):
            os.mkdir('/data')

        if wipe_cache == True:
            if os.path.exists('/data/enedisgateway.db'):
                f.logLine()
                f.log("Reset Cache")
                os.remove("/data/enedisgateway.db")

        f.log("Check database")
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

                list_tables = ["config", "addresses", "contracts", "consumption_daily", "consumption_detail", "production_daily", "production_detail"]

                query = f"SELECT name FROM sqlite_master WHERE type='table';"
                cur.execute(query)
                query_result = cur.fetchall()
                tables = []
                for table in query_result:
                    tables.append(str(table).replace("('", "").replace("',)", ''))
                for tab in list_tables:
                    if not tab in tables:
                        f.log(f"Table {tab} is missing")
                        raise
                cur.execute("INSERT OR REPLACE INTO config VALUES (?,?)", [0, 0])
                cur.execute("INSERT OR REPLACE INTO addresses VALUES (?,?,?)", [0, 0, 0])
                cur.execute("INSERT OR REPLACE INTO contracts VALUES (?,?,?)", [0, 0, 0])
                cur.execute("INSERT OR REPLACE INTO consumption_daily VALUES (?,?,?,?)", [0, '1970-01-01', 0, 0])
                cur.execute("INSERT OR REPLACE INTO consumption_detail VALUES (?,?,?,?,?,?)", [0, '1970-01-01', 0, 0, "", 0])
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
                f.log("Reset database")
                con.close()
                os.remove("/data/enedisgateway.db")
                f.log(" => Reconnect")
                con = sqlite3.connect('/data/enedisgateway.db', timeout=10)
                cur = con.cursor()
                init_database(cur)

        f.logLine()
        f.log("Get contract :")
        contract = cont.getContract(client, cur, con)
        f.log(contract,"debug")
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
                    if ha_autodiscovery == True:
                        ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=key, value=data)

            if addresses == True:
                f.logLine()
                f.log("Get Addresses :")
                addresse = addr.getAddresses(client, con, cur)
                if "error_code" in addresse:
                    f.publish(client, f"addresses/error", str(1))
                    for key, data in addresse["detail"].items():
                        f.publish(client, f"addresses/errorMsg/{key}", str(data))
                else:
                    f.publish(client, f"addresses/error", str(0))

            if get_consumption == True:
                f.logLine()
                f.log("Get Consumption :")
                ha_discovery_consumption = day.getDaily(cur, con, client, "consumption", last_activation_date)
                f.logLine1()
                f.log("                        SUCCESS : Consumption daily imported")
                f.logLine1()
                if ha_autodiscovery == True:
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
                                ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name, value=sensor_data['value'],
                                                   attributes=attributes, unit_of_meas=unit_of_meas,
                                                   device_class=device_class, state_class=state_class)
                f.log(" => HA Sensor updated")
            # f.logLine()

            if get_consumption_detail == True:
                f.log("Get Consumption Detail:")
                ha_discovery_consumption = detail.getDetail(cur, con, client, "consumption", last_activation_date, offpeak_hours)
                f.logLine1()
                f.log("                   SUCCESS : Consumption detail imported")
                f.logLine1()
                if ha_autodiscovery == True:
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
                                ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name, value=sensor_data['value'],
                                                   attributes=attributes, unit_of_meas=unit_of_meas,
                                                   device_class=device_class, state_class=state_class)
                    f.log(" => HA Sensor updated")
            # f.logLine()

            if get_production == True:
                f.logLine()
                f.log("Get production :")
                ha_discovery_production = day.getDaily(cur, con, client, "production", last_activation_date)
                f.logLine1()
                f.log("             SUCCESS : Production daily imported")
                f.logLine1()
                if ha_autodiscovery == True:
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

            if get_production_detail == True:
                f.logLine()
                f.log("Get production Detail:")
                ha_discovery_consumption = detail.getDetail(cur, con, client, "production", last_activation_date, offpeak_hours)
                f.logLine1()
                f.log("              SUCCESS : Production detail imported")
                f.logLine1()
                if ha_autodiscovery == True:
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
                                ha.haAutodiscovery(client=client, type="sensor", pdl=pdl, name=name, value=sensor_data['value'],
                                                   attributes=attributes, unit_of_meas=unit_of_meas,
                                                   device_class=device_class, state_class=state_class)
                    f.log(" => HA Sensor updated")

            if card_myenedis == True:
                f.logLine()
                f.log("Generate Sensor for myEnedis card")
                my_enedis_data = myenedis.myEnedis(cur, con, client, last_activation_date, offpeak_hours)
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


            if influxdb_enable == True:
                f.logLine()
                f.log("Push data in influxdb")
                influx.influxdb_insert(cur, con, influxdb_api)
                f.log(" => Data exported")

            query = f"SELECT * FROM consumption_daily WHERE pdl == '{pdl}' AND fail > {fail_count} ORDER BY date"
            rows = con.execute(query)
            if rows.fetchone() is not None:
                f.logLine()
                f.log(f"Consumption data not found on enedis (after {fail_count} retry) :")
                # pprint(rows.fetchall())
                for row in rows:
                    f.log(f"{row[0]} => {row[1]}")

            query = f"SELECT * FROM production_daily WHERE pdl == '{pdl}' AND fail > {fail_count} ORDER BY date"
            rows = con.execute(query)
            if rows.fetchone() is not None:
                f.logLine()
                f.log(f"Production data not found on enedis (after {fail_count} retry) :")
                # pprint(rows.fetchall())
                for row in rows:
                    f.log(f"{row[0]} => {row[1]}")

        con.commit()
        con.close()

        f.logLine()
        f.log("IMPORT FINISH")
        f.logLine()

        time.sleep(cycle)

if __name__ == '__main__':

    if accessToken == "":
        f.log("Environement variable 'ACCESS_TOKEN' is mandatory", "CRITICAL")
    if pdl == "":
        f.log("Environement variable 'PDL' is mandatory", "CRITICAL")
    if broker == "":
        f.log("Environement variable 'MQTT_HOST' is mandatory", "CRITICAL")
    if broker == "":
        f.log("Environement variable 'MQTT_HOST' can't be empty")

    # MQTT
    client = f.connect_mqtt()
    client.loop_start()
    pprint(client)

    # INFLUXDB
    if influxdb_enable == True:
        influxdb = influxdb_client.InfluxDBClient(
            url=f"http://{influxdb_host}:{influxdb_port}",
            token=influxdb_token,
            org=influxdb_org
        )
        health = influxdb.health()
        if health.status == "pass":
            f.log("InfluxDB : Connection success")
        else:
            f.log("InfluxDB : Connection failed", "CRITICAL")

        influxdb_api = influxdb.write_api(write_options=ASYNCHRONOUS)

    run()
