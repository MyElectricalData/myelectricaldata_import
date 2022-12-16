import __main__ as app
import time
import traceback

from dependencies import str2bool
from models.config import get_version
from models.database import Database
from models.export_home_assistant import HomeAssistant
from models.export_influxdb import ExportInfluxDB
from models.export_mqtt import ExportMqtt
from models.log import Log
from models.query_address import Address
from models.query_contract import Contract
from models.query_daily import Daily
from models.query_detail import Detail
from models.query_status import Status

DB = Database()
LOG = Log()


class Job:
    def __init__(self, usage_point_id=None):
        self.config = app.CONFIG
        self.usage_point_id = usage_point_id
        self.usage_point_config = {}
        self.mqtt_config = self.config.mqtt_config()
        self.home_assistant_config = self.config.home_assistant_config()
        self.influxdb_config = self.config.influxdb_config()
        self.wait_job_start = 10

    def job_import_data(self, wait=True, target=None):
        if app.DB.lock_status():
            return {
                "status": False,
                "notif": "Importation déjà en cours..."
            }
        else:
            DB.lock()
            if wait:
                LOG.title("Démarrage du job d'importation dans 10s")
                i = self.wait_job_start
                while i > 0:
                    LOG.log(f" => {i}s")
                    time.sleep(1)
                    i = i - 1
            if self.usage_point_id is None:
                self.usage_points = DB.get_usage_point_all()
            else:
                self.usage_points = [DB.get_usage_point(self.usage_point_id)]
            for self.usage_point_config in self.usage_points:
                self.usage_point_id = self.usage_point_config.usage_point_id
                LOG.log_usage_point_id(self.usage_point_id)
                if self.usage_point_config.enable:
                    try:
                        if target == "gateway_status" or target is None:
                            self.get_gateway_status()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération des informations de la passerelle", e])
                    try:
                        if target == "account_status" or target is None:
                            self.get_account_status()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération du status de votre compte", e])
                    try:
                        if target == "contract" or target is None:
                            self.get_contract()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération des informations du contract", e])
                    try:
                        if target == "addresses" or target is None:
                            self.get_addresses()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération de vos coordonnées", e])
                    try:
                        if target == "consumption" or target is None:
                            self.get_consumption()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération de votre consommation journalière", e])
                    try:
                        if target == "consumption_detail" or target is None:
                            self.get_consumption_detail()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération de votre consommation détaillée", e])
                    try:
                        if target == "production" or target is None:
                            self.get_production()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération de votre production journalière", e])
                    try:
                        if target == "production_detail" or target is None:
                            self.get_production_detail()
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de la récupération de votre production détaillée", e])

                    try:
                        # #######################################################################################################
                        # # MQTT
                        if "enable" in self.mqtt_config and self.mqtt_config["enable"]:
                            if target == "mqtt" or target is None:
                                LOG.title("Exportation MQTT")
                                ExportMqtt(self.usage_point_id).status()
                                ExportMqtt(self.usage_point_id).contract()
                                ExportMqtt(self.usage_point_id).address()
                                if hasattr(self.usage_point_config,
                                           "consumption") and self.usage_point_config.consumption:
                                    ExportMqtt(self.usage_point_id, "consumption").daily_annual(
                                        self.usage_point_config.consumption_price_base
                                    )
                                    ExportMqtt(self.usage_point_id, "consumption").daily_linear(
                                        self.usage_point_config.consumption_price_base
                                    )
                                if hasattr(self.usage_point_config,
                                           "production") and self.usage_point_config.production:
                                    ExportMqtt(self.usage_point_id, "production").daily_annual(
                                        self.usage_point_config.production_price
                                    )
                                    ExportMqtt(self.usage_point_id, "production").daily_linear(
                                        self.usage_point_config.production_price
                                    )
                                if hasattr(self.usage_point_config,
                                           "consumption_detail") and self.usage_point_config.consumption_detail:
                                    ExportMqtt(self.usage_point_id, "consumption").detail_annual(
                                        self.usage_point_config.consumption_price_hp,
                                        self.usage_point_config.consumption_price_hc
                                    )
                                    ExportMqtt(self.usage_point_id, "consumption").detail_linear(
                                        self.usage_point_config.consumption_price_hp,
                                        self.usage_point_config.consumption_price_hc
                                    )
                                if hasattr(self.usage_point_config,
                                           "production_detail") and self.usage_point_config.production_detail:
                                    ExportMqtt("production").detail_annual(self.usage_point_config.production_price)
                                    ExportMqtt("production").detail_linear(self.usage_point_config.production_price)
                            LOG.log(" => Export terminé")
                        else:
                            LOG.title("Exportation MQTT")
                            LOG.log(" => Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de l'exportation des données dans MQTT", e])

                    #######################################################################################################
                    # HOME ASSISTANT
                    try:
                        if "enable" in self.home_assistant_config and str2bool(self.home_assistant_config["enable"]):
                            if "enable" in self.mqtt_config and str2bool(self.mqtt_config["enable"]):
                                if target == "home_assistant" or target is None:
                                    LOG.title("Exportation Home Assistant")
                                    HomeAssistant(self.usage_point_id).export()
                                    LOG.log(" => Export terminé")
                            else:
                                LOG.critical("L'export Home Assistant est dépendant de MQTT, "
                                             "merci de configurer MQTT avant d'exporter vos données dans Home Assistant")
                        else:
                            LOG.title("Exportation Home Assistant")
                            LOG.log(" => Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de l'exportation des données dans Home Assistant", e])

                    #######################################################################################################
                    # INFLUXDB
                    try:
                        if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
                            # app.INFLUXDB.purge_influxdb()
                            if target == "influxdb" or target is None:
                                LOG.title("Exportation InfluxDB")
                                if hasattr(self.usage_point_config,
                                           "consumption") and self.usage_point_config.consumption:
                                    ExportInfluxDB(self.usage_point_id).daily(
                                        self.usage_point_config.consumption_price_base,
                                    )
                                if hasattr(self.usage_point_config,
                                           "production") and self.usage_point_config.production:
                                    ExportInfluxDB(self.usage_point_id).daily(
                                        self.usage_point_config.production_price,
                                        "production"
                                    )
                                if hasattr(self.usage_point_config,
                                           "consumption_detail") and self.usage_point_config.consumption_detail:
                                    ExportInfluxDB(self.usage_point_id).detail(
                                        self.usage_point_config.consumption_price_hp,
                                        self.usage_point_config.consumption_price_hc
                                    )
                                if hasattr(self.usage_point_config,
                                           "production_detail") and self.usage_point_config.production_detail:
                                    ExportInfluxDB(self.usage_point_id).detail(
                                        self.usage_point_config.production_price,
                                        measurement_direction="production_detail"
                                    )
                            LOG.log(" => Export terminé")
                        else:
                            LOG.title("Exportation InfluxDB")
                            LOG.log(" => Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9)")
                    except Exception as e:
                        traceback.print_exc()
                        LOG.error([f"Erreur lors de l'exportation des données dans InfluxDB", e])
                else:
                    LOG.log(f" => Point de livraison Désactivé dans la configuration (Exemple: https://tinyurl.com/2kbd62s9).")
            LOG.finish()
            DB.unlock()
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
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Statut de la passerelle :")
        result = Status(
            headers=self.header_generate(),
        ).ping()
        return result

    def get_account_status(self):
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Check account status :")
        result = Status(
            headers=self.header_generate(),
        ).status(usage_point_id=self.usage_point_config.usage_point_id)
        return result

    def get_contract(self):
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération du contrat :")
        result = Contract(
            headers=self.header_generate(),
            usage_point_id=self.usage_point_config.usage_point_id,
            config=self.usage_point_config
        ).get()
        if "error" in result and result["error"]:
            LOG.error(result["description"])
        return result

    def get_addresses(self):
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération des coordonnées :")
        result = Address(
            headers=self.header_generate(),
            usage_point_id=self.usage_point_config.usage_point_id,
            config=self.usage_point_config
        ).get()
        if "error" in result and result["error"]:
            LOG.error(result["description"])
        return result

    def get_consumption(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la consommation journalière :")
            result = Daily(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id
            ).get()
        return result

    def get_consumption_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la consommation détaillée :")
            result = Detail(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
            ).get()
        return result

    def get_production(self):
        result = {}
        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production journalière :")
            result = Daily(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                measure_type="production"
            ).get()
        return result

    def get_production_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production détaillée :")
            result = Detail(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                measure_type="production"
            ).get()
        return result

    def home_assistant(self):
        if "enable" in self.home_assistant_config and self.home_assistant_config["enable"]:
            LOG.title(
                f"[{self.usage_point_config.usage_point_id}] Exportation de données dans Home Assistant (via l'auto-discovery MQTT).")
            daily = app.DB.get_daily_all(self.usage_point_id, "consumption")
        return daily

    def influxdb(self):
        result = {}
        if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Exportation de données dans InfluxDB.")
        return result
