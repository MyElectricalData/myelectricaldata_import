import __main__ as app
from datetime import datetime
from pprint import pprint

from dateutil.relativedelta import relativedelta
from dependencies import daterange
from models.config import get_version
from models.database import Database
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
        if self.usage_point_id is None:
            self.usage_points = DB.get_usage_point_all()
        else:
            self.usage_points = [DB.get_usage_point(self.usage_point_id)]

    def job_import_data(self, target=None):
        for self.usage_point_config in self.usage_points:
            self.usage_point_id = self.usage_point_config.usage_point_id
            LOG.log_usage_point_id(self.usage_point_id)
            try:
                if target == "gateway_status" or target is None:
                    self.get_gateway_status()
                # if target == "account_status" or target is None:
                #     self.get_account_status()
                # if target == "contract" or target is None:
                #     self.get_contract()
                # if target == "addresses" or target is None:
                #     self.get_addresses()
                # if target == "consumption" or target is None:
                #     self.get_consumption()
                # if target == "consumption_detail" or target is None:
                #     self.get_consumption_detail()
                # if target == "production" or target is None:
                #     self.get_production()
                # if target == "production_detail" or target is None:
                #     self.get_production_detail()
            except Exception as e:
                LOG.error(e)
                LOG.error([
                    f"Erreur lors de la récupération des données du point de livraison {self.usage_point_config.usage_point_id}"],
                    [f"Un nouvel essaie aura lien dans {app.CYCLE}s"])

            try:
                if target == "mqtt" or target is None:
                    self.mqtt()
                if target == "home_assistant" or target is None:
                    self.home_assistant()
                if target == "influxdb" or target is None:
                    self.influxdb()
            except Exception as e:
                LOG.error(e)
                LOG.error(
                    [
                        f"Erreur lors de l'exportation des données du point de livraison {self.usage_point_config.usage_point_id}"],
                    [f"Un nouvel essaie aura lien dans {app.CYCLE}s"])
        LOG.finish()

    def header_generate(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': self.usage_point_config.token,
            'call-service': "myelectricaldata",
            'version': get_version()
        }

    def get_gateway_status(self):
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Status de la passerelle :")
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
        LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de coordonnée :")
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
                usage_point_id=self.usage_point_config.usage_point_id,
                config=self.usage_point_config,
            ).get()
        return result

    def get_consumption_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la consommation détaillé :")
            result = Detail(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                config=self.usage_point_config,
            ).get()
        return result

    def get_production(self):
        result = {}
        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production journalière :")
            result = Daily(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                config=self.usage_point_config,
                measure_type="production"
            ).get()
        return result

    def get_production_detail(self):
        result = {}
        if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Récupération de la production détaillé :")
            result = Detail(
                headers=self.header_generate(),
                usage_point_id=self.usage_point_config.usage_point_id,
                config=self.usage_point_config,
                measure_type="production"
            ).get()
        return result

    def mqtt(self):
        if "enable" in self.mqtt_config and self.mqtt_config["enable"]:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Exportation de données dans MQTT.")

            LOG.log("Export contract")
            contract_data = app.DB.get_contract(self.usage_point_id)
            if hasattr(contract_data, "__table__"):
                for column in contract_data.__table__.columns:
                    app.MQTT.publish(f"{self.usage_point_id}/contract/{column.name}",
                                     str(getattr(contract_data, column.name)))
                LOG.log("  => Success")
            else:
                LOG.log("  => Failed")

            LOG.log("Export address")
            address_data = app.DB.get_addresse(self.usage_point_id)
            if hasattr(address_data, "__table__"):
                for column in address_data.__table__.columns:
                    app.MQTT.publish(f"{self.usage_point_id}/address/{column.name}",
                                     str(getattr(address_data, column.name)))
                LOG.log("  => Success")
            else:
                LOG.log("  => Failed")

            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                LOG.log("Export consumption")
                all_consumption = app.DB.get_daily_all(self.usage_point_id, "consumption")
                output = {}
                i = 0
                key = f'year'
                year_index = 0
                for consumption in all_consumption:
                    consumption_date = datetime.strptime(consumption.date, "%Y-%m-%d")
                    consumption_year = consumption_date.strftime("%Y")
                    consumption_month = consumption_date.strftime("%m")
                    # ANNUAL
                    if f"annual/{consumption_year}/dateEnded" not in output:
                        output[f"annual/{consumption_year}/dateEnded"] = consumption.date
                    if f"annual/{consumption_year}/thisYear" not in output:
                        output[f"annual/{consumption_year}/thisYear"] = 0
                    output[f"annual/{consumption_year}/thisYear"] = output[f"annual/{consumption_year}/thisYear"] + int(consumption.value)
                    output[f"annual/{consumption_year}/dateBegin"] = consumption.date
                    if f"annual/{consumption_year}/month/{consumption_month}/value" not in output:

                        output[f"annual/{consumption_year}/month/{consumption_month}/value"] = 0
                    output[f"annual/{consumption_year}/month/{consumption_month}/value"] = output[f"annual/{consumption_year}/month/{consumption_month}/value"] + int(consumption.value)
                    output[f"linear/{key}/dateBegin"] = consumption.date
                    # THIS YEAR
                    if f"linear/{key}/thisYear" not in output:
                        output[f"linear/{key}/thisYear"] = 0
                    output[f"linear/{key}/thisYear"] = output[f"linear/{key}/thisYear"] + int(consumption.value)
                    # CURRENT WEEK
                    day = 1
                    while day <= 7:
                        year = 0
                        while year <= 4:
                            if consumption_date in daterange(
                                    (datetime.now() - relativedelta(weeks=1) - relativedelta(years=year))
                                            .replace(hour=0, minute=0, second=0, microsecond=0),
                                    (datetime.now() - relativedelta(years=year))
                                            .replace(hour=0, minute=0, second=0, microsecond=0)
                            ):
                                output[f"linear/{key}/currentWeek/{consumption_date.strftime('%A')}/date"] = consumption.date
                                output[f"linear/{key}/currentWeek/{consumption_date.strftime('%A')}/value"] = int(consumption.value)
                                if f"linear/{key}/thisWeek" not in output:
                                    output[f"linear/{key}/thisWeek"] = 0
                                output[f"linear/{key}/thisWeek"] = output[f"linear/{key}/thisWeek"] + int(
                                    consumption.value)
                            year = year + 1
                        day = day + 1

                    # THIS MONTH
                    year = 0
                    while year <= 4:
                        if consumption_date in daterange(
                                (datetime.now() - relativedelta(months=1) - relativedelta(years=year))
                                        .replace(hour=0, minute=0, second=0, microsecond=0),
                                (datetime.now() - relativedelta(years=year))
                                        .replace(hour=0, minute=0, second=0, microsecond=0)
                        ):
                            if f"linear/{key}/thisMonth" not in output:
                                output[f"linear/{key}/thisMonth"] = 0
                            output[f"linear/{key}/thisMonth"] = output[f"linear/{key}/thisMonth"] + int(
                                consumption.value)
                        year = year + 1

                    # MONTH
                    output[f"linear/{key}/month/{consumption_month}/year"] = consumption_date.strftime("%Y"),
                    if f"linear/{key}/month/{consumption_month}/value" not in output:
                        output[f"linear/{key}/month/{consumption_month}/value"] = 0
                    output[f"linear/{key}/month/{consumption_month}/value"] = output[f"linear/{key}/month/{consumption_month}/value"] + int(consumption.value)
                    i = i + 1
                    if i == 365:
                        year_index = year_index + 1
                        key = f'year-{year_index}'
                        i = 0

                for topic, value in output.items():
                    app.MQTT.publish(f"{self.usage_point_id}/consumption/{topic}", str(value))

    def home_assistant(self):
        if "enable" in self.home_assistant_config and self.home_assistant_config["enable"]:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Exportation de données dans Home Assistant (via l'auto-discovery MQTT).")
            all_consumption = app.DB.get_daily_all(self.usage_point_id, "consumption")
            # attribution: ''
            # version: 1.5.1
            # versionGit: v1.5.1
            # versionUpdateAvailable: false
            # nbCall: 4
            # typeCompteur: consommation
            # numPDL: '01226049119129'
            # horaireMinCall: 1437
            # activationDate: '2018-08-31'
            # lastUpdate: '2022-11-02T01:33:24.002246'
            # timeLastCall: '2021-11-29T01:45:17.294194'
            # yesterday: 0
            # last_week: 0
            # yesterdayDate: null
            # yesterdayLastYear: 0
            # yesterdayLastYearDate: null
            # yesterdayConsumptionMaxPower: 0
            # day_1_HP: -1
            # day_2_HP: -1
            # day_3_HP: -1
            # day_4_HP: -1
            # day_5_HP: -1
            # day_6_HP: -1
            # day_7_HP: -1
            # day_1_HC: -1
            # day_2_HC: -1
            # day_3_HC: -1
            # day_4_HC: -1
            # day_5_HC: -1
            # day_6_HC: -1
            # day_7_HC: -1
            # dailyweek_cost:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # dailyweek_costHC:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # dailyweek_HC:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # dailyweek:
            #   - '2022-11-01'
            #   - '2022-10-31'
            #   - '2022-10-30'
            #   - '2022-10-29'
            #   - '2022-10-28'
            #   - '2022-10-27'
            #   - '2022-10-26'
            # dailyweek_costHP:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # dailyweek_HP:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # day_1: -1
            # day_2: -1
            # day_3: -1
            # day_4: -1
            # day_5: -1
            # day_6: -1
            # day_7: -1
            # daily:
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            #   - -1
            # halfhourly: []
            # offpeak_hours: []
            # peak_hours: '0.000'
            # peak_offpeak_percent: 0
            # yesterday_HC_cost: '0.000'
            # yesterday_HP_cost: '0.000'
            # daily_cost: '0.00'
            # yesterday_HC: '0.000'
            # yesterday_HP: '0.000'
            # yesterday_HCHP: '0.000'
            # current_week: '0.000'
            # current_week_last_year: '0.000'
            # last_month: '1238.392'
            # last_month_last_year: '1236.381'
            # current_month: '0.000'
            # current_month_last_year: '0.000'
            # last_year: '18702.059'
            # current_year: '0.000'
            # errorLastCall: ''
            # errorLastCallInterne: ''
            # monthly_evolution: '0.163'
            # current_week_evolution: 0
            # current_month_evolution: 0
            # yesterday_evolution: 0
            # subscribed_power: 12 kVA
            # offpeak_hours_enedis: HC (22H38-6H38)
            # yesterday_production: 0
            # unit_of_measurement: kWh
            # friendly_name: myEnedis.01226049119129


        # return result

    def influxdb(self):
        result = {}
        if "enable" in self.influxdb_config and self.influxdb_config["enable"]:
            LOG.title(f"[{self.usage_point_config.usage_point_id}] Exportation de données dans InfluxDB.")
        return result
