"""Configuration class loader and checker."""

import logging
import re
from pathlib import Path

import yaml

from dependencies import APPLICATION_PATH_DATA, is_bool, is_float, separator, str2bool, title


class Config:
    """Represent the configuration settings for the application.

    Attributes:
        path (str): The path to the configuration file.
        db: The database connection object.
        file (str): The name of the configuration file.
        path_file (str): The full path to the configuration file.
        config (dict): The loaded configuration settings.
        default_port (int): The default port number.
        mandatory_parameters (dict): The mandatory parameters for the configuration.
        default (dict): The default configuration settings.
    """

    def __init__(self, path=APPLICATION_PATH_DATA):
        self.path = path
        self.db = None
        self.file = "config.yaml"
        self.path_file = f"{self.path}/{self.file}"
        self.config = {}
        self.default_port = 5000
        self.mandatory_parameters = {}
        self.default = {
            "cycle": 14400,
            "debug": False,
            "log2file": False,
            "tempo": {
                "enable": False,
            },
            "myelectricaldata": {
                "pdl": {
                    "enable": True,
                    "name": "",
                    "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    "cache": True,
                    "plan": "BASE",
                    "consumption": True,
                    "consumption_detail": True,
                    "consumption_price_hc": 0,
                    "consumption_price_hp": 0,
                    "consumption_price_base": 0,
                    "consumption_max_date": "",
                    "consumption_detail_max_date": "",
                    "production": False,
                    "production_detail": False,
                    "production_max_date": "",
                    "production_detail_max_date": "",
                    "production_price": 0,
                    "offpeak_hours_0": "",
                    "offpeak_hours_1": "",
                    "offpeak_hours_2": "",
                    "offpeak_hours_3": "",
                    "offpeak_hours_4": "",
                    "offpeak_hours_5": "",
                    "offpeak_hours_6": "",
                    "activation_date_daily": "",
                    "activation_date_detail": "",
                    "refresh_addresse": False,
                    "refresh_contract": False,
                }
            },
            "mqtt": {
                "enable": False,
                "hostname": "X.X.X.X",
                "port": 1883,
                "username": "",
                "password": "",
                "prefix": "myelectricaldata",
                "client_id": "myelectricaldata",
                "retain": True,
                "qos": 0,
            },
            "home_assistant": {
                "enable": False,
                "discovery_prefix": "homeassistant",
            },
            "home_assistant_ws": {"enable": False, "ssl": True, "token": "", "url": ""},
            "influxdb": {
                "enable": False,
                "hostname": "influxdb",
                "port": 8086,
                "token": "XXXXXXXXXXX",
                "org": "myelectricaldata",
                "bucket": "myelectricaldata",
                "method": "synchronous",
            },
            "ssl": {
                "gateway": True,
                "certfile": None,
                "keyfile": None,
            },
        }

    def set_db(self, db):
        """Set the database."""
        self.db = db

    def load(self):
        """Load the configuration."""
        config_file = f"{self.path_file}"
        if Path(config_file).exists():
            with Path(config_file).open(encoding="utf-8") as file:
                self.config = yaml.safe_load(file)

        else:
            with Path(config_file).open(mode="a", encoding="utf-8") as file:
                file.write(yaml.dump(self.default))
            with Path(config_file).open(encoding="utf-8") as file:
                self.config = yaml.safe_load(file)

        if self.config is None:
            return {
                "error": True,
                "message": [
                    "Impossible de charger le fichier de configuration.",
                    "",
                    "Vous pouvez récupérer un exemple ici :",
                    "https://github.com/MyElectricalData/myelectricaldata_import/wiki/03.-Configuration",
                ],
            }

    def check(self):
        """Check the configuration for missing mandatory parameters."""
        separator()
        logging.info(f"Check {self.file} :")
        lost_params = []
        # CHECK HOME ASSISTANT CONFIGURATION
        config_name = "home_assistant"
        for key, data in self.default[config_name].items():
            mandatory = False
            if key in self.mandatory_parameters:
                mandatory = True
            if mandatory and key not in self.config[config_name]:
                lost_params.append(f"{config_name}.{key.upper()}")
            elif key not in self.config[config_name]:
                self.config[config_name][key] = data

        if lost_params:
            msg = [
                "Some mandatory parameters are missing:",
            ]
            for param in lost_params:
                msg.append(f"- {param}")
            msg.append("")
            msg.append("You can get list of parameters here :")
            msg.append(" => https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file")
            logging.critical(msg)
        else:
            title("Config valid")

        return lost_params

    def display(self):
        """Display the configuration settings.

        This method logs the configuration settings to the console, hiding sensitive information such as passwords
        and tokens.

        Args:
            None

        Returns:
            None
        """
        logging.info("Display configuration :")
        for key, value in self.config.items():
            if isinstance(value, dict):
                logging.info(f"  {key}:")
                for dic_key, dic_value in value.items():
                    if isinstance(dic_value, dict):
                        logging.info(f"    {dic_key}:")
                        for dic1_key, dic1_value in dic_value.items():
                            if dic1_key in {"password", "token"}:
                                hidden_value = "** hidden **"
                            else:
                                hidden_value = dic1_value
                            if hidden_value is None or hidden_value == "None":
                                hidden_value = "''"
                            logging.info(f"      {dic1_key}: {hidden_value}")
                    else:
                        if dic_key in {"password", "token"}:
                            hidden_value = "** hidden **"
                        else:
                            hidden_value = dic_value
                        if hidden_value is None or hidden_value == "None":
                            hidden_value = "''"
                        logging.info(f"    {dic_key}: {hidden_value}")
            else:
                if key in {"password", "token"}:
                    hidden_value = "** hidden **"
                else:
                    hidden_value = value
                logging.info(f"  {key}: {hidden_value}")

    def get(self, path=None):
        """Get the value of a configuration parameter.

        Args:
            path (str, optional): The path of the configuration parameter. Defaults to None.

        Returns:
            Union[bool, Any]: The value of the configuration parameter if found, False otherwise.
        """
        if path:
            if path in self.config:
                return self.config[path]
            return False
        return self.config

    def set(self, path, value):
        """Set the value of a configuration parameter.

        Args:
            path (str): The path of the configuration parameter.
            value: The value to set.

        Returns:
            None
        """
        title(f"Switch {path} to {value}")
        with Path(self.path_file).open(mode="r+", encoding="utf-8") as file:
            text = file.read()
            text = re.sub(rf"(?<={path}: ).*", str(value).lower(), text)
            file.seek(0)
            file.write(text)
            file.truncate()
        self.config = yaml.safe_load(text)
        self.db.set_config(path, value)

    def tempo_config(self):
        """Return the configuration for tempo.

        Returns:
            dict: A dictionary containing the tempo configuration.
        """
        if "tempo" in self.config:
            return self.config["tempo"]
        return False

    def storage_config(self):
        """Return the configuration for storage.

        Returns:
            str: The storage URI.
        """
        if "storage_uri" in self.config:
            return self.config["storage_uri"]
        return False

    def mqtt_config(self):
        """Return the configuration for MQTT.

        Returns:
            dict: A dictionary containing the MQTT configuration.
        """
        if "mqtt" in self.config:
            return self.config["mqtt"]
        return False

    def home_assistant_config(self):
        """Return the configuration for Home Assistant.

        Returns:
            dict: A dictionary containing the Home Assistant configuration.
        """
        if "home_assistant" in self.config:
            return self.config["home_assistant"]
        return False

    def home_assistant_ws_config(self):
        """Return the configuration for Home Assistant WebSocket.

        Returns:
            dict: A dictionary containing the Home Assistant WebSocket configuration.
        """
        if "home_assistant_ws" in self.config:
            return self.config["home_assistant_ws"]
        return False

    def influxdb_config(self):
        """Return the configuration for InfluxDB.

        Returns:
            dict: A dictionary containing the InfluxDB configuration.
        """
        if "influxdb" in self.config:
            return self.config["influxdb"]
        return False

    def usage_point_id_config(self, usage_point_id):
        """Return the configuration for a specific usage point.

        Args:
            usage_point_id (str): The ID of the usage point.

        Returns:
            dict: A dictionary containing the configuration for the specified usage point.
        """
        if "myelectricaldata" in self.config and usage_point_id in self.config["myelectricaldata"]:
            return self.config["myelectricaldata"][usage_point_id]
        return False

    def list_usage_point(self):
        """Return the list of usage points in the configuration.

        Returns:
            dict: A dictionary containing the usage points.
        """
        return self.config["myelectricaldata"]

    def set_usage_point_config(self, usage_point_id, key, value):
        """Set the configuration for a specific usage point.

        Args:
            usage_point_id (str): The ID of the usage point.
            key (str): The configuration key.
            value (str): The configuration value.
        """
        if "myelectricaldata" in self.config:
            if usage_point_id not in self.config["myelectricaldata"]:
                self.config["myelectricaldata"][usage_point_id] = {}
            if is_bool(value):
                value = str2bool(value)
            elif value is None or value == "None":
                value = ""
            elif is_float(value):
                value = float(value)
            else:
                value = str(value)
            self.config["myelectricaldata"][usage_point_id][key] = value
            with Path(self.path_file).open(mode="w", encoding="utf-8") as outfile:
                yaml.dump(self.config, outfile, default_flow_style=False)
        else:
            return False

    def port(self):
        """Return the port configuration if it exists, otherwise returns the default port."""
        if "port" in self.config:
            return self.config["port"]
        return self.default_port

    def ssl_config(self):
        """Return the SSL configuration if it exists, otherwise returns an empty dictionary."""
        if "ssl" in self.config:
            if "keyfile" in self.config["ssl"] and "certfile" in self.config["ssl"]:
                if (
                    self.config["ssl"]["keyfile"] != ""
                    and self.config["ssl"]["keyfile"] is not None
                    and self.config["ssl"]["certfile"] != ""
                    and self.config["ssl"]["certfile"] is not None
                ):
                    return {
                        "ssl_keyfile": self.config["ssl"]["keyfile"],
                        "ssl_certfile": self.config["ssl"]["certfile"],
                    }
                logging.error("La configuration SSL est erronée.")
                return {}
            logging.error("La configuration SSL est erronée.")
            return {}
        return {}
