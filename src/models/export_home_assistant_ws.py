"""Import data in statistique recorder of Home Assistant."""

import json
import logging
import ssl
import traceback
from datetime import datetime, timedelta

import pytz
import websocket

from dependencies import chunks_list, is_integer, str2bool, truncate
from init import CONFIG, DB
from models.export_home_assistant import HomeAssistant
from models.stat import Stat

TZ_PARIS = pytz.timezone("Europe/Paris")


class HomeAssistantWs:
    """Class to interact with Home Assistant WebSocket API."""

    def __init__(self, usage_point_id):
        """Initialize the class with the usage point id.

        Args:
            usage_point_id (str): The usage point id
        """
        self.websocket = None
        self.usage_point_id = usage_point_id
        self.usage_point_id_config = DB.get_usage_point(self.usage_point_id)
        self.config = None
        self.url = None
        self.ssl = None
        self.token = None
        self.id = 1
        self.purge = False
        self.purge_force = True
        self.batch_size = 1000
        self.current_stats = []
        if self.load_config():
            if self.connect():
                self.mqtt = CONFIG.mqtt_config()
                # self.mqtt = False
                self.import_data()
        else:
            logging.critical("La configuration Home Assistant WebSocket est erronée")
        if self.websocket.connected:
            self.websocket.close()

    def load_config(self):
        """Load the Home Assistant WebSocket configuration from the configuration file.

        Returns:
            bool: True if the configuration is loaded, False otherwise
        """
        self.config = CONFIG.home_assistant_ws_config()
        if self.config is not None:
            if "url" in self.config:
                self.url = self.config["url"]
                if self.config.get("ssl"):
                    url_prefix = "wss"
                else:
                    url_prefix = "ws"
                self.url = f"{url_prefix}://{self.url}/api/websocket"
            else:
                logging.critical("L'url du WebSocket Home Assistant est obligatoire")
                return False
            if "token" in self.config:
                self.token = self.config["token"]
            else:
                logging.critical("Le token du WebSocket Home Assistant est obligatoire")
                return False
            if "purge" in self.config:
                self.purge = str2bool(self.config["purge"])
            if "batch_size" in self.config:
                if not is_integer(self.config["batch_size"]):
                    logging.error("Le paramètre batch_size du WebSocket Home Assistant doit être un entier")
                else:
                    self.batch_size = int(self.config["batch_size"])
        return True

    def connect(self):
        """Connect to the Home Assistant WebSocket server.

        Returns:
            bool: True if the connection is successful, False otherwise
        """
        try:
            check_ssl = CONFIG.get("ssl")
            sslopt = None
            if check_ssl and "gateway" in check_ssl:
                sslopt = {"cert_reqs": ssl.CERT_NONE}
            self.websocket = websocket.WebSocket(sslopt=sslopt)
            logging.info("Connexion au WebSocket Home Assistant %s", self.url)
            self.websocket.connect(
                self.url,
                timeout=5,
            )
            output = json.loads(self.websocket.recv())
            if "type" in output and output["type"] == "auth_required":
                logging.info("Authentification requise")
                return self.authentificate()
            return True
        except Exception as _e:
            self.websocket.close()
            logging.error(_e)
            logging.critical("Connexion impossible vers Home Assistant")
            logging.warning(
                " => ATTENTION, le WebSocket est également soumis au ban en cas de plusieurs échec d'authentification."
            )
            logging.warning(" => ex: 403: Forbidden")

    def authentificate(self):
        """Authenticate with the Home Assistant WebSocket server.

        Returns:
            bool: True if the authentication is successful, False otherwise
        """
        data = {"type": "auth", "access_token": self.token}
        auth_output = self.send(data)
        if auth_output["type"] == "auth_ok":
            logging.info(" => OK")
            return True
        logging.error(" => Authentification impossible, merci de vérifier votre url & token.")
        return False

    def send(self, data):
        """Send data to the Home Assistant WebSocket server.

        Args:
            data (dict): The data to send
        Returns:
            dict: The output from the server
        """
        self.websocket.send(json.dumps(data))
        self.id = self.id + 1
        output = json.loads(self.websocket.recv())
        if "type" in output and output["type"] == "result":
            if not output["success"]:
                logging.error(f"Erreur d'envoi : {data}")
                logging.error(output)
        return output

    def list_data(self):
        """List the data already cached in Home Assistant.

        Returns:
            dict: The list of data
        """
        logging.info("Liste les données déjà en cache.")
        import_statistics = {
            "id": self.id,
            "type": "recorder/list_statistic_ids",
            "statistic_type": "sum",
        }
        current_stats = self.send(import_statistics)
        for stats in current_stats["result"]:
            if stats["statistic_id"].startswith("myelectricaldata:"):
                self.current_stats.append(stats["statistic_id"])
        return current_stats

    def clear_data(self, statistic_ids):
        """Clear the data imported into Energy.

        Args:
            statistic_ids (list): The list of statistic ids
        Returns:
            dict: The output from clearing the data
        """
        logging.info("Effacement des données importées dans Energy.")
        for key in statistic_ids:
            logging.info(f" - {key}")
        clear_statistics = {
            "id": self.id,
            "type": "recorder/clear_statistics",
            "statistic_ids": statistic_ids,
        }
        for data in self.current_stats:
            logging.info(f" - {data}")
        clear_stat = self.send(clear_statistics)
        return clear_stat

    def get_data(self, statistic_ids, begin, end):
        """Get the data for a given period.

        Args:
            statistic_ids (list): The list of statistic ids
            begin (datetime): The start of the period
            end (datetime): The end of the period
        Returns:
            dict: The data for the period
        """
        statistics_during_period = {
            "id": self.id,
            "type": "recorder/statistics_during_period",
            "start_time": begin.isoformat(),
            "end_time": end.isoformat(),
            "statistic_ids": [statistic_ids],
            "period": "hour",
        }
        stat_period = self.send(statistics_during_period)
        return stat_period

    def import_data(self):  # noqa: C901
        """Import the data for the usage point into Home Assistant."""
        logging.info(f"Importation des données du point de livraison : {self.usage_point_id}")
        try:
            plan = DB.get_usage_point_plan(self.usage_point_id).upper()
            if self.usage_point_id_config.consumption_detail:
                logging.info("Consommation")
                measurement_direction = "consumption"
                if "max_date" in self.config:
                    logging.warning("Max date détectée %s", self.config["max_date"])
                    begin = datetime.strptime(self.config["max_date"], "%Y-%m-%d")
                    detail = DB.get_detail_all(begin=begin, usage_point_id=self.usage_point_id, order_dir="desc")
                else:
                    detail = DB.get_detail_all(usage_point_id=self.usage_point_id, order_dir="desc")

                cost = 0
                last_year = None
                last_month = None

                stats_kwh = {}
                stats_euro = {}

                db_tempo_price = DB.get_tempo_config("price")
                tempo_color_ref = {}
                for tempo_data in DB.get_tempo():
                    tempo_color_ref[tempo_data.date] = tempo_data.color

                stats = Stat(usage_point_id=self.usage_point_id, measurement_direction="consumption")

                for data in detail:
                    year = int(f'{data.date.strftime("%Y")}')
                    if last_year is None or year != last_year:
                        logging.info(f"{year} :")
                    month = int(f'{data.date.strftime("%m")}')
                    if last_month is None or month != last_month:
                        logging.info(f"- {month}")
                    last_year = year
                    last_month = month
                    hour_minute = int(f'{data.date.strftime("%H")}{data.date.strftime("%M")}')
                    name = f"MyElectricalData - {self.usage_point_id}"
                    statistic_id = f"myelectricaldata:{self.usage_point_id}"
                    value = data.value / (60 / data.interval)
                    if plan == "BASE":
                        name = f"{name} {plan} {measurement_direction}"
                        statistic_id = f"{statistic_id}_{plan.lower()}_{measurement_direction}"
                        cost = value * self.usage_point_id_config.consumption_price_base / 1000
                        tag = "base"
                    elif plan == "HC/HP":
                        measure_type = stats.get_mesure_type(data.date)
                        if measure_type == "HC":
                            name = f"{name} HC {measurement_direction}"
                            statistic_id = f"{statistic_id}_hc_{measurement_direction}"
                            cost = value * self.usage_point_id_config.consumption_price_hc / 1000
                            tag = "hc"
                        else:
                            name = f"{name} HP {measurement_direction}"
                            statistic_id = f"{statistic_id}_hp_{measurement_direction}"
                            cost = value * self.usage_point_id_config.consumption_price_hp / 1000
                            tag = "hp"
                    elif plan == "TEMPO":
                        if 600 <= hour_minute < 2200:
                            hour_type = "HP"
                        else:
                            hour_type = "HC"
                        if 600 <= hour_minute <= 2330:
                            date = datetime.combine(data.date, datetime.min.time())
                        else:
                            date = datetime.combine(data.date - timedelta(days=1), datetime.min.time())

                        if date not in tempo_color_ref:
                            logging.error(f"Import impossible, pas de donnée tempo sur la date du {data.date}")
                        else:
                            day_color = tempo_color_ref[date]
                            tempo_color = f"{day_color}{hour_type}"
                            tempo_color_price_key = f"{day_color.lower()}_{hour_type.lower()}"
                            tempo_price = float(db_tempo_price[tempo_color_price_key])
                            cost = value / 1000 * tempo_price
                            name = f"{name} {tempo_color} {measurement_direction}"
                            statistic_id = f"{statistic_id}_{tempo_color.lower()}_{measurement_direction}"
                            tag = tempo_color.lower()
                    else:
                        logging.error(f"Plan {plan} inconnu.")

                    date = TZ_PARIS.localize(data.date, "%Y-%m-%d %H:%M:%S").replace(minute=0, second=0, microsecond=0)
                    key = date.strftime("%Y-%m-%d %H:%M:%S")

                    # KWH
                    if statistic_id not in stats_kwh:
                        stats_kwh[statistic_id] = {"name": name, "sum": 0, "data": {}}
                    if key not in stats_kwh[statistic_id]["data"]:
                        stats_kwh[statistic_id]["data"][key] = {
                            "start": date.isoformat(),
                            "state": 0,
                            "sum": 0,
                        }
                    value = value / 1000
                    stats_kwh[statistic_id]["data"][key]["state"] = (
                        stats_kwh[statistic_id]["data"][key]["state"] + value
                    )
                    stats_kwh[statistic_id]["tag"] = tag
                    stats_kwh[statistic_id]["sum"] += value
                    stats_kwh[statistic_id]["data"][key]["sum"] = stats_kwh[statistic_id]["sum"]

                    # EURO
                    statistic_id = f"{statistic_id}_cost"
                    if statistic_id not in stats_euro:
                        stats_euro[statistic_id] = {
                            "name": f"{name} Cost",
                            "sum": 0,
                            "data": {},
                        }
                    if key not in stats_euro[statistic_id]["data"]:
                        stats_euro[statistic_id]["data"][key] = {
                            "start": date.isoformat(),
                            "state": 0,
                            "sum": 0,
                        }
                    stats_euro[statistic_id]["tag"] = tag
                    stats_euro[statistic_id]["data"][key]["state"] += cost
                    stats_euro[statistic_id]["sum"] += cost
                    stats_euro[statistic_id]["data"][key]["sum"] = stats_euro[statistic_id]["sum"]

                # CLEAN OLD DATA
                if self.purge or self.purge_force:
                    logging.info(f"Clean old data import In Home Assistant Recorder {self.usage_point_id}")
                    list_statistic_ids = []
                    for statistic_id, _ in stats_kwh.items():
                        list_statistic_ids.append(statistic_id)
                    self.clear_data(list_statistic_ids)
                    CONFIG.set("purge", False)


                for statistic_id, data in stats_kwh.items():
                    metadata = {
                        "has_mean": False,
                        "has_sum": True,
                        "name": data["name"],
                        "source": "myelectricaldata",
                        "statistic_id": statistic_id,
                        "unit_of_measurement": "kWh",
                    }


                    chunks = list(chunks_list(list(data["data"].values()), self.batch_size))
                    chunks_len = len(chunks)
                    for i, chunk in enumerate(chunks):
                        logging.info("Envoi des données de conso %s vers Home Assistant %s/%s (%s => %s)",
                            data["tag"].upper(),
                            i+1,
                            chunks_len,
                            chunk[-1]["start"],
                            chunk[0]["start"]
                        )
                        self.send({
                            "id": self.id,
                            "type": "recorder/import_statistics",
                            "metadata": metadata,
                            "stats": chunk,
                        })

                    if self.mqtt and "enable" in self.mqtt and str2bool(self.mqtt["enable"]):
                        HomeAssistant(self.usage_point_id).sensor(
                            topic=f"myelectricaldata_{data["tag"]}_{measurement_direction}/{self.usage_point_id}_energy",
                            name=f"{data["tag"]} {measurement_direction}",
                            device_name=f"Linky {self.usage_point_id}",
                            device_model=f"linky {self.usage_point_id}",
                            device_identifiers=f"{self.usage_point_id}",
                            uniq_id=statistic_id,
                            unit_of_measurement="kWh",
                            state=truncate(data["sum"]),
                            device_class="energy",
                            numPDL=self.usage_point_id,
                        )

                for statistic_id, data in stats_euro.items():
                    metadata = {
                        "has_mean": False,
                        "has_sum": True,
                        "name": data["name"],
                        "source": "myelectricaldata",
                        "statistic_id": statistic_id,
                        "unit_of_measurement": "EURO",
                    }
                    chunks = list(chunks_list(list(data["data"].values()), self.batch_size))
                    chunks_len = len(chunks)
                    for i, chunk in enumerate(chunks):
                        logging.info("Envoi des données de coût %s vers Home Assistant %s/%s (%s => %s)",
                            data["tag"].upper(),
                            i+1,
                            chunks_len,
                            chunk[0]["start"],
                            chunk[-1]["start"]
                        )
                        self.send({
                            "id": self.id,
                            "type": "recorder/import_statistics",
                            "metadata": metadata,
                            "stats": list(chunk),
                        })
                    if self.mqtt and "enable" in self.mqtt and str2bool(self.mqtt["enable"]):
                        HomeAssistant(self.usage_point_id).sensor(
                            topic=f"myelectricaldata_{data["tag"]}_{measurement_direction}/{self.usage_point_id}_cost",
                            name=f"{data["tag"]} {measurement_direction} cost",
                            device_name=f"Linky {self.usage_point_id}",
                            device_model=f"linky {self.usage_point_id}",
                            device_identifiers=f"{self.usage_point_id}",
                            uniq_id=statistic_id,
                            unit_of_measurement="EURO",
                            state=truncate(data["sum"]),
                            device_class="monetary",
                            numPDL=self.usage_point_id,
                        )

            if self.usage_point_id_config.production_detail:
                logging.info("Production")
                measurement_direction = "production"
                if "max_date" in self.config:
                    logging.warning("Max date détectée %s", self.config["max_date"])
                    begin = datetime.strptime(self.config["max_date"], "%Y-%m-%d")
                    detail = DB.get_detail_all(
                        begin=begin,
                        usage_point_id=self.usage_point_id,
                        measurement_direction="production",
                        order_dir="desc",
                    )
                else:
                    detail = DB.get_detail_all(
                        usage_point_id=self.usage_point_id, measurement_direction="production", order_dir="desc"
                    )

                cost = 0
                last_year = None
                last_month = None

                stats_kwh = {}
                stats_euro = {}
                for data in detail:
                    year = int(f'{data.date.strftime("%Y")}')
                    if last_year is None or year != last_year:
                        logging.info(f"{year} :")
                    month = int(f'{data.date.strftime("%m")}')
                    if last_month is None or month != last_month:
                        logging.info(f"- {month}")
                    last_year = year
                    last_month = month
                    hour_minute = int(f'{data.date.strftime("%H")}{data.date.strftime("%M")}')
                    name = f"MyElectricalData - {self.usage_point_id} {measurement_direction}"
                    statistic_id = f"myelectricaldata:{self.usage_point_id}_{measurement_direction}"
                    value = data.value / (60 / data.interval)
                    cost = value * self.usage_point_id_config.production_price / 1000
                    date = TZ_PARIS.localize(data.date, "%Y-%m-%d %H:%M:%S").replace(minute=0, second=0, microsecond=0)
                    key = date.strftime("%Y-%m-%d %H:%M:%S")

                    # KWH
                    if statistic_id not in stats_kwh:
                        stats_kwh[statistic_id] = {"name": name, "sum": 0, "data": {}}
                    if key not in stats_kwh[statistic_id]["data"]:
                        stats_kwh[statistic_id]["data"][key] = {
                            "start": date.isoformat(),
                            "state": 0,
                            "sum": 0,
                        }
                    value = value / 1000
                    stats_kwh[statistic_id]["data"][key]["state"] = (
                        stats_kwh[statistic_id]["data"][key]["state"] + value
                    )
                    stats_kwh[statistic_id]["sum"] += value
                    stats_kwh[statistic_id]["data"][key]["sum"] = stats_kwh[statistic_id]["sum"]

                    # EURO
                    statistic_id = f"{statistic_id}_revenue"
                    if statistic_id not in stats_euro:
                        stats_euro[statistic_id] = {
                            "name": f"{name} Revenue",
                            "sum": 0,
                            "data": {},
                        }
                    if key not in stats_euro[statistic_id]["data"]:
                        stats_euro[statistic_id]["data"][key] = {
                            "start": date.isoformat(),
                            "state": 0,
                            "sum": 0,
                        }
                    stats_euro[statistic_id]["data"][key]["state"] += cost
                    stats_euro[statistic_id]["sum"] += cost
                    stats_euro[statistic_id]["data"][key]["sum"] = stats_euro[statistic_id]["sum"]

                if self.purge or self.purge_force:
                    list_statistic_ids = []
                    for statistic_id, _ in stats_kwh.items():
                        list_statistic_ids.append(statistic_id)
                    self.clear_data(list_statistic_ids)
                    CONFIG.set("purge", False)

                for statistic_id, data in stats_kwh.items():
                    metadata = {
                        "has_mean": False,
                        "has_sum": True,
                        "name": data["name"],
                        "source": "myelectricaldata",
                        "statistic_id": statistic_id,
                        "unit_of_measurement": "kWh",
                    }
                    import_statistics = {
                        "id": self.id,
                        "type": "recorder/import_statistics",
                        "metadata": metadata,
                        "stats": list(data["data"].values()),
                    }
                    self.send(import_statistics)
                    if self.mqtt and "enable" in self.mqtt and str2bool(self.mqtt["enable"]):
                        HomeAssistant(self.usage_point_id).sensor(
                            topic=f"myelectricaldata_{measurement_direction}/{self.usage_point_id}_energy",
                            name=f"{measurement_direction} energy",
                            device_name=f"Linky {self.usage_point_id}",
                            device_model=f"linky {self.usage_point_id}",
                            device_identifiers=f"{self.usage_point_id}",
                            uniq_id=statistic_id,
                            unit_of_measurement="kWh",
                            state=truncate(data["sum"]),
                            device_class="energy",
                            numPDL=self.usage_point_id,
                        )
                for statistic_id, data in stats_euro.items():
                    metadata = {
                        "has_mean": False,
                        "has_sum": True,
                        "name": data["name"],
                        "source": "myelectricaldata",
                        "statistic_id": statistic_id,
                        "unit_of_measurement": "EURO",
                    }
                    import_statistics = {
                        "id": self.id,
                        "type": "recorder/import_statistics",
                        "metadata": metadata,
                        "stats": list(data["data"].values()),
                    }
                    self.send(import_statistics)
                    if self.mqtt and "enable" in self.mqtt and str2bool(self.mqtt["enable"]):
                        HomeAssistant(self.usage_point_id).sensor(
                            topic=f"myelectricaldata_{measurement_direction}/{self.usage_point_id}_cost",
                            name=f"{measurement_direction} cost",
                            device_name=f"Linky {self.usage_point_id}",
                            device_model=f"linky {self.usage_point_id}",
                            device_identifiers=f"{self.usage_point_id}",
                            uniq_id=statistic_id,
                            unit_of_measurement="EURO",
                            state=truncate(data["sum"]),
                            device_class="monetary",
                            numPDL=self.usage_point_id,
                        )
        except Exception as _e:
            self.websocket.close()
            traceback.print_exc()
            logging.error(_e)
            logging.critical("Erreur lors de l'export des données vers Home Assistant")
