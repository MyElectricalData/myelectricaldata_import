import __main__ as app
import datetime
from pprint import pprint
from mergedeep import Strategy, merge

import paho.mqtt.publish as publish
from dependencies import *
from paho.mqtt import client as mqtt



class Mqtt:

    def __init__(
            self,
            hostname,
            username="",
            password="",
            client_id="myelectricaldata",
            prefix="myelectricaldata",
            retain=True,
            qos=0,
            port=1883
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.client_id = client_id
        self.prefix = prefix
        self.retain = retain
        self.qos = qos

        self.client = {}
        self.connect()

    def connect(self):
        app.LOG.separator()
        app.LOG.log(f"Connect to MQTT broker {self.hostname}:{self.port}")
        try:
            self.client = mqtt.Client(self.client_id)
            if self.username != "" and self.password != "":
                self.client.username_pw_set(self.username, self.password)
            self.client.connect(self.hostname, self.port)
            self.client.loop_start()
            app.LOG.log(" => Connection success")
        except Exception as e:
            app.LOG.critical(["MQTT Connexion failed", e])

    def publish(self, topic, msg, prefix=None):
        if prefix is None:
            prefix = self.prefix
        result = self.client.publish(
            f'{self.prefix}/{prefix}/{topic}',
            str(msg),
            qos=self.qos,
            retain=self.retain
        )
        status = result[0]
        if status == 0:
            app.LOG.debug(f" MQTT Send : {prefix}/{topic} => {msg}")
        else:
            app.LOG.log(f" - Failed to send message to topic {prefix}/{topic}")

    def publish_multiple(self, data, prefix=None):
        if data:
            payload = []
            if prefix is None:
                prefix = ""
            else:
                prefix = f"{prefix}"
            for topics, value in data.items():
                payload.append({
                    "topic": f"{self.prefix}{prefix}/{topics}",
                    "payload": value,
                    "qos": self.qos,
                    "retain": self.retain
                })
            # pprint(payload)
            auth = None
            if self.username == "" and self.password == "":
                auth = {'username': self.username, 'password': self.password}
            publish.multiple(payload, hostname=self.hostname, port=self.port, client_id=self.client_id, auth=auth)

