from paho.mqtt import client as mqtt_client
from datetime import datetime

from importlib import import_module
main = import_module("main")

def connect_mqtt():

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            log("Connected to MQTT Broker!")
        else:
            log("Failed to connect, return code %d\n", rc)

    # Set Connecting Client ID
    client = mqtt_client.Client(main.client_id)
    if main.username != "" and main.password != "":
        client.username_pw_set(main.username, main.password)
    client.on_connect = on_connect
    client.connect(main.broker, main.port)
    return client

def publish(client, topic, msg, current_prefix="enedis_gateway"):
    msg_count = 0
    result = client.publish(f'{current_prefix}/{topic}', str(msg), qos=main.qos, retain=int(main.retain))
    status = result[0]
    if status == 0:
        log(f" MQTT Send : {current_prefix}/{topic} => {msg}")
    else:
        log(f" - Failed to send message to topic {current_prefix}/{topic}")
    msg_count += 1

def log(msg):
    now = datetime.now()
    print(f"{now} : {msg}")
