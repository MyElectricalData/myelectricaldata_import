from paho.mqtt import client as mqtt_client
from datetime import datetime

from importlib import import_module

main = import_module("main")


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log("Connected to MQTT Broker!")
        else:
            log(f"Failed to connect, return code {rc}\n")
            quit()

    # Set Connecting Client ID
    client = mqtt_client.Client(main.client_id)
    if main.username != "" and main.password != "":
        client.username_pw_set(main.username, main.password)
    client.on_connect = on_connect
    client.connect(main.broker, main.port)
    return client


def publish(client, topic, msg, prefix=main.prefix):
    msg_count = 0
    result = client.publish(f'{prefix}/{topic}', str(msg), qos=main.qos, retain=main.retain)
    status = result[0]
    if status == 0:
        log(f" MQTT Send : {prefix}/{topic} => {msg}")
    else:
        log(f" - Failed to send message to topic {prefix}/{topic}")
    msg_count += 1


def subscribe(client, topic, prefix=main.prefix):
    def on_message(client, userdata, msg):
        print(f" MQTT Received : `{prefix}/{topic}` => `{msg.payload.decode()}`")

    sub_topic = f"{prefix}/{topic}"
    client.subscribe(client, sub_topic)
    client.on_message = on_message

def log(msg):
    now = datetime.now()
    print(f"{now} : {msg}")


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
