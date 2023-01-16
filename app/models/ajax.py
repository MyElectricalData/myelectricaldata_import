import __main__ as app
from datetime import datetime, timezone, timedelta

import pytz
from dependencies import daterange
from models.config import get_version
from models.jobs import Job
from models.query_cache import Cache
from models.query_daily import Daily
from models.query_detail import Detail
from models.query_power import Power
from models.query_status import Status

utc = pytz.UTC


class Ajax:

    def __init__(self, usage_point_id=None):
        self.db = app.DB
        self.application_path = app.APPLICATION_PATH
        self.usage_point_id = usage_point_id
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
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
        app.LOG.title(f"[{self.usage_point_id}] Reset de la puissance maximum journalière.")
        Power(
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

    def delete_all_data(self):
        app.LOG.title(f"[{self.usage_point_id}] Suppression de la consommation journalière.")
        Daily(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
        ).delete()
        app.LOG.title(f"[{self.usage_point_id}] Suppression de la puissance maximum journalière.")
        Power(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
        ).delete()
        app.LOG.title(f"[{self.usage_point_id}] Suppression de la consommation détaillée.")
        Detail(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
        ).delete()
        app.LOG.title(f"[{self.usage_point_id}] Suppression de la production journalière.")
        Daily(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
            measure_type="production"
        ).delete()
        app.LOG.title(f"[{self.usage_point_id}] Suppression de la production détaillée.")
        Detail(
            headers=self.headers,
            usage_point_id=self.usage_point_id,
            measure_type="production"
        ).delete()
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
            # date = date.replace("---", " ")
            # date = date.replace("--", ":")
            app.LOG.title(f"[{self.usage_point_id}] Reset de la consommation détaillée du {date}:")
            result["consumption_detail"] = Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id
            ).reset_daily(date)
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
            # date = date.replace("---", " ")
            # date = date.replace("--", ":")
            app.LOG.title(f"[{self.usage_point_id}] Reset de la production détaillée du {date}:")
            result["production_detail"] = Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production"
            ).reset_daily(date)
        else:
            return {
                "error": "true",
                "notif": "Target inconnue.",
                "result": ""
            }
        if result[target]:
            return {
                "error": "false",
                "notif": f'Reset de la "{target}" du {date}',
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
            # date = date.replace("---", " ")
            # date = date.replace("--", ":")
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
            # date = date.replace("---", " ")
            # date = date.replace("--", ":")
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
            if target in result and "value" in result[target]:
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
            else:
                data = {
                    "error": "false",
                    "notif": f'Importation de la "{target}" du {date}',
                    "result": {
                        "value": 0,
                        "date": 0,
                        "fail_count": 0
                    }
                }
            return data

    def blacklist(self, target, date):
        result = {}
        if target == "consumption":
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                app.LOG.title(f"[{self.usage_point_id}] Blacklist de la consommation journalière du {date}:")
                result["consumption"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).blacklist(date, True)
        elif target == "consumption_max_power":
            if hasattr(self.usage_point_config,
                       "consumption_max_power") and self.usage_point_config.consumption_max_power:
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
            if hasattr(self.usage_point_config,
                       "consumption_max_power") and self.usage_point_config.consumption_max_power:
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

    def datatable(self, measurement_direction, args):
        recordsTotal = 0
        draw = int(args.get("draw"))
        length = int(args.get("length"))
        search = args.get("search[value]")
        start_index = int(args.get("start"))
        end_index = start_index + length
        order_column = int(args.get("order[0][column]"))
        order_dir = args.get("order[0][dir]")
        all_data = []
        data = []
        if measurement_direction == "consumption":
            recordsTotal = app.DB.get_daily_count(usage_point_id=self.usage_point_id,
                                                  measurement_direction="consumption")
            col_spec = {
                0: "date",
                1: "value",
                2: "value",
                3: "fail_count",
                4: "cache",
                5: "import_clean",
                6: "blacklist",
            }
            all_data = app.DB.get_daily_datatable(
                usage_point_id=self.usage_point_id,
                order_column=col_spec[order_column],
                order_dir=order_dir,
                search=search,
                measurement_direction="consumption")
            data = self.datatable_daily(all_data, start_index, end_index, measurement_direction)

        elif measurement_direction == "consumption_detail":
            recordsTotal = app.DB.get_detail_count(usage_point_id=self.usage_point_id,
                                                   measurement_direction="consumption")
            col_spec = {
                0: "date",
                1: "date",
                2: "value",
                3: "value",
                4: "fail_count",
                5: "cache",
                6: "import_clean",
                7: "blacklist",
            }
            all_data = app.DB.get_detail_datatable(
                usage_point_id=self.usage_point_id,
                order_column=col_spec[order_column],
                order_dir=order_dir,
                search=search,
                measurement_direction="consumption")
            data = self.datatable_detail(all_data, start_index, end_index, measurement_direction)

        elif measurement_direction == "production":
            recordsTotal = app.DB.get_daily_count(usage_point_id=self.usage_point_id,
                                                  measurement_direction="production")
            col_spec = {
                0: "date",
                1: "value",
                2: "value",
                3: "fail_count",
                4: "cache",
                5: "import_clean",
                6: "blacklist",
            }
            all_data = app.DB.get_daily_datatable(
                usage_point_id=self.usage_point_id,
                order_column=col_spec[order_column],
                order_dir=order_dir,
                search=search,
                measurement_direction="production")
            data = self.datatable_daily(all_data, start_index, end_index, measurement_direction)
        elif measurement_direction == "production_detail":
            recordsTotal = app.DB.get_detail_count(usage_point_id=self.usage_point_id,
                                                   measurement_direction="production")
            col_spec = {
                0: "date",
                1: "date",
                2: "value",
                3: "value",
                4: "fail_count",
                5: "cache",
                6: "import_clean",
                7: "blacklist",
            }
            all_data = app.DB.get_detail_datatable(
                usage_point_id=self.usage_point_id,
                order_column=col_spec[order_column],
                order_dir=order_dir,
                search=search,
                measurement_direction="production")
            data = self.datatable_detail(all_data, start_index, end_index, measurement_direction)
        elif measurement_direction == "consumption_max_power":
            recordsTotal = app.DB.get_daily_max_power_count(usage_point_id=self.usage_point_id)
            col_spec = {
                0: "date",
                1: "date",
                2: "value",
                3: "value",
                4: "ampere",
                5: "fail_count",
                6: "cache",
                7: "import_clean",
                8: "blacklist",
            }
            all_data = app.DB.get_daily_max_power_datatable(
                usage_point_id=self.usage_point_id,
                order_column=col_spec[order_column],
                order_dir=order_dir,
                search=search)
            data = self.datatable_max_power(all_data, start_index, end_index)
        result = {
            "draw": draw + 1,
            "recordsTotal": recordsTotal,
            "recordsFiltered": len(all_data),
            "data": data
        }
        return result

    def datatable_button(self,measurement_direction, db_data):
        date_text = db_data.date.strftime(self.date_format)
        value = db_data.value
        blacklist = db_data.blacklist
        fail_count = db_data.fail_count

        btn_import = ""
        btn_reset = ""
        btn_blacklist = ""
        btn_whitelist = ""
        btn_import_disable = ""
        btn_blacklist_disable = ""

        if fail_count == 0 and value > 0:
            btn_import = "display:none"
            btn_whitelist = "display:none"
            btn_blacklist_disable = "datatable_button_disable"
        elif blacklist == 1:
            btn_blacklist = "display:none"
            btn_reset = "display:none"
            btn_import_disable = "datatable_button_disable"
        else:
            btn_reset = "display:none"
            btn_whitelist = "display:none"

        cache_html = f"""
        <div id="{measurement_direction}_import_{date_text}" title="{measurement_direction}" name="import_{self.usage_point_id}_{date_text}" class="datatable_button datatable_button_import {btn_import_disable}" style="{btn_import}">
            <input type="button" value="Importer"></div>
        <div id="{measurement_direction}_reset_{date_text}" title="{measurement_direction}" name="reset_{self.usage_point_id}_{date_text}"  class="datatable_button" style="{btn_reset}">
            <input type="button" value="Vider"></div>
        """

        blacklist_html = f"""
        <div class="datatable_button datatable_blacklist {btn_blacklist_disable}" title="{measurement_direction}" id="{measurement_direction}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}" style="{btn_blacklist}">
            <input type="button" value="Blacklist"></div>
        <div class="datatable_button datatable_whitelist" title="{measurement_direction}" id="{measurement_direction}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}" style="{btn_whitelist}">
            <input type="button"  value="Whitelist"></div>
        """

        btn = {
            "cache": cache_html,
            "blacklist": blacklist_html
        }
        return btn

    def datatable_daily(self, all_data, start_index, end_index, measurement_direction):
        index = 0
        result = []
        for db_data in all_data:
            if start_index <= index <= end_index:
                date_text = db_data.date.strftime(self.date_format)
                target = "daily"
                # VALUE
                conso_w = f"""<div id="{measurement_direction}_conso_w_{date_text}">{db_data.value}</div>"""
                conso_kw = f"""<div id="{measurement_direction}_conso_kw_{date_text}">{db_data.value / 1000}</div>"""
                fail_count = f"""<div id="{measurement_direction}_fail_count_{date_text}">{db_data.fail_count}</div>"""
                # CACHE STATE
                if db_data.fail_count == 0:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                else:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                day_data = [
                    date_text,
                    conso_w,
                    conso_kw,
                    fail_count,
                    cache_state,
                    self.datatable_button(measurement_direction, db_data)["cache"],
                    self.datatable_button(measurement_direction, db_data)["blacklist"],
                ]
                result.append(day_data)
            index = index + 1
        return result

    def datatable_detail(self, all_data, start_index, end_index, measurement_direction):
        index = 0
        result = []
        for db_data in all_data:
            if start_index <= index <= end_index:
                # print(db_data)
                date_text = db_data.date.strftime(self.date_format)
                date_hour = db_data.date.strftime("%H:%M:%S")
                target = "detail"
                # VALUE
                conso_w = f"""<div id="{measurement_direction}_conso_w_{date_text}">{db_data.value}</div>"""
                conso_kw = f"""<div id="{measurement_direction}_conso_kw_{date_text}">{db_data.value / 1000}</div>"""
                fail_count = f"""<div id="{measurement_direction}_fail_count_{date_text}">{db_data.fail_count}</div>"""
                # CACHE STATE
                if db_data.fail_count == 0:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                else:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                day_data = [
                    date_text,
                    date_hour,
                    conso_w,
                    conso_kw,
                    fail_count,
                    cache_state,
                    self.datatable_button(measurement_direction, db_data)["cache"],
                    self.datatable_button(measurement_direction, db_data)["blacklist"],
                ]
                result.append(day_data)
            index = index + 1
        return result

    def datatable_max_power(self, all_data, start_index, end_index):
        index = 0
        result = []
        measurement_direction = "maxpower"
        event_date = ""
        target = "daily"
        contract = self.db.get_contract(self.usage_point_id)
        if hasattr(contract, "subscribed_power") and contract.subscribed_power is not None:
            max_power = int(contract.subscribed_power.split(' ')[0])*1000
        else:
            max_power = 999000
        for db_data in all_data:
            if start_index <= index <= end_index:
                date_text = db_data.date.strftime(self.date_format)
                ampere = f"{round(int(db_data.value) / 220, 1)}"
                if isinstance(db_data.event_date, datetime):
                    event_date = db_data.event_date.strftime("%H:%M:%S")
                # VALUE
                if max_power <= int(db_data.value):
                    style = 'style="color:#FF0000; font-weight:bolder"'
                elif (max_power * 80 / 100) <= db_data.value:
                    style = 'style="color:#FFB600; font-weight:bolder"'
                else:
                    style = ""
                conso_w = f"""<div id="{measurement_direction}_conso_w_{date_text}" {style}>{db_data.value}</div>"""
                conso_kw = f"""<div id="{measurement_direction}_conso_kw_{date_text}" {style}>{db_data.value / 1000}</div>"""
                conso_a = f"""<div id="{measurement_direction}_fail_count_{date_text}" {style}>{ampere}</div>"""
                fail_count = f"""<div id="{measurement_direction}_fail_count_{date_text}" {style}>{db_data.fail_count}</div>"""

                # CACHE STATE
                if db_data.fail_count == 0:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                else:
                    cache_state = f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                day_data = [
                    date_text,
                    event_date,
                    conso_w,
                    conso_kw,
                    conso_a,
                    fail_count,
                    cache_state,
                    self.datatable_button(measurement_direction, db_data)["cache"],
                    self.datatable_button(measurement_direction, db_data)["blacklist"],
                ]
                result.append(day_data)
            index = index + 1
        return result