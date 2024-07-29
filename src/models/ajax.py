"""This module represents an Ajax object."""
import inspect
from datetime import datetime

import pytz
from fastapi import Request

from config.main import APP_CONFIG
from database.contracts import DatabaseContracts
from database.daily import DatabaseDaily
from database.detail import DatabaseDetail
from database.max_power import DatabaseMaxPower
from database.tempo import DatabaseTempo
from database.usage_points import DatabaseUsagePoints
from external_services.myelectricaldata.cache import Cache
from external_services.myelectricaldata.daily import Daily
from external_services.myelectricaldata.detail import Detail
from external_services.myelectricaldata.ecowatt import Ecowatt
from external_services.myelectricaldata.power import Power
from external_services.myelectricaldata.status import Status
from external_services.myelectricaldata.tempo import Tempo
from models.jobs import Job
from models.stat import Stat
from utils import check_format, get_version, title

utc = pytz.UTC


class UsagePoint:
    """Usage point configurateur config."""

    name: str
    enable: str
    token: str
    cache: str
    plan: str
    refresh_addresse: str
    refresh_contract: str
    consumption: str
    consumption_max_power: str
    consumption_max_date: str
    consumption_detail: str
    consumption_detail_max_date: str
    consumption_price_hc: str
    consumption_price_hp: str
    consumption_price_base: str
    offpeak_hours_0: str
    offpeak_hours_1: str
    offpeak_hours_2: str
    offpeak_hours_3: str
    offpeak_hours_4: str
    offpeak_hours_5: str
    offpeak_hours_6: str
    production: str
    production_max_date: str
    production_detail: str
    production_detail_max_date: str
    production_price: str


class Ajax:
    """This class represents an Ajax object."""

    def __init__(self, usage_point_id=None):
        """Initialize Ajax."""
        self.usage_point_id = usage_point_id
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        if self.usage_point_id is not None:
            self.usage_point_config = DatabaseUsagePoints(self.usage_point_id).get()
            if hasattr(self.usage_point_config, "token"):
                self.headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.usage_point_config.token,
                    "call-service": "myelectricaldata",
                    "version": get_version(),
                }
            else:
                self.headers = {
                    "Content-Type": "application/json",
                    "call-service": "myelectricaldata",
                    "version": get_version(),
                }
        self.usage_points_id_list = ""

    def gateway_status(self):
        """Check the status of the gateway."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            if self.usage_point_id is not None:
                msg = f"[{self.usage_point_id}] Check de l'état de la passerelle."
            else:
                msg = "Check de l'état de la passerelle."
            title(msg)
            return Status().ping()

    def account_status(self):
        """Check the status of the account."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Check du statut du compte.")
            data = Status(headers=self.headers).status(self.usage_point_id)
            if isinstance(self.usage_point_config.last_call, datetime):
                data["last_call"] = self.usage_point_config.last_call.strftime("%H:%M")
            else:
                data["last_call"] = self.usage_point_config.last_call
            return data

    def fetch_tempo(self):
        """Fetch tempo day."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title("Récupération des jours Tempo.")
            return Tempo().fetch()

    def get_tempo(self):
        """Fetch tempo day number."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title("Affichage des jours Tempo.")
            return Tempo().get()

    def fetch_ecowatt(self):
        """Fetch the days of Ecowatt."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title("Récupération des jours Ecowatt.")
            return Ecowatt().fetch()

    def get_ecowatt(self):
        """Get the days of Ecowatt."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title("Affichage des jours Ecowatt.")
            return Ecowatt().get()

    def generate_price(self):
        """Generate the costs by subscription type."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Calcul des coûts par type d'abonnements.")
            return Stat(self.usage_point_id, "consumption").generate_price()

    def get_price(self):
        """Get the result of the subscription comparator."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Retourne le résultat du comparateur d'abonnements.")
            return Stat(self.usage_point_id, "consumption").get_price()

    def reset_all_data(self):
        """Reset all the data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Reset de la consommation journalière.")
            Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).reset()
            title(f"[{self.usage_point_id}] Reset de la puissance maximum journalière.")
            Power(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).reset()
            title(f"[{self.usage_point_id}] Reset de la consommation détaillée.")
            Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).reset()
            title(f"[{self.usage_point_id}] Reset de la production journalière.")
            Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production",
            ).reset()
            title(f"[{self.usage_point_id}] Reset de la production détaillée.")
            Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production",
            ).reset()
            return {
                "error": "false",
                "notif": "Toutes les données ont été supprimées.",
            }

    def delete_all_data(self):
        """Delete all the data."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Suppression de la consommation journalière.")
            Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).delete()
            title(f"[{self.usage_point_id}] Suppression de la puissance maximum journalière.")
            Power(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).delete()
            title(f"[{self.usage_point_id}] Suppression de la consommation détaillée.")
            Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
            ).delete()
            title(f"[{self.usage_point_id}] Suppression de la production journalière.")
            Daily(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production",
            ).delete()
            title(f"[{self.usage_point_id}] Suppression de la production détaillée.")
            Detail(
                headers=self.headers,
                usage_point_id=self.usage_point_id,
                measure_type="production",
            ).delete()
            title(f"[{self.usage_point_id}] Suppression des statistiques.")
            Stat(usage_point_id=self.usage_point_id).delete()
            return {
                "error": "false",
                "notif": "Toutes les données ont été supprimées.",
            }

    def reset_gateway(self):
        """Reset the gateway cache."""
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Reset du cache de la passerelle.")
            return Cache(headers=self.headers, usage_point_id=self.usage_point_id).reset()

    def reset_data(self, target, date):
        """Reset the specified data for the given target and date.

        Args:
            target (str): The target to reset.
            date (str): The date to reset.

        Returns:
            dict: The result of the reset.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            result = {}
            if target == "consumption":
                title(f"[{self.usage_point_id}] Reset de la consommation journalière du {date}:")
                result["consumption"] = Daily(headers=self.headers, usage_point_id=self.usage_point_id).reset(date)
            elif target == "consumption_detail":
                title(f"[{self.usage_point_id}] Reset de la consommation détaillée du {date}:")
                result["consumption_detail"] = Detail(
                    headers=self.headers, usage_point_id=self.usage_point_id
                ).reset_daily(date)
            elif target == "consumption_max_power":
                title(f"[{self.usage_point_id}] Reset de la puissance maximum du {date}:")
                result["consumption_max_power"] = Power(
                    headers=self.headers, usage_point_id=self.usage_point_id
                ).reset(date)
            elif target == "production":
                title(f"[{self.usage_point_id}] Reset de la production journalière du {date}:")
                result["production"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production",
                ).reset(date)
            elif target == "production_detail":
                title(f"[{self.usage_point_id}] Reset de la production détaillée du {date}:")
                result["production_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production",
                ).reset_daily(date)
            else:
                return {"error": "true", "notif": "Target inconnue.", "result": ""}
            if result[target]:
                return {
                    "error": "false",
                    "notif": f'Reset de la "{target}" du {date}',
                    "result": result[target],
                }
            return {
                "error": "true",
                "notif": "Erreur lors du traitement.",
                "result": result[target],
            }

    def fetch(self, target, date):  # noqa: C901
        """Fetch the specified data for the given target and date.

        Args:
            target (str): The target to fetch.
            date (str): The date to fetch.

        Returns:
            dict: The fetched data.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            result = {}
            if (
                target == "consumption"
                and hasattr(self.usage_point_config, "consumption")
                and self.usage_point_config.consumption
            ):
                title(f"[{self.usage_point_id}] Importation de la consommation journalière du {date}:")
                result["consumption"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
            elif (
                target == "consumption_max_power"
                and hasattr(self.usage_point_config, "consumption_max_power")
                and self.usage_point_config.consumption_max_power
            ):
                title(f"[{self.usage_point_id}] Importation de la puissance maximum journalière du {date}:")
                result["consumption_max_power"] = Power(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
            elif (
                target == "consumption_detail"
                and hasattr(self.usage_point_config, "consumption_detail")
                and self.usage_point_config.consumption_detail
            ):
                title(f"[{self.usage_point_id}] Importation de la consommation détaillée du {date}:")
                result["consumption_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                ).fetch(date)
            elif (
                target == "production"
                and hasattr(self.usage_point_config, "production")
                and self.usage_point_config.production
            ):
                title(f"[{self.usage_point_id}] Importation de la production journalière du {date}:")
                result["production"] = Daily(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production",
                ).fetch(date)
            elif (
                target == "production_detail"
                and hasattr(self.usage_point_config, "production_detail")
                and self.usage_point_config.production_detail
            ):
                title(f"[{self.usage_point_id}] Importation de la production détaillée du {date}:")
                result["production_detail"] = Detail(
                    headers=self.headers,
                    usage_point_id=self.usage_point_id,
                    measure_type="production",
                ).fetch(date)
            else:
                return {"error": "true", "notif": "Target inconnue.", "result": ""}

            if "error" in result[target] and result[target]["error"]:
                data = {
                    "error": "true",
                    "notif": result[target]["notif"],
                    "result": {
                        "value": 0,
                        "date": date,
                        "hc": "-",
                        "hp": "-",
                        "fail_count": result[target]["fail_count"],
                    },
                }
                if "event_date" in result[target]:
                    data["result"]["event_date"] = result[target]["event_date"]
                return data
            if target in result and "value" in result[target]:
                data = {
                    "error": "false",
                    "notif": f"Importation de la {target} journalière du {date}",
                    "result": {
                        "value": result[target]["value"],
                        "date": result[target]["date"],
                        "fail_count": 0,
                    },
                }
                if "hc" in result[target]:
                    data["result"]["hc"] = (result[target]["hc"],)
                if "hp" in result[target]:
                    data["result"]["hp"] = (result[target]["hp"],)
                if "event_date" in result[target]:
                    data["result"]["event_date"] = result[target]["event_date"]
            else:
                data = {
                    "error": "false",
                    "notif": f'Importation de la "{target}" du {date}',
                    "result": {"value": 0, "date": 0, "hc": "-", "hp": "-", "fail_count": 0},
                }
            return data

    def blacklist(self, target, date):  # noqa: C901
        """Blacklist the specified target for the given date.

        Args:
            target (str): The target to blacklist.
            date (str): The date to blacklist.

        Returns:
            dict: A dictionary containing the result of the blacklist operation.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            result = {}
            if target == "consumption":
                if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                    title(f"[{self.usage_point_id}] Blacklist de la consommation journalière du {date}:")
                    result["consumption"] = Daily(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 1)
            elif target == "consumption_max_power":
                if (
                    hasattr(self.usage_point_config, "consumption_max_power")
                    and self.usage_point_config.consumption_max_power
                ):
                    title(f"[{self.usage_point_id}] Blacklist de la puissance maximum du {date}:")
                    result["consumption_max_power"] = Power(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 1)
            elif target == "consumption_detail":
                if (
                    hasattr(self.usage_point_config, "consumption_detail")
                    and self.usage_point_config.consumption_detail
                ):
                    title(f"[{self.usage_point_id}] Blacklist de la consommation détaillée du {date}:")
                    result["consumption_detail"] = Detail(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 1)
            elif target == "production":
                if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                    title(f"[{self.usage_point_id}] Blacklist de la production journalière du {date}:")
                    result["production"] = Daily(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                        measure_type="production",
                    ).blacklist(date, 1)
            elif target == "production_detail":
                if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                    title(f"[{self.usage_point_id}] Blacklist de la production détaillée du {date}:")
                    result["production_detail"] = Detail(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                        measure_type="production",
                    ).blacklist(date, 1)
            else:
                return {"error": "true", "notif": "Target inconnue.", "result": ""}
            if not result[target]:
                return {
                    "error": "true",
                    "notif": "Erreur lors du traitement.",
                    "result": result[target],
                }
            return {
                "error": "false",
                "notif": f"Blacklist de la {target} journalière du {date}",
                "result": result[target],
            }

    def whitelist(self, target, date):  # noqa: C901
        """Whitelist the specified target for the given date.

        Args:
            target (str): The target to whitelist.
            date (str): The date to whitelist.

        Returns:
            dict: A dictionary containing the result of the whitelist operation.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            result = {}
            if target == "consumption":
                if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                    title(f"[{self.usage_point_id}] Whitelist de la consommation journalière du {date}:")
                    result["consumption"] = Daily(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 0)
            elif target == "consumption_max_power":
                if (
                    hasattr(self.usage_point_config, "consumption_max_power")
                    and self.usage_point_config.consumption_max_power
                ):
                    title(f"[{self.usage_point_id}] Whitelist de la puissance maximale journalière du {date}:")
                    result["consumption_max_power"] = Power(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 0)
            elif target == "consumption_detail":
                if (
                    hasattr(self.usage_point_config, "consumption_detail")
                    and self.usage_point_config.consumption_detail
                ):
                    title(f"[{self.usage_point_id}] Whitelist de la consommation détaillée du {date}:")
                    result["consumption_detail"] = Detail(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                    ).blacklist(date, 0)
            elif target == "production":
                if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                    title(f"[{self.usage_point_id}] Whitelist de la production journalière du {date}:")
                    result["production"] = Daily(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                        measure_type="production",
                    ).blacklist(date, 0)
            elif target == "production_detail":
                if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                    title(f"[{self.usage_point_id}] Whitelist de la production détaillée du {date}:")
                    result["production_detail"] = Detail(
                        headers=self.headers,
                        usage_point_id=self.usage_point_id,
                        measure_type="production",
                    ).blacklist(date, 0)
            else:
                return {"error": "true", "notif": "Target inconnue.", "result": ""}
            if not result[target]:
                return {
                    "error": "true",
                    "notif": "Erreur lors du traitement.",
                    "result": result[target],
                }
            return {
                "error": "false",
                "notif": f"Whitelist de la {target} journalière du {date}",
                "result": result[target],
            }

    def import_data(self, target=None):
        """Import data for the specified target.

        Args:
            target (str, optional): The target to import data for. Defaults to None.

        Returns:
            dict: A dictionary containing the result of the import data operation.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            result = Job(self.usage_point_id).job_import_data(wait=False, target=target)
            if not result:
                return {
                    "error": "true",
                    "notif": "Erreur lors du traitement.",
                    "result": result,
                }
            else:
                return {
                    "error": "false",
                    "notif": "Récupération de la consommation/production.",
                    "result": result,
                }

    def new_account(self, configs):
        """Add a new account.

        Args:
            configs (dict): A dictionary containing the configuration for the new account.

        Returns:
            dict: A dictionary containing the output of the new account operation.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            output = UsagePoint()
            self.usage_point_id = configs["usage_point_id"]
            title(f"[{self.usage_point_id}] Ajout d'un nouveau point de livraison:")
            if not hasattr(APP_CONFIG.myelectricaldata.usage_point_config, self.usage_point_id):
                APP_CONFIG.myelectricaldata.new(self.usage_point_id)
            print(APP_CONFIG.myelectricaldata.usage_point_config[self.usage_point_id])
            for key, value in configs.items():
                if key != "usage_point_id":
                    setattr(
                        APP_CONFIG.myelectricaldata.usage_point_config[self.usage_point_id], key, check_format(value)
                    )
            return output

    def configuration(self, configs):
        """Change the configuration for the specified usage point.

        Args:
            configs (dict): A dictionary containing the new configuration values.

        Returns:
            dict: A dictionary containing the updated configuration values.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            title(f"[{self.usage_point_id}] Changement de configuration:")
            for key, value in configs.items():
                setattr(APP_CONFIG.myelectricaldata.usage_point_config[self.usage_point_id], key, check_format(value))

    def datatable(self, measurement_direction, args: Request):
        """Retrieve datatable for the specified measurement direction.

        Args:
            measurement_direction (str): The measurement direction.
            args (object): The arguments.

        Returns:
            dict: A dictionary containing the datatable result.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            records_total = 0
            args = args._query_params  # noqa: SLF001 # pylint: disable=W0212
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
                records_total = DatabaseDaily(self.usage_point_id, "consumption").get_count()
                col_spec = {
                    0: "date",
                    1: "value",
                    2: "value",
                    3: "value",
                    4: "value",
                    5: "fail_count",
                    6: "cache",
                    7: "import_clean",
                    8: "blacklist",
                }
                all_data = DatabaseDaily(self.usage_point_id, "consumption").get_datatable(
                    order_column=col_spec[order_column],
                    order_dir=order_dir,
                    search=search,
                )
                data = self.datatable_daily(all_data, start_index, end_index, measurement_direction)

            elif measurement_direction == "consumption_detail":
                records_total = DatabaseDetail(self.usage_point_id, "consumption").get_count()
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
                all_data = DatabaseDetail(self.usage_point_id, "consumption").get_datatable(
                    order_column=col_spec[order_column],
                    order_dir=order_dir,
                    search=search,
                )
                data = self.datatable_detail(all_data, start_index, end_index, measurement_direction)

            elif measurement_direction == "production":
                records_total = DatabaseDaily(self.usage_point_id, "production").get_count()
                col_spec = {
                    0: "date",
                    1: "value",
                    2: "value",
                    3: "fail_count",
                    4: "cache",
                    5: "import_clean",
                    6: "blacklist",
                }
                all_data = DatabaseDaily(self.usage_point_id, "consumption").get_datatable(
                    order_column=col_spec[order_column],
                    order_dir=order_dir,
                    search=search,
                )
                data = self.datatable_daily(all_data, start_index, end_index, measurement_direction)
            elif measurement_direction == "production_detail":
                records_total = DatabaseDetail(self.usage_point_id, "production").get_count()
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
                all_data = DatabaseDetail(self.usage_point_id, "production").get_datatable(
                    order_column=col_spec[order_column],
                    order_dir=order_dir,
                    search=search,
                )
                data = self.datatable_detail(all_data, start_index, end_index, measurement_direction)
            elif measurement_direction == "consumption_max_power":
                records_total = DatabaseMaxPower(self.usage_point_id).get_daily_count()
                col_spec = {
                    0: "date",
                    1: "date",
                    2: "value",
                    3: "value",
                    4: "value",
                    5: "fail_count",
                    6: "cache",
                    7: "import_clean",
                    8: "blacklist",
                }
                all_data = DatabaseMaxPower(self.usage_point_id).get_daily_datatable(
                    order_column=col_spec[order_column],
                    order_dir=order_dir,
                    search=search,
                )
                data = self.datatable_max_power(all_data, start_index, end_index)
            result = {
                "draw": draw + 1,
                "recordsTotal": records_total,
                "recordsFiltered": len(all_data),
                "data": data,
            }
            return result

    def datatable_button(self, measurement_direction, db_data):
        """Generate HTML code for datatable buttons based on measurement direction and database data.

        Args:
            measurement_direction (str): The measurement direction.
            db_data (object): The database data.

        Returns:
            dict: The generated HTML code for the buttons.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
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
    <div id="{measurement_direction}_import_{date_text}" title="{measurement_direction}"
    name="import_{self.usage_point_id}_{date_text}"
    class="datatable_button datatable_button_import {btn_import_disable}"
    style="{btn_import}">
        <input type="button" value="Importer">
    </div>
    <div id="{measurement_direction}_reset_{date_text}" title="{measurement_direction}"
    name="reset_{self.usage_point_id}_{date_text}" class="datatable_button" style="{btn_reset}">
        <input type="button" value="Vider">
    </div>
            """

            blacklist_html = f"""
    <div class="datatable_button datatable_blacklist {btn_blacklist_disable}" title="{measurement_direction}"
    id="{measurement_direction}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}"
    style="{btn_blacklist}">
        <input type="button" value="Blacklist">
    </div>
    <div class="datatable_button datatable_whitelist" title="{measurement_direction}"
    id="{measurement_direction}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}"
    style="{btn_whitelist}">
        <input type="button"  value="Whitelist">
    </div>
            """

            btn = {"cache": cache_html, "blacklist": blacklist_html}
            return btn

    def datatable_daily(self, all_data, start_index, end_index, measurement_direction):
        """Generate the HTML code for the daily datatable based on the provided data.

        Args:
            all_data (list): The list of database data.
            start_index (int): The start index of the datatable.
            end_index (int): The end index of the datatable.
            measurement_direction (str): The measurement direction.

        Returns:
            list: The generated HTML code for the daily datatable.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            index = 0
            result = []
            for db_data in all_data:
                if start_index <= index <= end_index:
                    date_text = db_data.date.strftime(self.date_format)
                    target = "daily"
                    # VALUE
                    conso_w = f"""<div id="{measurement_direction}_conso_w_{date_text}">{db_data.value}</div>"""
                    conso_kw = (
                        f"""<div id="{measurement_direction}_conso_kw_{date_text}">{db_data.value / 1000}</div>"""
                    )
                    fail_count = (
                        f"""<div id="{measurement_direction}_fail_count_{date_text}">{db_data.fail_count}</div>"""
                    )
                    # CACHE STATE
                    if db_data.fail_count == 0:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                        )
                    else:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                        )
                    tempo = DatabaseTempo().get_range(db_data.date, db_data.date)
                    if tempo and tempo[0]:
                        if tempo[0].color == "RED":
                            temp_color = f"""
<div id="{measurement_direction}_tempo_{target}_{date_text}" class="tempo_red">2</div>"""
                        elif tempo[0].color == "WHITE":
                            temp_color = f"""
<div id="{measurement_direction}_tempo_{target}_{date_text}" class="tempo_white">1</div>"""
                        else:
                            temp_color = f"""
<div id="{measurement_direction}_tempo_{target}_{date_text}" class="tempo_blue">0</div>"""
                    else:
                        temp_color = f'<div id="{measurement_direction}_tempo_{target}_{date_text}" class="">-</div>'
                    hc = Stat(self.usage_point_id, "consumption").get_daily(db_data.date, "hc")
                    if hc == 0:
                        hc = "-"
                    else:
                        hc = hc / 1000
                    hp = Stat(self.usage_point_id, "consumption").get_daily(db_data.date, "hp")
                    if hp == 0:
                        hp = "-"
                    else:
                        hp = hp / 1000
                    hc_kw = f'<div id="{measurement_direction}_hc_{target}_{date_text}" class="">{hc}</div>'
                    hp_kw = f'<div id="{measurement_direction}_hp_{target}_{date_text}" class="">{hp}</div>'
                    if measurement_direction == "consumption":
                        day_data = [
                            date_text,
                            conso_w,
                            conso_kw,
                            hc_kw,
                            hp_kw,
                            temp_color,
                            fail_count,
                            cache_state,
                            self.datatable_button(measurement_direction, db_data)["cache"],
                            self.datatable_button(measurement_direction, db_data)["blacklist"],
                        ]
                    else:
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
        """Generate the datatable for the detailed view of the electrical data.

        Args:
            all_data (list): List of all data.
            start_index (int): Start index of the data.
            end_index (int): End index of the data.
            measurement_direction (str): Measurement direction.

        Returns:
            list: Resulting datatable.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            index = 0
            result = []
            for db_data in all_data:
                if start_index <= index <= end_index:
                    date_text = db_data.date.strftime(self.date_format)
                    date_hour = db_data.date.strftime("%H:%M:%S")
                    target = "detail"
                    # VALUE
                    conso_w = f"""<div id="{measurement_direction}_conso_w_{date_text}">{db_data.value}</div>"""
                    conso_kw = (
                        f"""<div id="{measurement_direction}_conso_kw_{date_text}">{db_data.value / 1000}</div>"""
                    )
                    fail_count = (
                        f"""<div id="{measurement_direction}_fail_count_{date_text}">{db_data.fail_count}</div>"""
                    )
                    # CACHE STATE
                    if db_data.fail_count == 0:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                        )
                    else:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                        )
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
        """Generate the datatable for the maximum power data.

        Args:
            all_data (list): List of all data.
            start_index (int): Start index of the data.
            end_index (int): End index of the data.

        Returns:
            list: Resulting datatable.
        """
        with APP_CONFIG.tracer.start_as_current_span(f"{__name__}.{inspect.currentframe().f_code.co_name}"):
            index = 0
            result = []
            measurement_direction = "consumption_max_power"
            event_date = ""
            target = "daily"
            contract = DatabaseContracts(self.usage_point_id).get()
            if hasattr(contract, "subscribed_power") and contract.subscribed_power is not None:
                max_power = int(contract.subscribed_power.split(" ")[0]) * 1000
            else:
                max_power = 999000
            for db_data in all_data:
                if start_index <= index <= end_index:
                    date_text = db_data.date.strftime(self.date_format)
                    ampere = f"{round(int(db_data.value) / 230, 2)}"
                    if isinstance(db_data.event_date, datetime):
                        event_date = db_data.event_date.strftime("%H:%M:%S")
                    # VALUE
                    if max_power <= int(db_data.value):
                        style = 'style="color:#FF0000; font-weight:bolder"'
                    elif (max_power * 90 / 100) <= db_data.value:
                        style = 'style="color:#FFB600; font-weight:bolder"'
                    else:
                        style = ""
                    data_text_event_date = f"""<div id="{measurement_direction}_conso_event_date_{date_text}"
                    {style}>{event_date}</div>"""
                    conso_w = (
                        f"""<div id="{measurement_direction}_conso_w_{date_text}" {style}>{db_data.value}</div>"""
                    )
                    conso_kw = f"""<div id="{measurement_direction}_conso_kw_{date_text}"
                    {style}>{db_data.value / 1000}</div>"""
                    conso_a = f"""<div id="{measurement_direction}_conso_a_{date_text}" {style}>{ampere}</div>"""
                    fail_count = f"""<div id="{measurement_direction}_fail_count_{date_text}"
                    {style}>{db_data.fail_count}</div>"""

                    # CACHE STATE
                    if db_data.fail_count == 0:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_success">1</div>'
                        )
                    else:
                        cache_state = (
                            f'<div id="{measurement_direction}_icon_{target}_{date_text}" class="icon_failed">0</div>'
                        )
                    day_data = [
                        date_text,
                        data_text_event_date,
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
