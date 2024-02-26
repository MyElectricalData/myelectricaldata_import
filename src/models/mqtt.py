import logging

import paho.mqtt.publish as publish
from paho.mqtt import client as mqtt

from dependencies import separator, title


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
        port=1883,
        ca_cert=None,
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
        self.ca_cert = ca_cert
        self.connect()

    def connect(self):
        separator()
        logging.info(f"Connect to MQTT broker {self.hostname}:{self.port}")
        try:
            self.client = mqtt.Client(self.client_id)
            if self.username != "" and self.password != "":
                self.client.username_pw_set(self.username, self.password)
            if self.ca_cert:
                logging.info(f"Using ca_cert: {self.ca_cert}")
                self.client.tls_set(ca_certs=self.ca_cert)
            self.client.connect(self.hostname, self.port)
            self.client.loop_start()
            title("Connection success")
        except Exception as e:
            logging.critical(["MQTT Connexion failed", e])

    def publish(self, topic, msg, prefix=None):
        if prefix is None:
            prefix = self.prefix
        result = self.client.publish(f"{self.prefix}/{prefix}/{topic}", str(msg), qos=self.qos, retain=self.retain)
        status = result[0]
        if status == 0:
            logging.debug(f" MQTT Send : {prefix}/{topic} => {msg}")
        else:
            logging.info(f" - Failed to send message to topic {prefix}/{topic}")

    def publish_multiple(self, data, prefix=None):
        if data:
            payload = []
            if prefix is None:
                prefix = self.prefix
            else:
                prefix = f"{prefix}"
            for topics, value in data.items():
                payload.append(
                    {"topic": f"{prefix}/{topics}", "payload": value, "qos": self.qos, "retain": self.retain}
                )
            auth = None
            if self.username is not None and self.password is not None:
                auth = {"username": self.username, "password": self.password}
            publish.multiple(payload, hostname=self.hostname, port=self.port, client_id=self.client_id, auth=auth)
