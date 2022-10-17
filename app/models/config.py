import os
import re

import yaml

import __main__ as app


def get_version():
    f = open("/app/VERSION", "r")
    version = f.read()
    f.close()
    return version


class Config:

    def __init__(self, path="/data"):
        self.path = path
        self.file = "config.yaml"
        self.path_file = f"{self.path}/{self.file}"
        self.config = {}
        self.mandatory_parameters = {
            "myelectricaldata": {
                "pdl": {
                    "token"
                }
            }
        }
        self.default = {
            "wipe_cache": False,
            "cycle": 3600,
            "debug": False,
            "myelectricaldata": {
                "pdl": {
                    "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
                    "cache": True,
                    "plan": "BASE",
                    "consumption": True,
                    "consumption_detail": True,
                    "consumption_price_hc": 0,
                    "consumption_price_hp": 0,
                    "consumption_price_base": 0,
                    "production": False,
                    "production_detail": False,
                    "offpeak_hours": None,
                    "refresh_contract": False,
                    "refresh_addresses": False
                }
            },
            "mqtt": {
                "enable": False,
                "host": "X.X.X.X",
                "port": 1883,
                "username": "",
                "password": "",
                "prefix": "myelectricaldata",
                "client_id": "myelectricaldata",
                "retain": True,
                "qos": 0
            },
            "home_assistant": {
                "enable": False,
                "discovery_prefix": "homeassistant",
                "card_myenedis": True
            },
            "influxdb": {
                "enable": False,
                "host": "influxdb",
                "port": 8086,
                "token": "XXXXXXXXXXX",
                "org": "myelectricaldata",
                "bucket": "myelectricaldata",
            }
        }

    def load(self):
        config_file = f'{self.path_file}'
        if os.path.exists(config_file):
            with open(f'{self.path}/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            f = open(config_file, "a")
            f.write(yaml.dump(self.default))
            f.close()
            with open(f'{self.path}/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

        if self.config is None:
            return {
                "error": True,
                "message": ["Impossible de charger le fichier de configuration.",
                            "",
                            "Vous pouvez récupérer un exemple ici :",
                            "https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file"
                            ]
            }

    def check(self):
        app.LOG.separator()
        app.LOG.log(f"Check {self.file} :")
        lost_params = []
        # CHECK HOME ASSISTANT CONFIGURATION
        config_name = "home_assistant"
        for key, data in self.default[config_name].items():
            mandatory = False
            if key in self.mandatory_parameters:
                mandatory = True
            if mandatory and key not in self.config[config_name]:
                lost_params.append(f"{config_name}.{key.upper()}")
            else:
                if key not in self.config[config_name]:
                    self.config[config_name][key] = data

        # CHECK ENEDIS GATEWAY CONFIGURATION
        if "myelectricaldata" not in self.config:
            lost_params.append("myelectricaldata")
        else:
            if not isinstance(self.config["myelectricaldata"], dict):
                lost_params.append("myelectricaldata.PDL")
            else:
                for pdl, pdl_data in self.config["myelectricaldata"].items():
                    if len(str(pdl)) != 14:
                        lost_params.append(f"PDL must be 14 characters ({pdl} => {len(str(pdl))})")
                    if not isinstance(self.config["myelectricaldata"][pdl], dict):
                        lost_params.append(f"myelectricaldata.{pdl}.TOKEN")
                    else:
                        for key, data in self.default['myelectricaldata']['pdl'].items():
                            mandatory = False
                            if key in self.mandatory_parameters:
                                mandatory = True
                            if mandatory and not key in self.config["myelectricaldata"][pdl]:
                                lost_params.append(f"myelectricaldata.{pdl}.{key.upper()}")
                            else:
                                if key not in self.config["myelectricaldata"][pdl]:
                                    self.config["myelectricaldata"][pdl][key] = data

        if lost_params:
            msg = [
                "Some mandatory parameters are missing:",
            ]
            for param in lost_params:
                msg.append(f'- {param}')
            msg.append("")
            msg.append("You can get list of parameters here :")
            msg.append(f" => https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file")
            app.LOG.critical(msg)
        else:
            app.LOG.log(" => Config valid")

        return lost_params

    def display(self):
        app.LOG.log("Display configuration :")
        for key, value in self.config.items():
            if type(value) is dict:
                app.LOG.log(f"  {key}:")
                for dic_key, dic_value in value.items():
                    if type(dic_value) is dict:
                        app.LOG.log(f"    {dic_key}:")
                        for dic1_key, dic1_value in dic_value.items():
                            if dic1_key == "password" or dic1_key == "token":
                                dic1_value = "** hidden **"
                            app.LOG.log(f"      {dic1_key}: {dic1_value}")
                    else:
                        if dic_key == "password" or dic_key == "token":
                            dic_value = "** hidden **"
                        app.LOG.log(f"    {dic_key}: {dic_value}")
            else:
                if key == "password" or key == "token":
                    value = "** hidden **"
                app.LOG.log(f"  {key}: {value}")

    def get(self, path=None):
        if path:
            if path in self.config:
                return self.config[path]
            else:
                return False
        else:
            return self.config

    def set(self, path, value):
        app.LOG.log(f" => Switch {path} to {value}")
        with open(f'{self.path_file}', 'r+') as f:
            text = f.read()
            text = re.sub(fr'(?<={path}: ).*', str(value).lower(), text)
            f.seek(0)
            f.write(text)
            f.truncate()
        self.config = yaml.load(text, Loader=yaml.FullLoader)

    def mqtt_config(self):
        if "mqtt" in self.config:
            return self.config["mqtt"]
        else:
            return False

    def influxdb_config(self):
        if "influxdb" in self.config:
            return self.config["influxdb"]
        else:
            return False

    def usage_point_id_config(self, usage_point_id):
        if "myelectricaldata" in self.config and usage_point_id in self.config["myelectricaldata"]:
            return self.config["myelectricaldata"][usage_point_id]
        else:
            return False
