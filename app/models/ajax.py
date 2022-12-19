import __main__ as app
from dependencies import reformat_json
from models.jobs import Job
from models.config import get_version
from models.query_daily import Daily
from models.query_power import Power
from models.query_detail import Detail
from models.query_status import Status
from models.query_cache import Cache


class Ajax:

    def __init__(self, usage_point_id=None):
        self.db = app.DB
        self.application_path = app.APPLICATION_PATH
        self.usage_point_id = usage_point_id
        if self.usage_point_id is not None:
            self.usage_point_config = self.db.get_usage_point(self.usage_point_id)
            if hasattr(self.usage_point_config, "token"):
                self.headers = {
                    'Content-Type': 'application/json',
                    'Authorization': self.usage_point_config.token,
                    'call-service': "myelectricaldata",
                    'version': get_version()
                }
            else:
                self.headers = {
                    'Content-Type': 'application/json',
                    'call-service': "myelectricaldata",
                    'version': get_version()
                }
        self.usage_points_id_list = ""

    def gateway_status(self):
        app.LOG.title(f"[{self.usage_point_id}] Check de l'état de la passerelle.")
        return Status().ping()

    def account_status(self):
        app.LOG.title(f"[{self.usage_point_id}] Check du statut du compte.")
        return Status(headers=self.headers).status(self.usage_point_id)

    def reset_all_data(self):
        app.LOG.title(f"[{self.usage_point_id}] Reset de la consommation journalière.")
        Daily(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
        ).reset()
        app.LOG.title(f"[{self.usage_point_id}] Reset de la consommation détaillée.")
        Detail(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
        ).reset()
        app.LOG.title(f"[{self.usage_point_id}] Reset de la production journalière.")
        Daily(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
            measure_type="production"
        ).reset()
        app.LOG.title(f"[{self.usage_point_id}] Reset de la production détaillée.")
        Detail(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
            measure_type="production"
        ).reset()
        return {
            "error": "false",
            "notif": "Toutes les données ont été supprimées.",
        }

    def reset_gateway(self):
        app.LOG.title(f"[{self.usage_point_id}] Reset du cache de la passerelle.")
        return Cache(self.usage_point_id).reset()

    def reset_data(self, target, date):
        result = {}
        if target == "consumption":
            app.LOG.title(f"[{self.usage_point_id}] Reset de la consommation journalière du {date}:")
            result["consumption"] = Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id
            ).reset(date)
        elif target == "consumption_detail":
            app.LOG.title(f"[{self.usage_point_id}] Reset de la consommation détaillée du {date}:")
            result["consumption_detail"] = Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id
            ).reset(date)
        elif target == "consumption_max_power":
            app.LOG.title(f"[{self.usage_point_id}] Reset de la puissance maximum du {date}:")
            result["consumption_max_power"] = Power(
                headers=self.headers,
                usage_point_id=self.usage_point_id
            ).reset(date)
        elif target == "production":
            app.LOG.title(f"[{self.usage_point_id}] Reset de la production journalière du {date}:")
            result["production"] = Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production"
            ).reset(date)
        elif target == "production_detail":
            app.LOG.title(f"[{self.usage_point_id}] Reset de la production détaillée du {date}:")
            result["production_detail"] = Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production"
            ).reset(date)
        else:
            return {
                "error": "true",
                "notif": "Target inconnue.",
                "result": ""
            }
        if result[target]:
            return {
                "error": "false",
                "notif": f"Reset de la {target} journalière du {date}",
                "result": result[target]
            }
        else:
            return {
                "error": "true",
                "notif": "Erreur lors du traitement.",
                "result": result[target]
            }

    def fetch(self, target, date):
        result = {}
        if target == "consumption":
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                app.LOG.title(f"[{self.usage_point_id}] Importation de la consommation journalière du {date}:")
                result["consumption"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
        elif target == "consumption_max_power":
            if hasattr(self.usage_point_config, "consumption_max_power") and self.usage_point_config.consumption:
                app.LOG.title(f"[{self.usage_point_id}] Importation de la puissance maximum journalière du {date}:")
                result["consumption_max_power"] = Power(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
        elif target == "consumption_detail":
            if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
                app.LOG.title(f"[{self.usage_point_id}] Importation de la consommation détaillée du {date}:")
                result["consumption_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
        elif target == "production":
            if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                app.LOG.title(f"[{self.usage_point_id}] Importation de la production journalière du {date}:")
                result["production"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).fetch(date)
        elif target == "production_detail":
            if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                app.LOG.title(f"[{self.usage_point_id}] Importation de la production détaillée du {date}:")
                result["production_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).fetch(date)
        else:
            return {
                "error": "true",
                "notif": "Target inconnue.",
                "result": ""
            }
        if "error" in result[target] and result[target]["error"]:
            data = {
                "error": "true",
                "notif": result[target]['notif'],
                "result": {
                    "value": 0,
                    "date": date,
                    "fail_count": result[target]["fail_count"]
                }
            }
            if "event_date" in result[target]:
                data["result"]["event_date"] = result[target]["event_date"]
            return data
        else:
            data = {
                "error": "false",
                "notif": f"Importation de la {target} journalière du {date}",
                "result": {
                    "value": result[target]["value"],
                    "date": result[target]["date"],
                    "fail_count": 0
                }
            }
            if "event_date" in result[target]:
                data["result"]["event_date"] = result[target]["event_date"]
            return data

    def blacklist(self, target, date):
        print(target)
        result = {}
        if target == "consumption":
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la consommation journalière du {date}:")
                result["consumption"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, True)
        elif target == "consumption_max_power":
            if hasattr(self.usage_point_config, "consumption_max_power") and self.usage_point_config.consumption_max_power:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la puissance maximum du {date}:")
                result["consumption_max_power"] = Power(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, True)
        elif target == "consumption_detail":
            if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la consommation détaillée du {date}:")
                result["consumption_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, True)
        elif target == "production":
            if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la production journalière du {date}:")
                result["production"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).blacklist(date, True)
        elif target == "production_detail":
            if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la production détaillée du {date}:")
                result["production_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).blacklist(date, True)
        else:
            return {
                "error": "true",
                "notif": "Target inconnue.",
                "result": ""
            }
        if not result[target]:
            return {
                "error": "true",
                "notif": "Erreur lors du traitement.",
                "result": result[target]
            }
        else:
            return {
                "error": "false",
                "notif": f"Blacklist de la {target} journalière du {date}",
                "result": result[target]
            }

    def whitelist(self, target, date):
        result = {}
        if target == "consumption":
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                app.LOG.title(f"[{self.usage_point_id}] Whitelist de la consommation journalière du {date}:")
                result["consumption"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, False)
        elif target == "consumption_max_power":
            if hasattr(self.usage_point_config, "consumption_max_power") and self.usage_point_config.consumption_max_power:
                app.LOG.title(f"[{self.usage_point_id}] Whitelist de la puissance maximale journalière du {date}:")
                result["consumption_max_power"] = Power(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, False)
        elif target == "consumption_detail":
            if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
                app.LOG.title(f"[{self.usage_point_id}] Whitelist de la consommation détaillée du {date}:")
                result["consumption_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, False)
        elif target == "production":
            if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                app.LOG.title(f"[{self.usage_point_id}] Whitelist de la production journalière du {date}:")
                result["production"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).blacklist(date, False)
        elif target == "production_detail":
            if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                app.LOG.title(f"[{self.usage_point_id}] Whitelist de la production détaillée du {date}:")
                result["production_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production"
                ).blacklist(date, False)
        else:
            return {
                "error": "true",
                "notif": "Target inconnue.",
                "result": ""
            }
        if not result[target]:
            return {
                "error": "true",
                "notif": "Erreur lors du traitement.",
                "result": result[target]
            }
        else:
            return {
                "error": "false",
                "notif": f"Whitelist de la {target} journalière du {date}",
                "result": result[target]
            }

    def import_data(self, target=None):
        result = Job(self.usage_point_id).job_import_data(wait=False, target=target)
        if not result:
            return {
                "error": "true",
                "notif": "Erreur lors du traitement.",
                "result": result
            }
        else:
            return {
                "error": "false",
                "notif": "Récupération de la consommation/production.",
                "result": result
            }

    def new_account(self, configs):
        self.usage_point_id = configs['usage_point_id']
        app.LOG.title(f"[{self.usage_point_id}] Ajout d'un nouveau point de livraison:")
        output = {}
        for key, value in configs.items():
            if key != "usage_point_id":
                if value is None or value == "None":
                    value = ""
                app.LOG.log(f"{str(key)} => {str(value)}")
                output[key] = value
                app.CONFIG.set_usage_point_config(self.usage_point_id, key, value)
        app.DB.set_usage_point(self.usage_point_id, output)
        return output

    def configuration(self, configs):
        app.LOG.title(f"[{self.usage_point_id}] Changement de configuration:")
        output = {}
        for key, value in configs.items():
            if value is None or value == "None":
                value = ""
            app.LOG.log(f"{str(key)} => {str(value)}")
            output[key] = value
            app.CONFIG.set_usage_point_config(self.usage_point_id, key, value)
        app.DB.set_usage_point(self.usage_point_id, output)
        return output
