import json
import logging
import ssl
from datetime import datetime, timedelta

import pytz
import websocket

from init import CONFIG, DB

TZ_PARIS = pytz.timezone("Europe/Paris")


class HomeAssistantWs:
    def __init__(self, usage_point_id):
        self.ws = None
        self.usage_point_id = usage_point_id
        self.usage_point_id_config = DB.get_usage_point(self.usage_point_id)
        self.config = None
        self.url = None
        self.ssl = None
        self.token = None
        self.id = 1
        self.current_stats = []
        if self.load_config():
            if self.connect():
                # self.list_data()
                # self.clear_data()
                self.import_data()
        else:
            logging.critical("La configuration Home Assistant WebSocket est erronée")
        if self.ws.connected:
            self.ws.close()

    def load_config(self):
        self.config = CONFIG.home_assistant_ws()
        if self.config is not None:
            if "url" in self.config:
                self.url = self.config["url"]
                if "ssl" in self.config and self.config["ssl"]:
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
        return True

    def connect(self):
        try:
            check_ssl = CONFIG.get("ssl")
            sslopt = None
            if check_ssl and "gateway" in check_ssl:
                sslopt = {"cert_reqs": ssl.CERT_NONE}
            self.ws = websocket.WebSocket(sslopt=sslopt)
            logging.info(f"Connexion au WebSocket Home Assistant {self.url}")
            self.ws.connect(
                self.url,
                timeout=5,
            )
            output = json.loads(self.ws.recv())
            if "type" in output and output["type"] == "auth_required":
                logging.info("Authentification requise")
                return self.authentificate()
            return True
        except Exception as e:
            self.ws.close()
            logging.error(e)
            logging.critical("Connexion impossible vers Home Assistant")
            logging.warning(
                f" => ATTENTION, le WebSocket est également soumis au ban en cas de plusieurs échec d'authentification."
            )
            logging.warning(f" => ex: 403: Forbidden")

    def authentificate(self):
        data = {"type": "auth", "access_token": self.token}
        auth_output = self.send(data)
        if auth_output["type"] == "auth_ok":
            logging.info(" => OK")
            return True
        else:
            logging.error(" => Authentification impossible, merci de vérifier votre url & token.")
            return False

    def send(self, data):
        self.ws.send(json.dumps(data))
        self.id = self.id + 1
        output = json.loads(self.ws.recv())
        if "type" in output and output["type"] == "result":
            if not output["success"]:
                logging.error(f"Erreur d'envoie : {data}")
                logging.error(output)
        return output

    def list_data(self):
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

    def clear_data(self):
        logging.info("Effacement des données importées dans Energy.")
        clear_statistics = {
            "id": self.id,
            "type": "recorder/clear_statistics",
            "statistic_ids": self.current_stats,
        }
        logging.info("Clean :")
        for data in self.current_stats:
            logging.info(f" - {data}")
        clear_stat = self.send(clear_statistics)
        return clear_stat

    def get_data(self, statistic_ids, begin, end):
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

    def import_data(self):
        logging.info(f"Importation des données du point de livraison : {self.usage_point_id}")
        try:
            plan = self.usage_point_id_config.plan.upper()
            if self.usage_point_id_config.consumption_detail:
                logging.info("Consommation")
                measure_type = "consumption"
                if "max_date" in self.config:
                    logging.warn(f"WARNING : Max date détecter {self.config['max_date']}")
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
                        name = f"{name} {plan} {measure_type}"
                        statistic_id = f"{statistic_id}_{plan.lower()}_{measure_type}"
                        cost = value * self.usage_point_id_config.consumption_price_base / 1000
                    elif plan == "HC/HP":
                        if data.measure_type == "HC":
                            name = f"{name} HC {measure_type}"
                            statistic_id = f"{statistic_id}_hc_{measure_type}"
                            cost = value * self.usage_point_id_config.consumption_price_hc / 1000
                        else:
                            name = f"{name} HP {measure_type}"
                            statistic_id = f"{statistic_id}_hp_{measure_type}"
                            cost = value * self.usage_point_id_config.consumption_price_hp / 1000
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
                            name = f"{name} {tempo_color} {measure_type}"
                            statistic_id = f"{statistic_id}_{tempo_color.lower()}_{measure_type}"
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
                    stats_euro[statistic_id]["data"][key]["state"] += cost
                    stats_euro[statistic_id]["sum"] += cost
                    stats_euro[statistic_id]["data"][key]["sum"] = stats_euro[statistic_id]["sum"]

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

            if self.usage_point_id_config.production_detail:
                logging.info("Production")
                measure_type = "production"
                if "max_date" in self.config:
                    logging.warn(f"WARNING : Max date détectée {self.config['max_date']}")
                    begin = datetime.strptime(self.config["max_date"], "%Y-%m-%d")
                    detail = DB.get_detail_all(begin=begin, usage_point_id=self.usage_point_id, order_dir="desc")
                else:
                    detail = DB.get_detail_all(usage_point_id=self.usage_point_id, order_dir="desc")

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
                    name = f"MyElectricalData - {self.usage_point_id} {measure_type}"
                    statistic_id = f"myelectricaldata:{self.usage_point_id}_{measure_type}"
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
        except Exception as e:
            self.ws.close()
            logging.error(e)
            logging.critical("Erreur lors de l'export des données vers Home Assistant")
