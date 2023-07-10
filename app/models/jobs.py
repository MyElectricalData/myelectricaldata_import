import logging
import time
import traceback

from dependencies import str2bool, title, finish, get_version, log_usage_point_id
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
    def __init__(self, config, db, usage_point_id=None):
        self.config = config
        self.db = db
        self.usage_point_id = usage_point_id
        self.usage_point_config = {}
        self.mqtt_config = self.config.mqtt_config()
        self.home_assistant_config = self.config.home_assistant_config()
        self.influxdb_config = self.config.influxdb_config()
        self.wait_job_start = 10

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
            if self.usage_point_id is None:
                self.usage_points = self.db.get_usage_point_all()
            else:
                self.usage_points = [self.db.get_usage_point(self.usage_point_id)]

            #######################################################################################################
            # FETCH TEMPO DATA
            try:
                tempo_config = self.config.tempo_config()
                if tempo_config and "enable" in tempo_config and tempo_config["enable"]:
                    self.get_tempo()
                else:
                    title(
                        [f"Import Tempo désactivé"])
            except Exception as e:
                traceback.print_exc()
                logging.error([f"Erreur lors de la récupération des données tempo", e])

            #######################################################################################################
            # FETCH ECOWATT DATA
            try:
                self.get_ecowatt()
            except Exception as e:
                traceback.print_exc()
                logging.error([f"Erreur lors de la récupération des données EcoWatt", e])

            for self.usage_point_config in self.usage_points:
                self.usage_point_id = self.usage_point_config.usage_point_id
                log_usage_point_id(self.usage_point_id)
                self.db.last_call_update(self.usage_point_id)
                if self.usage_point_config.enable:
                    try:
                        if target == "gateway_status" or target is None:
                            self.get_gateway_status()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération des informations de la passerelle", e])
                    try:
                        if target == "account_status" or target is None:
                            self.get_account_status()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération du status de votre compte", e])
                    try:
                        if target == "contract" or target is None:
                            self.get_contract()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération des informations du contract", e])
                    try:
                        if target == "addresses" or target is None:
                            self.get_addresses()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de vos coordonnées", e])
                    try:
                        if target == "consumption" or target is None:
                            self.get_consumption()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de votre consommation journalière", e])
                    try:
                        if target == "consumption_detail" or target is None:
                            self.get_consumption_detail()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de votre consommation détaillée", e])
                    try:
                        if target == "production" or target is None:
                            self.get_production()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de votre production journalière", e])
                    try:
                        if target == "production_detail" or target is None:
                            self.get_production_detail()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de votre production détaillée", e])
                    try:
                        if target == "consumption_max_power" or target is None:
                            self.get_consumption_max_power()
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la récupération de votre puissance maximum journalière", e])
                    try:
                        if target == "price" or target is None:
                            self.stat_price(self.usage_point_id)
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la génération des statistique tarifaire de consommation", e])
                    try:
                        if target == "price" and target is None:
                            self.stat_price(self.usage_point_id, "production")
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de la génération des statistique tarifaire de production", e])
                    try:
                        # #######################################################################################################
                        # # MQTT
                        title(" Exportation MQTT")
                        if "enable" in self.mqtt_config and self.mqtt_config["enable"]:
                            if target == "mqtt" or target is None:
                                ExportMqtt(self.config, self.db, self.usage_point_id).status()
                                ExportMqtt(self.config, self.db, self.usage_point_id).contract()
                                ExportMqtt(self.config, self.db, self.usage_point_id).address()
                                if hasattr(self.usage_point_config,
                                           "consumption") and self.usage_point_config.consumption:
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "consumption").daily_annual(
                                        self.usage_point_config.consumption_price_base
                                    )
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "consumption").daily_linear(
                                        self.usage_point_config.consumption_price_base
                                    )
                                if hasattr(self.usage_point_config,
                                           "production") and self.usage_point_config.production:
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "production").daily_annual(
                                        self.usage_point_config.production_price
                                    )
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "production").daily_linear(
                                        self.usage_point_config.production_price
                                    )
                                if hasattr(self.usage_point_config,
                                           "consumption_detail") and self.usage_point_config.consumption_detail:
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "consumption").detail_annual(
                                        self.usage_point_config.consumption_price_hp,
                                        self.usage_point_config.consumption_price_hc
                                    )
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "consumption").detail_linear(
                                        self.usage_point_config.consumption_price_hp,
                                        self.usage_point_config.consumption_price_hc
                                    )
                                if hasattr(self.usage_point_config,
                                           "production_detail") and self.usage_point_config.production_detail:
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "production").detail_annual(
                                        self.usage_point_config.production_price
                                    )
                                    ExportMqtt(self.config, self.db, self.usage_point_id,
                                               "production").detail_linear(
                                        self.usage_point_config.production_price
                                    )
                                if hasattr(self.usage_point_config,
                                           "consumption_max_power") and self.usage_point_config.consumption_max_power:
                                    ExportMqtt(self.config, self.db, self.usage_point_id).max_power()
                            export_finish()
                        else:
                            title(" Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de l'exportation des données dans MQTT", e])

                    #######################################################################################################
                    # HOME ASSISTANT
                    try:
                        if "enable" in self.home_assistant_config and str2bool(self.home_assistant_config["enable"]):
                            if "enable" in self.mqtt_config and str2bool(self.mqtt_config["enable"]):
                                if target == "home_assistant" or target is None:
                                    title(" Exportation Home Assistant")
                                    HomeAssistant(self.mqtt_config, self.usage_point_id).export()
                                    export_finish()
                            else:
                                logging.critical("L'export Home Assistant est dépendant de MQTT, "
                                                 "merci de configurer MQTT avant d'exporter vos données dans Home Assistant")
                        else:
                            title(" Exportation Home Assistant")
                            title(" Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de l'exportation des données dans Home Assistant", e])

                    #######################################################################################################
                    # INFLUXDB
                    try:
                        if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
                            # INFLUXDB.purge_influxdb()
                            if target == "influxdb" or target is None:
                                title(" Exportation InfluxDB")
                                if hasattr(self.usage_point_config,
                                           "consumption") and self.usage_point_config.consumption:
                                    ExportInfluxDB(self.influxdb_config, self.db, self.usage_point_config).daily()
                                if hasattr(self.usage_point_config,
                                           "production") and self.usage_point_config.production:
                                    ExportInfluxDB(self.influxdb_config, self.db, self.usage_point_config).daily(
                                        measurement_direction="production")
                                if hasattr(self.usage_point_config,
                                           "consumption_detail") and self.usage_point_config.consumption_detail:
                                    ExportInfluxDB(self.influxdb_config, self.db, self.usage_point_config).detail()
                                if hasattr(self.usage_point_config,
                                           "production_detail") and self.usage_point_config.production_detail:
                                    ExportInfluxDB(self.influxdb_config, self.db, self.usage_point_config).detail(
                                        measurement_direction="production")
                            export_finish()
                        else:
                            title(" Exportation InfluxDB")
                            title(" Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        logging.error([f"Erreur lors de l'exportation des données dans InfluxDB", e])
                else:
                    logging.info(
                        f" => Point de livraison Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9).")
            finish()
            self.usage_point_id = None
            self.db.unlock()
            return {
                "status": True,
                "notif": "Importation terminée"
            }

    def header_generate(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': self.usage_point_config.token,
            'call-service': "myelectricaldata",
            'version': get_version()
        }

    def get_gateway_status(self):
        title(f"[{self.usage_point_config.usage_point_id}] Statut de la passerelle :")
        result = Status(
            self.db,
            headers=self.header_generate(),
        ).ping()
        return result

    def get_account_status(self):
        title(f"[{self.usage_point_config.usage_point_id}] Check account status :")
        result = Status(
            self.db,
            headers=self.header_generate(),
        ).status(usage_point_id=self.usage_point_config.usage_point_id)
        return result

    def get_contract(self):
        title(f"[{self.usage_point_config.usage_point_id}] Récupération du contrat :")
        result = Contract(
            db=self.db,
            headers=self.header_generate(),
            usage_point_id=self.usage_point_config.usage_point_id,
            config=self.usage_point_config
        ).get()
        if "error" in result and result["error"]:
            logging.error(result["description"])
        return result

    def get_addresses(self):
        title(f"[{self.usage_point_config.usage_point_id}] Récupération des coordonnées :")
        result = Address(
            config=self.config,
            db=self.db,
            headers=self.header_generate(),
            usage_point_id=self.usage_point_config.usage_point_id,
        ).get()
        if "error" in result and result["error"]:
            logging.error(result["description"])
        return result

    def get_consumption(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
            title(f"[{self.usage_point_config.usage_point_id}] Récupération de la consommation journalière :")
            result = Daily(
                config=self.config,
                db=self.db,
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id
            ).get()
        return result

    def get_consumption_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
            title(f"[{self.usage_point_config.usage_point_id}] Récupération de la consommation détaillée :")
            result = Detail(
                config=self.config,
                db=self.db,
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
            ).get()
        return result

    def get_production(self):
        result = {}
        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
            title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production journalière :")
            result = Daily(
                config=self.config,
                db=self.db,
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                measure_type="production"
            ).get()
        return result

    def get_production_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
            title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production détaillée :")
            result = Detail(
                config=self.config,
                db=self.db,
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                measure_type="production"
            ).get()
        return result

    def get_consumption_max_power(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption_max_power") and self.usage_point_config.consumption_max_power:
            title(
                f"[{self.usage_point_config.usage_point_id}] Récupération de la puissance maximun journalière :")
            result = Power(
                config=self.config,
                db=self.db,
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id
            ).get()
        return result

    def get_tempo(self):
        title(
            f"Récupération des données Tempo :")
        return Tempo(
            config=self.config,
            db=self.db
        ).get()

    def get_ecowatt(self):
        title(
            f"Récupération des données EcoWatt :")
        return Ecowatt(
            config=self.config,
            db=self.db
        ).get()

    def stat_price(self, usage_point_id, measurement_direction="consumption"):
        title(
            f"Génération des statistiques Tarifaire de {measurement_direction}:")
        return Stat(self.config, self.db, usage_point_id=usage_point_id,
                    measurement_direction=measurement_direction).price()

    def home_assistant(self):
        result = {}
        if "enable" in self.home_assistant_config and self.home_assistant_config["enable"]:
            title(
                f"[{self.usage_point_config.usage_point_id}] Exportation de données dans Home Assistant (via l'auto-discovery MQTT).")
            result = self.db.get_daily_all(self.usage_point_id, "consumption")
        return result

    def influxdb(self):
        result = {}
        if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
            title(f"[{self.usage_point_config.usage_point_id}] Exportation de données dans InfluxDB.")
        return result
