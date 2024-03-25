"""Initialisation of the application."""

import locale
import logging
import sys
import time
import typing as t
from os import environ, getenv
from pathlib import Path

import yaml

from config import LOG_FORMAT, LOG_FORMAT_DATE, cycle_minimun
from database.config import DatabaseConfig
from dependencies import APPLICATION_PATH_DATA, APPLICATION_PATH_LOG, str2bool
from models.config import Config
from models.influxdb import InfluxDB
from models.mqtt import Mqtt

# LOGGING CONFIGURATION
config = {}
CONFIG_PATH = Path(APPLICATION_PATH_DATA) / "config.yaml"
if Path(CONFIG_PATH).exists():
    with Path(CONFIG_PATH).open() as file:
        config = yaml.safe_load(file)

root_logger = logging.getLogger()
if len(root_logger.handlers) > 0:
    root_logger.removeHandler(root_logger.handlers[0])

if "DEBUG" in environ and str2bool(getenv("DEBUG")):
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

if config.get("log2file"):
    logging.basicConfig(
        filename=f"{APPLICATION_PATH_LOG}/myelectricaldata.log",
        format=LOG_FORMAT,
        datefmt=LOG_FORMAT_DATE,
        level=logging_level,
    )
    console = logging.StreamHandler()
    console.setLevel(logging_level)
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_FORMAT_DATE)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
else:
    logging.basicConfig(format=LOG_FORMAT, datefmt=LOG_FORMAT_DATE, level=logging_level)

# # Clear the default handler
# root_logger = logging.getLogger()
# if len(root_logger.handlers) > 0:
#     # remove the first handler
#     root_logger.removeHandler(root_logger.handlers[0])

if not Path(CONFIG_PATH).exists():
    logging.critical(f"Config file is not found ({CONFIG_PATH})")
    sys.exit()


class EndpointFilter(logging.Filter):
    """Filter class for filtering log records based on the path."""

    def __init__(
        self,
        path: str,
        *args: t.Any,
        **kwargs: t.Any,
    ):
        super().__init__(*args, **kwargs)
        self._path = path

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records based on the path."""
        return record.getMessage().find(self._path) == -1


uvicorn_logger = logging.getLogger("uvicorn.access")
uvicorn_logger.addFilter(EndpointFilter(path="/import_status"))

locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

MINIMUN_CYCLE = cycle_minimun

CONFIG = Config()
CONFIG.load()
CONFIG.display()
CONFIG.check()

DatabaseConfig().load_config_file()

INFLUXB_ENABLE = False
INFLUXDB = None
INFLUXDB_CONFIG = CONFIG.influxdb_config()
if INFLUXDB_CONFIG and "enable" in INFLUXDB_CONFIG and str2bool(INFLUXDB_CONFIG["enable"]):
    INFLUXB_ENABLE = True
    if "method" in INFLUXDB_CONFIG:
        method = INFLUXDB_CONFIG["method"]
    else:
        method = "SYNCHRONOUS"

    if "scheme" not in INFLUXDB_CONFIG:
        INFLUXDB_CONFIG["scheme"] = "http"

    write_options = []
    if "batching_options" in INFLUXDB_CONFIG:
        write_options = INFLUXDB_CONFIG["batching_options"]
    INFLUXDB = InfluxDB()
    if CONFIG.get("wipe_influxdb"):
        INFLUXDB.purge_influxdb()
        CONFIG.set("wipe_influxdb", False)
        time.sleep(1)

MQTT_ENABLE = False
MQTT = None
MQTT_CONFIG = CONFIG.mqtt_config()
if MQTT_CONFIG and "enable" in MQTT_CONFIG and str2bool(MQTT_CONFIG["enable"]):
    MQTT_ENABLE = True
    MQTT = Mqtt(
        hostname=MQTT_CONFIG["hostname"],
        port=MQTT_CONFIG["port"],
        username=MQTT_CONFIG["username"],
        password=MQTT_CONFIG["password"],
        client_id=MQTT_CONFIG["client_id"],
        prefix=MQTT_CONFIG["prefix"],
        retain=MQTT_CONFIG["retain"],
        qos=MQTT_CONFIG["qos"],
        ca_cert=MQTT_CONFIG.get("ca_cert"),
    )
