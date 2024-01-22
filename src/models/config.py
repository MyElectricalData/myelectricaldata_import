import logging
import os
import re

import yaml

from dependencies import title, separator, APPLICATION_PATH_DATA


class Config:
    def __init__(self, path=APPLICATION_PATH_DATA):
        self.path = path
        self.db = None
        self.file = "config.yaml"
        self.path_file = f"{self.path}/{self.file}"
        self.config = {}
        self.default_port = 5000
        self.mandatory_parameters = {}
        #     "myelectricaldata": {
        #         "pdl": {
        #             "enable": True,
        #             "name": "",
        #             "token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
        #             "cache": True,
        #             "plan": "BASE",
        #             "consumption": True,
        #             "consumption_detail": True,
        #             "consumption_price_hc": 0,
        #             "consumption_price_hp": 0,
        #             "consumption_price_base": 0,
        #             "consumption_max_date": "",
        #             "consumption_detail_max_date": "",
        #             "production": False,
        #             "production_detail": False,
        #             "production_max_date": "",
        #             "production_detail_max_date": "",
        #             "production_price": 0,
        #             "offpeak_hours_0": '',
        #             "offpeak_hours_1": '',
        #             "offpeak_hours_2": '',
        #             "offpeak_hours_3": '',
        #             "offpeak_hours_4": '',
        #             "offpeak_hours_5": '',
        #             "offpeak_hours_6": '',
        #         }
        #     }
        # }
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
        self.db = db

    def load(self):
        config_file = f"{self.path_file}"
        if os.path.exists(config_file):
            with open(config_file) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

        else:
            f = open(config_file, "a")
            f.write(yaml.dump(self.default))
            f.close()
            with open(config_file) as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

        if self.config is None:
            return {
                "error": True,
                "message": [
                    "Impossible de charger le fichier de configuration.",
                    "",
                    "Vous pouvez récupérer un exemple ici :",
                    "https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file",
                ],
            }

    def check(self):
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
            else:
                if key not in self.config[config_name]:
                    self.config[config_name][key] = data

        # CHECK ENEDIS GATEWAY CONFIGURATION
        # if "myelectricaldata" not in self.config:
        #     lost_params.append("myelectricaldata")
        # else:
        #     if not isinstance(self.config["myelectricaldata"], dict):
        #         lost_params.append("myelectricaldata.PDL")
        #     else:
        #         for pdl, pdl_data in self.config["myelectricaldata"].items():
        #             if len(str(pdl)) != 14:
        #                 lost_params.append(f"PDL must be 14 characters ({pdl} => {len(str(pdl))})")
        #             if not isinstance(self.config["myelectricaldata"][pdl], dict):
        #                 lost_params.append(f"myelectricaldata.{pdl}.TOKEN")
        #             else:
        #                 for key, data in self.default['myelectricaldata']['pdl'].items():
        #                     mandatory = False
        #                     if key in self.mandatory_parameters:
        #                         mandatory = True
        #                     if mandatory and not key in self.config["myelectricaldata"][pdl]:
        #                         lost_params.append(f"myelectricaldata.{pdl}.{key.upper()}")
        #                     else:
        #                         if key not in self.config["myelectricaldata"][pdl]:
        #                             self.config["myelectricaldata"][pdl][key] = data

        if lost_params:
            msg = [
                "Some mandatory parameters are missing:",
            ]
            for param in lost_params:
                msg.append(f"- {param}")
            msg.append("")
            msg.append("You can get list of parameters here :")
            msg.append(f" => https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file")
            logging.critical(msg)
        else:
            title("Config valid")

        return lost_params

    def display(self):
        logging.info("Display configuration :")
        for key, value in self.config.items():
            if type(value) is dict:
                logging.info(f"  {key}:")
                for dic_key, dic_value in value.items():
                    if type(dic_value) is dict:
                        logging.info(f"    {dic_key}:")
                        for dic1_key, dic1_value in dic_value.items():
                            if dic1_key == "password" or dic1_key == "token":
                                dic1_value = "** hidden **"
                            if dic1_value is None or dic1_value == "None":
                                dic1_value = "''"
                            logging.info(f"      {dic1_key}: {dic1_value}")
                    else:
                        if dic_key == "password" or dic_key == "token":
                            dic_value = "** hidden **"
                        if dic_value is None or dic_value == "None":
                            dic_value = "''"
                        logging.info(f"    {dic_key}: {dic_value}")
            else:
                if key == "password" or key == "token":
                    value = "** hidden **"
                logging.info(f"  {key}: {value}")

    def get(self, path=None):
        if path:
            if path in self.config:
                return self.config[path]
            else:
                return False
        else:
            return self.config

    def set(self, path, value):
        title(f"Switch {path} to {value}")
        with open(f"{self.path_file}", "r+") as f:
            text = f.read()
            text = re.sub(rf"(?<={path}: ).*", str(value).lower(), text)
            f.seek(0)
            f.write(text)
            f.truncate()
        self.config = yaml.load(text, Loader=yaml.FullLoader)
        self.db.set_config(path, value)

    def tempo_config(self):
        if "tempo" in self.config:
            return self.config["tempo"]
        else:
            return False

    def storage_config(self):
        if "storage_uri" in self.config:
            return self.config["storage_uri"]
        else:
            return False

    def mqtt_config(self):
        if "mqtt" in self.config:
            return self.config["mqtt"]
        else:
            return False

    def home_assistant_config(self):
        if "home_assistant" in self.config:
            return self.config["home_assistant"]
        else:
            return False

    def home_assistant_ws_config(self):
        if "home_assistant_ws" in self.config:
            return self.config["home_assistant_ws"]
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

    def list_usage_point(self):
        return self.config["myelectricaldata"]

    def set_usage_point_config(self, usage_point_id, key, value):
        if "myelectricaldata" in self.config:
            if usage_point_id not in self.config["myelectricaldata"]:
                self.config["myelectricaldata"][usage_point_id] = {}
            if value is None or value == "None":
                value = ""
            self.config["myelectricaldata"][usage_point_id][key] = str(value)
            with open(self.path_file, "w") as outfile:
                yaml.dump(self.config, outfile, default_flow_style=False)
        else:
            return False

    def port(self):
        if "port" in self.config:
            return self.config["port"]
        else:
            return self.default_port

    def ssl_config(self):
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
                else:
                    logging.error("La configuration SSL est erronée.")
                    return {}
            else:
                logging.error("La configuration SSL est erronée.")
                return {}
        else:
            return {}

    def home_assistant_ws(self):
        if "home_assistant_ws" in self.config:
            return self.config["home_assistant_ws"]
        else:
            return None
