import requests
import os
from pprint import pprint
import json
from paho.mqtt import client as mqtt_client
import random
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import *

def log(msg):
    now = datetime.now()
    print(f"{now} : {msg}")

url = "https://enedisgateway.tech/api"

if not "ACCESS_TOKEN" in os.environ:
    log("Environement variable 'ACCESS_TOKEN' is mandatory")
    quit()
if not "PDL" in os.environ:
    log("Environement variable 'PDL' is mandatory")
    quit()
if not "MQTT_HOST" in os.environ:
    log("Environement variable 'MQTT_HOST' is mandatory")
    quit()

accessToken = os.environ['ACCESS_TOKEN']
pdl = os.environ['PDL']
broker = os.environ['MQTT_HOST']

if broker == "":
    log("Environement variable 'MQTT_HOST' can't be empty")
    quit()

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
if "CYCLE" in os.environ:
    cycle = int(os.environ['CYCLE'])
else:
    cycle = 86400
if "RETAIN" in os.environ:
    retain = int(os.environ['RETAIN'])
else:
    retain = True
if "BASE_PRICE" in os.environ:
    base_price = float(os.environ['BASE_PRICE'])
else:
    base_price = False
if "HA_AUTODISCOVERY" in os.environ:
    ha_autodiscovery = os.environ['HA_AUTODISCOVERY']
else:
    ha_autodiscovery = False
if "HA_AUTODISCOVERY_PREFIX" in os.environ:
    ha_autodiscovery_prefix = os.environ['HA_AUTODISCOVERY_PREFIX']
else:
    ha_autodiscovery_prefix = "homeassistant"

# ! GENERATE 1 API CALL !
if "YEARS" in os.environ:
    years = int(os.environ['YEARS'])
else:
    years = 1

# ! GENERATE 1 API CALL !
if "ADDRESSES" in os.environ:
    addresses = int(os.environ['ADDRESSES'])
else:
    addresses = True

# Fix min cycle
if cycle < 3600:
    cycle = 3600

if years >= 3:
    years = 3

headers = {
    'Content-Type': 'application/json',
    'Authorization': accessToken
}


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log("Connected to MQTT Broker!")
        else:
            log("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    if username != "" and password != "":
        client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, msg, current_prefix=prefix):
    msg_count = 0
    result = client.publish(f'{current_prefix}/{topic}', str(msg), qos=0, retain=retain)
    status = result[0]
    if status == 0:
        log(f"  => Send `{msg}` to topic `{current_prefix}/{topic}`")
    else:
        log(f"  => Failed to send message to topic {current_prefix}/{topic}")
    msg_count += 1

def getContract(client):
    data = {
        "type": "contracts",
        "usage_point_id": str(pdl),
    }
    contract = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()
    retour = ""
    if "customer" in contract:
        customer = contract["customer"]
        publish(client, f"{pdl}/details/customer_id", str(customer["customer_id"]))
        for usage_points in customer['usage_points']:
            for usage_point_key, usage_point_data in usage_points['usage_point'].items():
                publish(client, f"{pdl}/details/usage_points/usage_point/{usage_point_key}", str(usage_point_data))
            for contracts_key, contracts_data in usage_points['contracts'].items():
                publish(client, f"{pdl}/details/usage_points/contracts/{contracts_key}", str(contracts_data))
                if contracts_key == "last_activation_date":
                    retour = contracts_data
                    publish(client, f"{pdl}/activation_date", str(contracts_data))
                if contracts_key == "subscribed_power":
                    publish(client, f"{pdl}/subscribed_power", str(contracts_data.split()[0]))
                if contracts_key == "offpeak_hours":
                    offpeak_hours = contracts_data[contracts_data.find("(") + 1:contracts_data.find(")")].split(';')
                    index = 0
                    for oh in offpeak_hours:
                        publish(client, f"{pdl}/offpeak_hours/{index}/start", str(oh.split('-')[0]))
                        publish(client, f"{pdl}/offpeak_hours/{index}/stop", str(oh.split('-')[1]))
                        index = index + 1
                    publish(client, f"{pdl}/offpeak_hours", str(contracts_data))
    else:
        retour = {
            "error": True,
            "errorMsg": contract
        }
    return retour


def getAddresses(client):
    data = {
        "type": "addresses",
        "usage_point_id": str(pdl),
    }
    addresses = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()
    customer = addresses["customer"]
    publish(client, f"{pdl}/details/customer_id", str(customer["customer_id"]))
    for usage_points in customer['usage_points']:
        for usage_point_key, usage_point_data in usage_points['usage_point'].items():
            if isinstance(usage_point_data, dict):
                for usage_point_data_key, usage_point_data_data in usage_point_data.items():
                    publish(client, f"{pdl}/details/usage_points/usage_point/{usage_point_key}/{usage_point_data_key}",
                            str(usage_point_data_data))
            else:
                publish(client, f"{pdl}/details/usage_points/usage_point/{usage_point_key}", str(usage_point_data))


def calcVariation(client, queue, data, lastData):
    if "thisWeek" in data:
        thisWeek = data['thisWeek']
        lastWeek = lastData['thisWeek']
        pourcentWeek = (lastWeek - thisWeek) / thisWeek * 100
        publish(client, f"{pdl}/consumption/{queue}/variationWeek", str(round(pourcentWeek, 2)))
    if "thisMonth" in data:
        thisMonth = data['thisMonth']
        lastMonth = lastData['thisMonth']
        pourcentMonth = (lastMonth - thisMonth) / thisMonth * 100
        publish(client, f"{pdl}/consumption/{queue}/variationMonth", str(round(pourcentMonth, 2)))
    if "thisYear" in data:
        thisYear = data['thisYear']
        lastYear = lastData['thisYear']
        pourcentYear = (lastYear - thisYear) / lastYear * 100
        publish(client, f"{pdl}/consumption/{queue}/variationYear", str(round(pourcentYear, 2)))
    return data


def ha_autodiscovery(client, type="Sensor", name=None, value=None, unit_of_meas=None, device_class=None,
                     state_class=None):

    name = name.replace("-", "_")

    config = {
        "name": f"{name}",
        "stat_t": f"{ha_autodiscovery_prefix}/{type}/enedisgateway_{name}/state",
        # "json_attr_t": f"{ha_autodiscovery_prefix}/{type}/enedisgateway_{name}/attributes",
    }
    if unit_of_meas is not None:
        config['unit_of_meas'] = str(unit_of_meas)
    if device_class is not None:
        config['device_class'] = str(device_class)
    if state_class is not None:
        config['state_class'] = str(state_class)

    publish(client, f"{type}/enedisgateway_{name}/config", json.dumps(config), ha_autodiscovery_prefix)
    publish(client, f"{type}/enedisgateway_{name}/state", str(value), ha_autodiscovery_prefix)


def dailyConsumption(client, last_activation_date):
    my_date = datetime.now()

    # Check activation data
    last_activation_date = last_activation_date.split("+")[0]
    last_activation_date = datetime.strptime(last_activation_date, '%Y-%m-%d')

    lastYears = datetime.now() + relativedelta(years=-1)
    dateBegin = lastYears.strftime('%Y-%m-%d')
    dateEnded = my_date.strftime('%Y-%m-%d')

    data = dailyConsumptionBeetwen(pdl, dateBegin, dateEnded, last_activation_date)
    for key, value in data.items():
        publish(client, f"{pdl}/consumption/current_year/{key}", str(value))
        ha_autodiscovery(client, "sensor", f"consumption_current_year_{key}", str(value), "W", "energy",
                         "total_increasing")
        if base_price != False:
            if isinstance(value, int):
                roundValue = round(int(value) / 1000 * base_price, 2)
                publish(client, f"{pdl}/price/current_year/{key}", roundValue)
                ha_autodiscovery(client, "sensor", f"price_current_year_{key}", roundValue, "€", 'monetary')
        lastData = data

    current_year = 1
    while current_year <= years:
        if years >= current_year:
            log(f"Year => {current_year}")
            dateEnded = dateBegin
            dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
            dateBegin = dateEndedDelta + relativedelta(years=-1)
            dateBegin = dateBegin.strftime('%Y-%m-%d')
            data = dailyConsumptionBeetwen(pdl, dateBegin, dateEnded, last_activation_date)
            if "error_code" in data:
                publish(client, f"{pdl}/consumption/year-{current_year}/error", str(1))
                for key, value in data.items():
                    publish(client, f"{pdl}/consumption/year-{current_year}/errorMsg/{key}", str(value))
            else:
                publish(client, f"{pdl}/consumption/year-{current_year}/error", str(0))
                for key, value in data.items():
                    publish(client, f"{pdl}/consumption/year-{current_year}/{key}", str(value))
                    ha_autodiscovery(client, "sensor", f"consumption_year_{current_year}_{key}", str(value), "W",
                                     "energy", "total_increasing")
                    if base_price != False:
                        if isinstance(value, int):
                            roundValue = round(int(value) / 1000 * base_price, 2)
                            publish(client, f"{pdl}/price/year-{current_year}/{key}", roundValue)
                            ha_autodiscovery(client, "sensor", f"price_year_{current_year}_{key}", roundValue, "€",
                                             'monetary')
            if current_year == 1:
                queue = "current_year"
            else:
                queue = f"year-{current_year - 1}"
            lastData = calcVariation(client, queue, data, lastData)
            current_year = current_year + 1


def dailyConsumptionBeetwen(pdl, dateBegin, dateEnded, last_activation_date):
    response = {}

    lastYears = datetime.strptime(dateEnded, '%Y-%m-%d')
    lastYears = lastYears + relativedelta(years=-1)
    if lastYears < last_activation_date:
        dateBegin = last_activation_date
        dateBegin = dateBegin.strftime('%Y-%m-%d')

    response['dateBegin'] = dateBegin
    response['dateEnded'] = dateEnded

    data = {
        "type": "daily_consumption",
        "usage_point_id": str(pdl),
        "start": str(dateBegin),
        "end": str(dateEnded),
    }

    try:
        daily_consumption = requests.request("POST", url=f"{url}", headers=headers, data=json.dumps(data)).json()

        meter_reading = daily_consumption['meter_reading']

        mesures = {}
        for interval_reading in meter_reading["interval_reading"]:
            date = interval_reading['date']
            value = interval_reading['value']
            mesures[date] = value
        # mesure = sorted(mesures, reverse=True)
        list_date = list(reversed(sorted(mesures.keys())))

        dateEnded = datetime.strptime(dateEnded, '%Y-%m-%d')

        dateWeek = dateEnded + relativedelta(days=-7)
        dateMonths = dateEnded + relativedelta(months=-1)
        dateYears = dateEnded + relativedelta(years=-1)
        j1 = dateEnded + relativedelta(days=-1)
        j1 = j1.replace(hour=0, minute=0, second=0, microsecond=0)
        j2 = dateEnded + relativedelta(days=-2)
        j2 = j2.replace(hour=0, minute=0, second=0, microsecond=0)
        j3 = dateEnded + relativedelta(days=-3)
        j3 = j3.replace(hour=0, minute=0, second=0, microsecond=0)
        j4 = dateEnded + relativedelta(days=-4)
        j4 = j4.replace(hour=0, minute=0, second=0, microsecond=0)
        j5 = dateEnded + relativedelta(days=-5)
        j5 = j5.replace(hour=0, minute=0, second=0, microsecond=0)
        j6 = dateEnded + relativedelta(days=-6)
        j6 = j6.replace(hour=0, minute=0, second=0, microsecond=0)
        j7 = dateEnded + relativedelta(days=-7)
        j7 = j7.replace(hour=0, minute=0, second=0)

        energyWeek = 0
        energyMonths = 0
        energyYears = 0

        for date in list_date:
            value = int(mesures[date])
            current_date = datetime.strptime(date, '%Y-%m-%d')

            # WEEK DAYS
            if current_date == j1:
                response['j-1'] = value
            if current_date == j2:
                response['j-2'] = value
            if current_date == j3:
                response['j-3'] = value
            if current_date == j4:
                response['j-4'] = value
            if current_date == j5:
                response['j-5'] = value
            if current_date == j6:
                response['j-6'] = value
            if current_date == j7:
                response['j-7'] = value
            # LAST WEEK
            if current_date >= dateWeek:
                energyWeek = int(energyWeek) + int(value)
            # LAST MONTH
            if current_date >= dateMonths:
                energyMonths = int(energyMonths) + int(value)
            # LAST YEARS
            if current_date >= dateYears:
                energyYears = int(energyYears) + int(value)

        response['thisWeek'] = energyWeek
        response['thisMonth'] = energyMonths
        response['thisYear'] = energyYears
    except:
        for error_key, error_msg in daily_consumption.items():
            response[error_key] = error_msg

    return response


def run():
    client = connect_mqtt()
    client.loop_start()
    while True:
        log("Get contract :")
        last_activation_date = getContract(client)
        if "error" in last_activation_date:
            publish(client, f"error", str(1))
            for key, data in last_activation_date["errorMsg"].items():
                publish(client, f"errorMsg/{key}", str(data))
        else:
            publish(client, f"error", str(0))
            if addresses == True:
                log("Get Addresses :")
                getAddresses(client)
            log("Get Consumption :")
            dailyConsumption(client, last_activation_date)
        time.sleep(cycle)


if __name__ == '__main__':
    run()
