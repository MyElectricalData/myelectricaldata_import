import requests
from paho.mqtt import client as mqtt_client
from datetime import datetime
import json
from pprint import pprint
import main

from importlib import import_module

main = import_module("main")


def connect_mqtt():
    try:
        client = mqtt_client.Client(main.client_id)
        if main.username != "" and main.password != "":
            client.username_pw_set(main.username, main.password)
        client.on_connect = on_connect
        client.connect(main.broker, main.port)
        log("Connected to MQTT Broker!")
        return client
    except:
        log(f"Failed to connect to MQTT Broker")
        log(f" => Check your MQTT Configuration", "CRITICAL")

def publish(client, topic, msg, prefix=main.prefix):
    msg_count = 0
    result = client.publish(f'{prefix}/{topic}', str(msg), qos=main.qos, retain=main.retain)
    status = result[0]
    if status == 0:
        log(f" MQTT Send : {prefix}/{topic} => {msg}", "debug")
    else:
        log(f" - Failed to send message to topic {prefix}/{topic}")
    msg_count += 1


def subscribe(client, topic, prefix=main.prefix):
    def on_message(client, userdata, msg):
        print(f" MQTT Received : `{prefix}/{topic}` => `{msg.payload.decode()}`")

    sub_topic = f"{prefix}/{topic}"
    client.subscribe(client, sub_topic)
    client.on_message = on_message


def logLine():
    log("####################################################################################")


def log(msg, level="INFO "):
    now = datetime.now()
    level = level.upper()
    display = False
    critical = False
    if main.debug == True and level == "DEBUG":
        display = True
    if level == "INFO ":
        display = True
    if level == "ERROR":
        display = True
    if level == "CRITICAL":
        display = True
        critical = True
    if display:
        print(f"{now} - {level} : {msg}")
    if critical:
        quit()


def splitLog(msg):
    format_log = ""
    i = 1
    nb_col = 12
    msg_length = len(msg)
    cur_length = 1
    for log_msg in msg:
        format_log += f" | {log_msg}"
        if i == nb_col:
            i = 1
            format_log += f" |"
            log(format_log)
            format_log = ""
        elif cur_length == msg_length:
            format_log += f" |"
            log(format_log)
        else:
            i = i + 1
        cur_length = cur_length + 1


def apiRequest(cur, con, type="POST", url=None, headers=None, data=None):
    config_query = f"SELECT * FROM config WHERE key = 'config'"
    cur.execute(config_query)
    query_result = cur.fetchall()
    query_result = json.loads(query_result[0][1])
    log(f"call_number : {query_result['call_number']}", "debug")
    if query_result["day"] == datetime.now().strftime('%Y-%m-%d'):
        if query_result["call_number"] > query_result["max_call"]:
            return {
                "error_code": 2,
                "description": f"API Call number per day is reached ({query_result['max_call']}), please wait until tomorrow to load the rest of data"
            }
        else:
            query_result["call_number"] = int(query_result["call_number"]) + 1
            query_result["day"] = datetime.now().strftime('%Y-%m-%d')
            query = f"UPDATE config SET key = 'config', value = '{json.dumps(query_result)}' WHERE key = 'config'"
            cur.execute(query)
            con.commit()

    else:
        query_result["call_number"] = 0
    log(f"Call API : {url}", "DEBUG")
    log(f"Data : {data}", "DEBUG")
    retour = requests.request(type, url=f"{url}", headers=headers, data=data).json()
    if main.debug == True:
        pprint(f"API Return :")
        pprint(retour)
    return retour
