"""Manage Config table in database."""

import json
import logging

from sqlalchemy import select

from database import DB
from database.usage_points import DatabaseUsagePoints
from db_schema import Config as ConfigTable
from dependencies import title
from models.config import Config


class DatabaseConfig:
    """Manage configuration for the database."""

    def __init__(self):
        """Initialize DatabaseConfig."""
        self.session = DB.session
        self.config = Config()

    def load_config_file(self):
        """Load the database configuration and clean the database."""
        title("Chargement du config.yaml...")
        logging.info(" - Home Assistant")
        if self.config.home_assistant_config() is not None:
            self.set("home_assistant", self.config.home_assistant_config())
            logging.info("    => Success")
        else:
            logging.warning("Aucune configuration Home Assistant détectée.")
        logging.info(" - Home Assistant Websocket")
        if self.config.home_assistant_ws_config() is not None:
            self.set("home_assistant_ws", self.config.home_assistant_ws_config())
            logging.info("    => Success")
        else:
            logging.warning("Aucune configuration Home Assistant Websocket détectée.")
        logging.info(" - InfluxDB")
        if self.config.influxdb_config() is not None:
            self.set("influxdb", self.config.influxdb_config())
            logging.info("    => Success")
        else:
            logging.warning("Aucune configuration InfluxDB détectée.")
        logging.info(" - MQTT")
        if self.config.mqtt_config() is not None:
            self.set("mqtt", self.config.mqtt_config())
            logging.info("    => Success")
        else:
            logging.warning("Aucune configuration MQTT détectée.")
        logging.info(" - Point de livraison")
        usage_point_list = []
        if self.config.list_usage_point() is not None:
            for upi, upi_data in self.config.list_usage_point().items():
                logging.info(f"   {upi}")
                DatabaseUsagePoints(upi).set(upi_data)
                usage_point_list.append(upi)
                logging.info("    => Success")
        else:
            logging.warning("Aucun point de livraison détecté.")

    def get(self, key):
        """Get data from config table."""
        query = select(ConfigTable).where(ConfigTable.key == key)
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set(self, key, value):
        """Set data from config table."""
        query = select(ConfigTable).where(ConfigTable.key == key)
        config = self.session.scalars(query).one_or_none()
        if config:
            config.value = json.dumps(value)
        else:
            self.session.add(ConfigTable(key=key, value=json.dumps(value)))
        self.session.flush()
        self.session.close()
        DB.refresh_object()
