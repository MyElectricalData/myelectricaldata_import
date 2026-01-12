"""MQTT Client."""

import inspect
import logging

from paho.mqtt import client as mqtt
from paho.mqtt import publish

from config.main import APP_CONFIG
from const import URL_CONFIG_FILE
from utils import separator


class Mqtt:
    """MQTT Client."""

    def __init__(self):
        self.client: mqtt.Client = {}
        self.valid: bool = False
        self.connect()

    def connect(self) -> None:
        """Connector."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            separator()
            logging.info(f"Connect to MQTT broker {APP_CONFIG.mqtt.hostname}:{APP_CONFIG.mqtt.port}")
            try:
                self.client = mqtt.Client(APP_CONFIG.mqtt.client_id)
                if APP_CONFIG.mqtt.username != "" and APP_CONFIG.mqtt.password != "":
                    self.client.username_pw_set(APP_CONFIG.mqtt.username, APP_CONFIG.mqtt.password)
                if APP_CONFIG.mqtt.cert:
                    logging.info(f"Using ca_cert: {APP_CONFIG.mqtt.cert}")
                    self.client.tls_set(ca_certs=APP_CONFIG.mqtt.cert)
                self.client.connect(APP_CONFIG.mqtt.hostname, APP_CONFIG.mqtt.port)
                self.client.loop_start()
                self.valid = True
                logging.info(" => Connection success")
            except Exception:
                logging.error(
                    f"""
    Impossible de se connecter au serveur MQTT.

    Vous pouvez récupérer un exemple de configuration ici:
    {URL_CONFIG_FILE}
"""
                )

    def disconnect(self) -> None:
        """Disconnect from MQTT broker and cleanup resources."""
        if self.valid and hasattr(self, "client") and isinstance(self.client, mqtt.Client):
            try:
                logging.info("Disconnecting from MQTT broker")
                self.client.loop_stop()  # Stop the background thread
                self.client.disconnect()  # Close the connection
                self.valid = False
                logging.info(" => Disconnected successfully")
            except Exception as e:
                logging.warning(f"Error during MQTT disconnect: {e}")

    def __del__(self):
        """Destructor to ensure cleanup of MQTT resources."""
        self.disconnect()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.disconnect()
        return False  # Don't suppress exceptions

    def publish(self, topic, msg, prefix=None):
        """Publish one message."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if self.valid:
                if prefix is None:
                    prefix = APP_CONFIG.mqtt.prefix
                result = self.client.publish(
                    f"{APP_CONFIG.mqtt.prefix}/{prefix}/{topic}",
                    str(msg),
                    qos=APP_CONFIG.mqtt.qos,
                    retain=APP_CONFIG.mqtt.retain,
                )
                status = result[0]
                if status == 0:
                    logging.debug(f" MQTT Send : {prefix}/{topic} => {msg}")
                else:
                    logging.info(f" - Failed to send message to topic {prefix}/{topic}")

    def publish_multiple(self, data, prefix=None):
        """Public multiple message."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if self.valid:
                if data:
                    payload = []
                    if prefix is None:
                        prefix = APP_CONFIG.mqtt.prefix
                    else:
                        prefix = f"{prefix}"
                    for topics, value in data.items():
                        payload.append(
                            {
                                "topic": f"{prefix}/{topics}",
                                "payload": value,
                                "qos": APP_CONFIG.mqtt.qos,
                                "retain": APP_CONFIG.mqtt.retain,
                            }
                        )
                    username = None if not APP_CONFIG.mqtt.username else APP_CONFIG.mqtt.username
                    password = None if not APP_CONFIG.mqtt.password else APP_CONFIG.mqtt.password
                    if username is None and password is None:
                        auth = None
                    else:
                        auth = {"username": username, "password": password}
                    publish.multiple(
                        payload,
                        hostname=APP_CONFIG.mqtt.hostname,
                        port=APP_CONFIG.mqtt.port,
                        client_id=APP_CONFIG.mqtt.client_id,
                        auth=auth,
                    )
