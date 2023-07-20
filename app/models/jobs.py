import logging
import time
import traceback
from os import getenv, environ

from dependencies import str2bool, title, finish, get_version, log_usage_point_id
from init import DB, CONFIG
from models.export_home_assistant import HomeAssistant
from models.export_influxdb import ExportInfluxDB
from models.export_mqtt import ExportMqtt
from models.query_address import Address
from models.query_contract import Contract
from models.query_daily import Daily
from models.query_detail import Detail
from models.query_ecowatt import Ecowatt
from models.query_power import Power
from models.query_status import Status
from models.query_tempo import Tempo
from models.stat import Stat


def export_finish():
    title(" Export terminé")


class Job:
    def __init__(self, usage_point_id=None):
        self.config = CONFIG
        self.db = DB
        self.usage_point_id = usage_point_id
        self.usage_point_config = {}
        self.mqtt_config = self.config.mqtt_config()
        self.home_assistant_config = self.config.home_assistant_config()
        self.influxdb_config = self.config.influxdb_config()
        self.wait_job_start = 10
        self.tempo_enable = False

        if self.usage_point_id is None:
            self.usage_points = self.db.get_usage_point_all()
        else:
            self.usage_points = [self.db.get_usage_point(self.usage_point_id)]

    def boot(self):
        if ("DEV" in environ and getenv("DEV")) or ("DEBUG" in environ and getenv("DEBUG")):
            logging.warning("=> Import job disable")
        else:
            self.job_import_data()

    def job_import_data(self, wait=True, target=None):
        if self.db.lock_status():
            return {
                "status": False,
                "notif": "Importation déjà en cours..."
            }
        else:
            self.db.lock()
            if wait:
                title(" Démarrage du job d'importation dans 10s")
                i = self.wait_job_start
                while i > 0:
                    title(f" {i}s")
                    time.sleep(1)
                    i = i - 1

            if target == "gateway_status" or target is None:
                self.get_gateway_status()

            for self.usage_point_config in self.usage_points:
                self.usage_point_id = self.usage_point_config.usage_point_id
                log_usage_point_id(self.usage_point_id)
                self.db.last_call_update(self.usage_point_id)
                if self.usage_point_config.enable:

                    # if target == "account_status" or target is None:
                    #     self.get_account_status()
                    #
                    # if target == "contract" or target is None:
                    #     self.get_contract()
                    #
                    # if target == "addresses" or target is None:
                    #     self.get_addresses()
                    #
                    # if target == "consumption" or target is None:
                    #     self.get_consumption()
                    #
                    # if target == "consumption_detail" or target is None:
                    #     self.get_consumption_detail()
                    #
                    # if target == "production" or target is None:
                    #     self.get_production()
                    #
                    # if target == "production_detail" or target is None:
                    #     self.get_production_detail()
                    #
                    # if target == "consumption_max_power" or target is None:
                    #     self.get_consumption_max_power()
                    #
                    # if target == "price" or target is None:
                    #     self.stat_price()
                    #
                    # #######################################################################################################
                    # # MQTT
                    # if target == "mqtt" or target is None:
                    #     self.export_mqtt()

                    #######################################################################################################
                    # HOME ASSISTANT
                    if target == "home_assistant" or target is None:
                        self.export_home_assistant()

                    #######################################################################################################
                    # INFLUXDB
                    if target == "influxdb" or target is None:
                        self.export_influxdb()
                else:
                    logging.info(
                        f" => Point de livraison Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9).")

            # ######################################################################################################
            # FETCH TEMPO DATA
            if target == "tempo" or target is None:
                self.get_tempo()

            # ######################################################################################################
            # FETCH ECOWATT DATA
            if target == "ecowatt" or target is None:
                self.get_ecowatt()

            finish()

            self.usage_point_id = None
            self.db.unlock()
            return {
                "status": True,
                "notif": "Importation terminée"
            }

    def header_generate(self, token=True):
        output = {
            'Content-Type': 'application/json',
            'call-service': "myelectricaldata",
            'version': get_version()
        }
        if token:
            output['Authorization'] = self.usage_point_config.token
        return output

    def get_gateway_status(self):
        detail = "Récupération du statut de la passerelle :"
        try:
            title(detail)
            Status(headers=self.header_generate(token=False)).ping()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_account_status(self):
        detail = "Récupération des informations du compte"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    usage_point_id = usage_point_config.usage_point_id
                    title(f"[{usage_point_id}] {detail}  :")
                    if self.usage_point_config.enable:
                        Status(headers=self.header_generate()).status(usage_point_id=usage_point_id)
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                Status(headers=self.header_generate()).status(usage_point_id=self.usage_point_id)
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_contract(self):
        detail = "Récupération des informations contractuelles"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    usage_point_id = usage_point_config.usage_point_id
                    title(f"[{usage_point_id}] {detail} :")
                    if self.usage_point_config.enable:
                        Contract(
                            headers=self.header_generate(),
                            usage_point_id=usage_point_id,
                            config=self.usage_point_config
                        ).get()
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                Contract(
                    headers=self.header_generate(),
                    usage_point_id=self.usage_point_id,
                    config=self.usage_point_config
                ).get()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_addresses(self):
        detail = "Récupération des coordonnées postales"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    usage_point_id = usage_point_config.usage_point_id
                    title(f"[{usage_point_id}] {detail} :")
                    if self.usage_point_config.enable:
                        Address(headers=self.header_generate(), usage_point_id=usage_point_id).get()
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                Address(headers=self.header_generate(), usage_point_id=self.usage_point_id).get()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_consumption(self):
        detail = "Récupération de la consommation journalière"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    if hasattr(usage_point_config, "consumption") and usage_point_config.consumption:
                        usage_point_id = usage_point_config.usage_point_id
                        title(f"[{usage_point_id}] {detail} :")
                        if self.usage_point_config.enable:
                            Daily(headers=self.header_generate(), usage_point_id=usage_point_id).get()
                    else:
                        logging.info(f"{detail} désactivée sur le point de livraison")
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                    Daily(headers=self.header_generate(), usage_point_id=self.usage_point_id).get()
                else:
                    logging.info(f"{detail} désactivée sur le point de livraison")

        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_consumption_detail(self):
        detail = "Récupération de la consommation détaillée"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    if hasattr(usage_point_config, "consumption_detail") and usage_point_config.consumption_detail:
                        usage_point_id = usage_point_config.usage_point_id
                        title(f"[{usage_point_id}] {detail} :")
                        if self.usage_point_config.enable:
                            Detail(headers=self.header_generate(), usage_point_id=usage_point_id).get()
                    else:
                        logging.info(f"{detail} désactivée sur le point de livraison")
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                if hasattr(self.usage_point_config,
                           "consumption_detail") and self.usage_point_config.consumption_detail:
                    Detail(headers=self.header_generate(), usage_point_id=self.usage_point_id).get()
                else:
                    logging.info(f"{detail} désactivée sur le point de livraison")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_production(self):
        detail = "Récupération de la production journalière"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    if hasattr(usage_point_config, "production") and usage_point_config.production:
                        usage_point_id = usage_point_config.usage_point_id
                        title(f"[{usage_point_id}] {detail} :")
                        if self.usage_point_config.enable:
                            Daily(
                                headers=self.header_generate(),
                                usage_point_id=usage_point_id,
                                measure_type="production").get()
                    else:
                        logging.info(f"{detail} désactivée sur le point de livraison")
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                    Daily(
                        headers=self.header_generate(),
                        usage_point_id=self.usage_point_id,
                        measure_type="production").get()
                else:
                    logging.info(f"{detail} désactivée sur le point de livraison")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_production_detail(self):
        detail = "Récupération de la production détaillée"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    if hasattr(usage_point_config, "production_detail") and usage_point_config.production_detail:
                        usage_point_id = usage_point_config.usage_point_id
                        title(f"[{usage_point_id}] {detail} :")
                        if self.usage_point_config.enable:
                            Detail(
                                headers=self.header_generate(),
                                usage_point_id=usage_point_id,
                                measure_type="production").get()
                    else:
                        logging.info(f"{detail} désactivée sur le point de livraison")
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                    Detail(
                        headers=self.header_generate(),
                        usage_point_id=self.usage_point_id,
                        measure_type="production").get()
                else:
                    logging.info(f"{detail} désactivée sur le point de livraison")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_consumption_max_power(self):
        detail = "Récupération de la puissance maximum journalière"
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    usage_point_id = usage_point_config.usage_point_id
                    title(f"[{usage_point_id}] {detail} :")
                    if self.usage_point_config.enable:
                        Power(headers=self.header_generate(), usage_point_id=usage_point_id).get()
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                Power(headers=self.header_generate(), usage_point_id=self.usage_point_id).get()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def get_tempo(self):
        title(f"Récupération des données Tempo :")
        try:
            tempo_config = self.config.tempo_config()
            if tempo_config and "enable" in tempo_config and tempo_config["enable"]:
                Tempo().fetch()
            else:
                title([f"Import Tempo désactivé"])
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la récupération des données tempo", e])

    def get_ecowatt(self):
        title(f"Récupération des données EcoWatt :")
        try:
            Ecowatt().fetch()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la récupération des données EcoWatt", e])

    def stat_price(self):
        detail = "Génération des statistiques Tarifaire de consommation/production "
        try:
            if self.usage_point_id is None:
                for usage_point_config in self.usage_points:
                    usage_point_id = usage_point_config.usage_point_id
                    title(f"[{usage_point_id}] {detail} :")
                    if self.usage_point_config.enable:
                        if hasattr(usage_point_config, "consumption_detail") and usage_point_config.consumption_detail:
                            Stat(usage_point_id=usage_point_id).generate_price()
                        if hasattr(usage_point_config, "production_detail") and usage_point_config.consumption_detail:
                            Stat(usage_point_id=usage_point_id, measurement_direction="production").generate_price()
            else:
                title(f"[{self.usage_point_id}] {detail} :")
                if hasattr(self.usage_point_config,
                           "consumption_detail") and self.usage_point_config.consumption_detail:
                    Stat(usage_point_id=self.usage_point_id).generate_price()
                if hasattr(self.usage_point_config,
                           "production_detail") and self.usage_point_config.consumption_detail:
                    Stat(usage_point_id=self.usage_point_id, measurement_direction="production").generate_price()
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de la {detail.lower()}", e])

    def export_home_assistant(self):
        try:
            if "enable" in self.home_assistant_config and str2bool(self.home_assistant_config["enable"]):
                if "enable" in self.mqtt_config and str2bool(self.mqtt_config["enable"]):
                    for self.usage_point_config in self.usage_points:
                        self.usage_point_id = self.usage_point_config.usage_point_id
                        if self.usage_point_config.enable:
                            HomeAssistant(self.usage_point_id).export()
                    export_finish()
                else:
                    logging.critical("L'export Home Assistant est dépendant de MQTT, "
                                     "merci de configurer MQTT avant d'exporter vos données dans Home Assistant")
            else:
                title("Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de l'export des données dans Home Assistant", e])

    def export_influxdb(self):
        try:
            title(" Export InfluxDB")
            if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
                for self.usage_point_config in self.usage_points:
                    self.usage_point_id = self.usage_point_config.usage_point_id
                    if self.usage_point_config.enable:
                        export_influxdb = ExportInfluxDB(self.influxdb_config, self.usage_point_config)

                        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                            export_influxdb.daily()
                        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                            export_influxdb.daily(measurement_direction="production")
                        if hasattr(self.usage_point_config,
                                   "consumption_detail") and self.usage_point_config.consumption_detail:
                            export_influxdb.detail()
                        if hasattr(self.usage_point_config,
                                   "production_detail") and self.usage_point_config.production_detail:
                            export_influxdb.detail(measurement_direction="production")

                        tempo_config = self.config.tempo_config()
                        if tempo_config and "enable" in tempo_config and tempo_config["enable"]:
                            export_influxdb.tempo()

                        export_influxdb.ecowatt()
                        export_finish()
            else:
                title("Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de l'export des données dans InfluxDB", e])

    def export_mqtt(self):
        try:
            title(" Export MQTT")
            if "enable" in self.mqtt_config and self.mqtt_config["enable"]:
                for self.usage_point_config in self.usage_points:
                    self.usage_point_id = self.usage_point_config.usage_point_id
                    if self.usage_point_config.enable:
                        export_mqtt = ExportMqtt(self.usage_point_id)
                        export_mqtt.status()
                        export_mqtt.contract()
                        export_mqtt.address()
                        export_mqtt.ecowatt()
                        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                            export_mqtt.daily_annual(self.usage_point_config.consumption_price_base,
                                                     measurement_direction="consumption")
                            export_mqtt.daily_linear(self.usage_point_config.consumption_price_base,
                                                     measurement_direction="consumption")
                        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                            export_mqtt.daily_annual(self.usage_point_config.production_price,
                                                     measurement_direction="production")
                            export_mqtt.daily_linear(self.usage_point_config.production_price,
                                                     measurement_direction="production")
                        if hasattr(self.usage_point_config,
                                   "consumption_detail") and self.usage_point_config.consumption_detail:
                            export_mqtt.detail_annual(self.usage_point_config.consumption_price_hp,
                                                      self.usage_point_config.consumption_price_hc,
                                                      measurement_direction="consumption")
                            export_mqtt.detail_linear(self.usage_point_config.consumption_price_hp,
                                                      self.usage_point_config.consumption_price_hc,
                                                      measurement_direction="consumption")
                        if hasattr(self.usage_point_config,
                                   "production_detail") and self.usage_point_config.production_detail:
                            export_mqtt.detail_annual(self.usage_point_config.production_price,
                                                      measurement_direction="production")
                            export_mqtt.detail_linear(self.usage_point_config.production_price,
                                                      measurement_direction="production")
                        if hasattr(self.usage_point_config,
                                   "consumption_max_power") and self.usage_point_config.consumption_max_power:
                            export_mqtt.max_power()
            else:
                title("Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
        except Exception as e:
            traceback.print_exc()
            logging.error([f"Erreur lors de l'export des données dans MQTT", e])
