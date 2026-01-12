"""Configuration class loader and checker."""

import locale
import logging
import sys
from os import getenv
from typing import List

from deepdiff import DeepDiff
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import Resource, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from __version__ import VERSION
from config.backend import Backend
from config.gateway import Gateway
from config.home_assistant import HomeAssistant
from config.home_assistant_ws import HomeAssistantWs
from config.influxdb import InfluxDB
from config.log import Logging
from config.mqtt import MQTT
from config.myelectricaldata import MyElectricalData, UsagePointId
from config.optel import OpTel
from config.server import Server
from const import URL_CONFIG_FILE
from database.usage_points import DatabaseUsagePoints
from utils import barcode_message, edit_config, load_config, logo, str2bool, title

try:
    locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "")  # Use system default
    except locale.Error:
        locale.setlocale(locale.LC_ALL, "C")  # Last resort


class Configuration:
    """Configuration Templates."""

    def __init__(self) -> None:
        self.dev = str2bool(getenv("DEV", "False"))

        file_config = load_config()
        self.application_path = file_config.application_path
        self.application_path_data = file_config.application_path_data
        self.application_path_log = file_config.application_path_log
        self.config_file = file_config.config_file
        self.config = file_config.config

        # Load config
        self.opentelemetry: OpTel = OpTel(self.config)
        self.logging: Logging = Logging(self.config)
        self.myelectricaldata: MyElectricalData = MyElectricalData(self.config)
        self.influxdb: InfluxDB = InfluxDB(self.config)
        self.home_assistant_ws: HomeAssistantWs = HomeAssistantWs(self.config)
        self.home_assistant: HomeAssistant = HomeAssistant(self.config)
        self.mqtt: MQTT = MQTT(self.config)
        self.gateway: Gateway = Gateway(self.config)
        self.backend: Backend = Backend(self.config)
        self.server: Server = Server(self.config)


class Config:
    """Represent the configuration settings for the application."""

    def __init__(self):
        self.config = Configuration()
        self.default = {}

        # SHORTCUT
        self.application_path = self.config.application_path
        self.application_path_data = self.config.application_path_data
        self.application_path_log = self.config.application_path_log
        self.config_file = self.config.config_file
        self.application_path = self.config.application_path
        self.dev = self.config.dev
        self.opentelemetry = self.config.opentelemetry
        self.logging = self.config.logging
        self.myelectricaldata = self.config.myelectricaldata
        self.influxdb = self.config.influxdb
        self.home_assistant_ws = self.config.home_assistant_ws
        self.home_assistant = self.config.home_assistant
        self.mqtt = self.config.mqtt
        self.gateway = self.config.gateway
        self.backend = self.config.backend
        self.server = self.config.server

        # ENVIRONMENT VARIABLE
        self.debug = str2bool(getenv("DEBUG", "False"))

        self.tracer = None
        self.load_logging()
        self.setup_tracing()
        logo(VERSION)

        comments = None
        for key in self.config.config:
            attr = getattr(self.config, key, None)
            if attr is not None and getattr(attr, "__dict__", False):
                comments = attr.__dict__["comments"] if "comments" in attr.__dict__ else None
                self.default[key] = attr.default()

        self.check_config()
        if self.dev:
            barcode_message("DEV MODE")
            exemple_file = "config.example.yaml"
            edit_config(data=self.default, file=exemple_file, comments=comments, wipe=True)
            edit_config(
                data=self.default,
                file=f"{self.application_path}/templates/{exemple_file}",
                comments=comments,
                wipe=True,
            )
            title([f"Generate {exemple_file}", f" => {exemple_file} generated"])
        self.display()
        self.clean_database()

    def clean_database(self):
        """Clean database."""
        title("Nettoyage de la base de données...")
        usage_point_list: List[UsagePointId] = []
        if self.myelectricaldata.usage_point_config is not None:
            for upi, _ in self.myelectricaldata.usage_point_config.items():
                usage_point_list.append(upi)
        for usage_point in DatabaseUsagePoints().get_all():
            if usage_point.usage_point_id not in usage_point_list:
                DatabaseUsagePoints(usage_point.usage_point_id).delete()

    def check_config(self):
        """Check current config file."""
        # CHECK CLASSIC KEYS
        diff_config = DeepDiff(self.default, self.config.config, ignore_order=True, exclude_paths=["myelectricaldata"])
        found = ""
        for diff in diff_config.get("dictionary_item_added", {}):
            found += f"\n - {str(diff.replace('root', '')[2:-2]).replace("']['", '.')}"

        # CHECK MYELETRICALDATA KEYS
        for usage_point_id, data in self.config.config["myelectricaldata"].items():
            usage_point_default = UsagePointId(self.config, usage_point_id, False).default()
            diff_config = DeepDiff(usage_point_default, data, ignore_order=True)
            for diff in diff_config.get("dictionary_item_added", {}):
                key = str(diff.replace("root", "")[2:-2]).replace("']['", ".")
                found += f"\n - myelectricaldata.{usage_point_id}.{key}"
        if found:
            logging.critical(f"\nDes valeurs inutiles ont étaient détectées dans le fichier de configuration :{found}")
            logging.critical(
                f"""
    Impossible de charger le fichier de configuration.

    Vous pouvez récupérer un exemple de configuration ici:
    {URL_CONFIG_FILE}
"""
            )
            sys.exit(1)

    def load_logging(self):
        """Configure logging."""

        class NewLineFormatter(logging.Formatter):
            """Split carrier return in multiple messages."""

            def __init__(self, fmt, datefmt=None):
                """Init given the log line format and date format."""
                logging.Formatter.__init__(self, fmt, datefmt)

            def format(self, record):
                """Override format function."""
                msg = logging.Formatter.format(self, record)

                if record.message != "":
                    parts = msg.split(record.message)
                    msg = msg.replace("\n", "\n" + parts[0])

                return msg

        root_logger = logging.getLogger()
        if len(root_logger.handlers) > 0:
            root_logger.removeHandler(root_logger.handlers[0])

        if self.config.logging.log2file:
            logging.basicConfig(
                filename=f"{self.config.application_path_log}/myelectricaldata.log",
                format=self.config.logging.log_format,
                datefmt=self.config.logging.log_format_date,
                level=self.config.logging.log_level,
            )
            console = logging.StreamHandler()
            console.setLevel(self.config.logging.log_level)
            formatter = logging.Formatter(self.config.logging.log_format, datefmt=self.config.logging.log_format_date)
            console.setFormatter(formatter)
            logging.getLogger("").addHandler(console)
        else:
            logging.basicConfig(
                format=self.config.logging.log_format,
                datefmt=self.config.logging.log_format_date,
                level=self.config.logging.log_level,
            )
            formatter = NewLineFormatter(self.config.logging.log_format, datefmt=self.config.logging.log_format_date)
            lg = logging.getLogger()
            lg.handlers[0].setFormatter(formatter)
            lg.setLevel(self.config.logging.log_level)

        if self.config.logging.debug:
            logging.debug("   => Starting in Debug mode : %s", self.config.logging.debug)

    def display(self):
        """Display the configuration settings.

        This method logs the configuration settings to the console, hiding sensitive information such as passwords
        and tokens.

        Args:
            None

        Returns:
            None
        """

        def message(key, value="", indent=4):
            """Hidden password."""
            value = value if key not in ["token", "password"] else "** hidden **"
            logging.info("%s| %s: %s", " " * indent, key, value)

        logging.info("Affichage de la configuration :")
        for key, value in self.config.config.items():
            title_key = key.replace("_", " ").capitalize()
            if not isinstance(value, dict):
                logging.info(f"* {title_key}: {value}")
            else:
                logging.info(f"* {title_key}:")
                for sub_key, sub_value in value.items():
                    if not isinstance(sub_value, dict):
                        message(sub_key, sub_value)
                    else:
                        message(sub_key)
                        for sub_sub_key, sub_sub_value in sub_value.items():
                            message(sub_sub_key, sub_sub_value, 8)

    def usage_point_id_config(self, usage_point_id) -> UsagePointId:
        """Return the configuration for a specific usage point.

        Args:
            usage_point_id (str): The ID of the usage point.

        Returns:
            dict: A dictionary containing the configuration for the specified usage point.
        """
        if usage_point_id in self.config.myelectricaldata.usage_point_config:
            return self.config.myelectricaldata.usage_point_config[usage_point_id]
        return False

    def set_usage_point_config(self, usage_point_id, key, value):
        """Set the configuration for a specific usage point.

        Args:
            usage_point_id (str): The ID of the usage point.
            key (str): The configuration key.
            value (str): The configuration value.
        """
        if usage_point_id not in self.config.myelectricaldata.usage_point_config:
            setattr(self.config.myelectricaldata.usage_point_config[usage_point_id], key, value)
        else:
            logging.error("Usage point ID not found in configuration")

    def ssl_config(self):
        """Return the SSL configuration if it exists, otherwise returns an empty dictionary."""
        if self.config.server.keyfile is not None and self.config.server.certfile is not None:
            return {
                "ssl_keyfile": self.config.server.keyfile,
                "ssl_certfile": self.config.server.certfile,
            }
        return {}

    def setup_tracing(self):
        """OTEL setup."""
        if self.config.opentelemetry.enable:  # no pragma: no cover
            RequestsInstrumentor().instrument()
            resource_attributes = {
                "service.name": self.config.opentelemetry.service_name,
                "telemetry.version": VERSION,
                "service.version": VERSION,
                "env": self.config.opentelemetry.environment,
                "Deployment.environment": self.config.opentelemetry.environment,
            }
            resource = Resource.create(resource_attributes)
            provider = TracerProvider(resource=resource)
            processor = BatchSpanProcessor(
                OTLPSpanExporter(endpoint=self.config.opentelemetry.endpoint, insecure=True),
                export_timeout_millis=5,
            )
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
        else:
            trace.set_tracer_provider(trace.NoOpTracerProvider())
        self.tracer = trace.get_tracer_provider().get_tracer("main")
        self.tracing_sqlalchemy()

    def tracing_sqlalchemy(self):
        """SQLAchemy Tracing."""
        if self.config.opentelemetry.enable and "sqlalchemy" in self.config.opentelemetry.extension:
            logging.debug("[OpenTelemetry] SQLAchemy loaded")
            SQLAlchemyInstrumentor().instrument(enable_commenter=True, commenter_options={})

    def tracing_fastapi(self, app):
        """FastAPI Tracing."""
        if self.config.opentelemetry.enable and "fastapi" in self.config.opentelemetry.extension:
            logging.debug("[OpenTelemetry] FastAPI loaded")
            FastAPIInstrumentor.instrument_app(app)


if __name__ == "config.main":
    APP_CONFIG = Config()
