import os

import yaml
import json

from models.log import log


class Config:

    def __init__(self, path="/data"):
        self.path = path
        self.config = {}
        self.mandatory_parameters = {
            "myelectricaldata": {
                "pdl": {
                    "token"
                }
            }
        }
        self.default = {
            "wipe_local_cache": False,
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
                "enable": True,
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
                "card_myenedis": False
            }
        }

    def load(self):
        config_file = f'{self.path}/config.yaml'
        if os.path.exists(config_file):
            with open(f'{self.path}/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            f = open(config_file, "a")
            f.write(yaml.dump(self.default))
            f.close()
            with open(f'{self.path}/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

    def check(self):
        lost_params = []
        # CHECK GLOBAL CONFIGURATION
        for key, data in self.default.items():
            isDict = False
            if isinstance(self.default[key], dict):
                isDict = True
            name = key
            mandatory = False
            if key in self.mandatory_parameters:
                mandatory = True
                name = key
            if mandatory and name not in self.config:
                lost_params.append(name.upper())
            elif not isDict:
                if name not in self.config:
                    self.config[name] = data

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

    def display(self):
        log("Display configuration :")
        for key, value in self.config.items():
            if type(value) is dict:
                log(f"  {key}:")
                for dic_key, dic_value in value.items():
                    if type(dic_value) is dict:
                        log(f"    {dic_key}:")
                        for dic1_key, dic1_value in dic_value.items():
                            log(f"      {dic1_key}: {dic1_value}")
                    else:
                        log(f"    {dic_key}: {dic_value}")
            else:
                log(f"  {key}: {value}")

    def get(self, path=None):
        if path:
            return self.config[path]
        else:
            return self.config


if "APPLICATION_PATH_DATA" in os.environ:
    APPLICATION_PATH_DATA = os.getenv("APPLICATION_PATH_DATA")
else:
    APPLICATION_PATH_DATA = "/data"
config = Config(
    path=APPLICATION_PATH_DATA
)

config.load()
config.check()
