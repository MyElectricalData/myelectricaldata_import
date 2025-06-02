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
from dependencies import APPLICATION_PATH_DATA, APPLICATION_PATH_LOG, str2bool
from models.config import Config
from models.database import Database
from models.influxdb import InfluxDB
from models.mqtt import Mqtt

# LOGGING CONFIGURATION
config = {}
CONFIG_PATH = Path(APPLICATION_PATH_DATA) / "config.yaml"
if Path(CONFIG_PATH).exists():
    with Path(CONFIG_PATH).open() as file:
        config = yaml.safe_load(file)

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

CONFIG = Config(path=APPLICATION_PATH_DATA)
CONFIG.load()
CONFIG.display()
CONFIG.check()

DB = Database(CONFIG)
DB.init_database()
DB.unlock()

CONFIG.set_db(DB)

INFLUXB_ENABLE = False
INFLUXDB = None
INFLUXDB_CONFIG = CONFIG.influxdb_config()
if INFLUXDB_CONFIG and "enable" in INFLUXDB_CONFIG and str2bool(INFLUXDB_CONFIG["enable"]):
    INFLUXB_ENABLE = True
    method = INFLUXDB_CONFIG.get("method", "SYNCHRONOUS")
    scheme = INFLUXDB_CONFIG.get("scheme", "http")
    write_options = INFLUXDB_CONFIG.get("batching_options", {})
    vm_mode = str2bool(INFLUXDB_CONFIG.get("vm_mode", False))

    logging.info(f"Connexion à la base de données : {scheme}://{INFLUXDB_CONFIG['hostname']}:{INFLUXDB_CONFIG['port']} (vm_mode={vm_mode})")

    INFLUXDB = InfluxDB(
        scheme=scheme,
        hostname=INFLUXDB_CONFIG["hostname"],
        port=INFLUXDB_CONFIG["port"],
        token=INFLUXDB_CONFIG["token"],
        org=INFLUXDB_CONFIG["org"],
        bucket=INFLUXDB_CONFIG["bucket"],
        method=method,
        write_options=write_options,
        vm_mode=vm_mode  # <-- ✅ Ajout important
    )

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
    )"""Initialisation of the application."""

import locale
import logging
import sys
import time
import typing as t
from os import environ, getenv
from pathlib import Path

import yaml

from config import LOG_FORMAT, LOG_FORMAT_DATE, cycle_minimun
from dependencies import APPLICATION_PATH_DATA, APPLICATION_PATH_LOG, str2bool
from models.config import Config
from models.database import Database
from models.influxdb import InfluxDB
from models.mqtt import Mqtt

# LOGGING CONFIGURATION
config = {}
CONFIG_PATH = Path(APPLICATION_PATH_DATA) / "config.yaml"
if Path(CONFIG_PATH).exists():
    with Path(CONFIG_PATH).open() as file:
        config = yaml.safe_load(file)

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

CONFIG = Config(path=APPLICATION_PATH_DATA)
CONFIG.load()
CONFIG.display()
CONFIG.check()

DB = Database(CONFIG)
DB.init_database()
DB.unlock()

CONFIG.set_db(DB)

INFLUXB_ENABLE = False
INFLUXDB = None
INFLUXDB_CONFIG = CONFIG.influxdb_config()
if INFLUXDB_CONFIG and "enable" in INFLUXDB_CONFIG and str2bool(INFLUXDB_CONFIG["enable"]):
    INFLUXB_ENABLE = True
    method = INFLUXDB_CONFIG.get("method", "SYNCHRONOUS")
    scheme = INFLUXDB_CONFIG.get("scheme", "http")
    write_options = INFLUXDB_CONFIG.get("batching_options", {})
    vm_mode = str2bool(INFLUXDB_CONFIG.get("vm_mode", False))

    logging.info(f"Connexion à la base de données : {scheme}://{INFLUXDB_CONFIG['hostname']}:{INFLUXDB_CONFIG['port']} (vm_mode={vm_mode})")

    INFLUXDB = InfluxDB(
        scheme=scheme,
        hostname=INFLUXDB_CONFIG["hostname"],
        port=INFLUXDB_CONFIG["port"],
        token=INFLUXDB_CONFIG["token"],
        org=INFLUXDB_CONFIG["org"],
        bucket=INFLUXDB_CONFIG["bucket"],
        method=method,
        write_options=write_options,
        vm_mode=vm_mode  # <-- ✅ Ajout important
    )

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
