import __main__ as app
from datetime import datetime

from dateutil.relativedelta import relativedelta
from models.stat import Stat


class ExportMqtt:

    def __init__(self, usage_point_id, measurement_direction="consumption"):
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        self.date_format = "%Y-%m-%d"
        self.stat = Stat(self.usage_point_id, measurement_direction)

    def status(self):
        app.LOG.title(f"[{self.usage_point_id}] Statut du compte.")
        usage_point_id_config = app.DB.get_usage_point(self.usage_point_id)
        # consentement_expiration_date = usage_point_id_config.consentement_expiration.strftime("%Y-%m-%d %H:%M:%S")
        if hasattr(usage_point_id_config,
                   "consentement_expiration") and usage_point_id_config.consentement_expiration is not None:
            consentement_expiration_date = usage_point_id_config.consentement_expiration.strftime("%Y-%m-%d %H:%M:%S")
        else:
            consentement_expiration_date = ""
        if hasattr(usage_point_id_config,
                   "call_number") and usage_point_id_config.call_number is not None:
            call_number = usage_point_id_config.call_number
        else:
            call_number = ""
        if hasattr(usage_point_id_config,
                   "quota_reached") and usage_point_id_config.quota_reached is not None:
            quota_reached = usage_point_id_config.quota_reached
        else:
            quota_reached = ""
        if hasattr(usage_point_id_config,
                   "quota_limit") and usage_point_id_config.quota_limit is not None:
            quota_limit = usage_point_id_config.quota_limit
        else:
            quota_limit = ""
        if hasattr(usage_point_id_config,
                   "quota_reset_at") and usage_point_id_config.quota_reset_at is not None:
            quota_reset_at = usage_point_id_config.quota_reset_at.strftime(
                "%Y-%m-%d %H:%M:%S"),
        else:
            quota_reset_at = ""
        if hasattr(usage_point_id_config,
                   "last_call") and usage_point_id_config.last_call is not None:
            last_call = usage_point_id_config.last_call.strftime(
                "%Y-%m-%d %H:%M:%S"),
        else:
            last_call = ""
        if hasattr(usage_point_id_config,
                   "ban") and usage_point_id_config.ban is not None:
            ban = usage_point_id_config.ban
        else:
            ban = ""
        consentement_expiration = {
            f"{self.usage_point_id}/status/consentement_expiration": consentement_expiration_date,
            f"{self.usage_point_id}/status/call_number": str(call_number),
            f"{self.usage_point_id}/status/quota_reached": str(quota_reached),
            f"{self.usage_point_id}/status/quota_limit": str(quota_limit),
            f"{self.usage_point_id}/status/quota_reset_at": str(quota_reset_at),
            f"{self.usage_point_id}/status/last_call": str(last_call),
            f"{self.usage_point_id}/status/ban": str(ban)
        }
        # print(consentement_expiration)
        app.MQTT.publish_multiple(consentement_expiration)
        app.LOG.log(" => Finish")

    def contract(self):
        app.LOG.title(f"[{self.usage_point_id}] Exportation de données dans MQTT.")

        app.LOG.log("Génération des messages du contrat")
        contract_data = app.DB.get_contract(self.usage_point_id)
        if hasattr(contract_data, "__table__"):
            output = {}
            for column in contract_data.__table__.columns:
                output[f"{self.usage_point_id}/contract/{column.name}"] = str(getattr(contract_data, column.name))
            app.MQTT.publish_multiple(output)
            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => Failed")

    def address(self):
        app.LOG.log(f"[{self.usage_point_id}] Génération des messages d'addresse")
        address_data = app.DB.get_addresse(self.usage_point_id)
        if hasattr(address_data, "__table__"):
            output = {}
            for column in address_data.__table__.columns:
                output[f"{self.usage_point_id}/address/{column.name}"] = str(getattr(address_data, column.name))
            app.MQTT.publish_multiple(output)
            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => Failed")

    def daily_annual(self, price):
        app.LOG.log("Génération des données annuelles")
        date_range = app.DB.get_daily_date_range(self.usage_point_id)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = datetime.combine(date_end.replace(month=1).replace(day=1),
                                                  datetime.min.time())
            finish = False
            while not finish:
                year = int(date_begin_current.strftime('%Y'))
                get_daily_year = self.stat.get_year(year=year)
                get_daily_month = self.stat.get_month(year=year)
                get_daily_week = self.stat.get_week(year=year)
                sub_prefix = f"{self.usage_point_id}/{self.measurement_direction}/annual/{year}"
                mqtt_data = {
                    # thisYear
                    f"{sub_prefix}/thisYear/dateBegin": get_daily_year["begin"],
                    f"{sub_prefix}/thisYear/dateEnd": get_daily_year["end"],
                    f"{sub_prefix}/thisYear/base/Wh": get_daily_year["value"],
                    f"{sub_prefix}/thisYear/base/kWh": round(get_daily_year["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/base/euro": round(get_daily_year["value"] / 1000 * price, 2),
                    # thisMonth
                    f"{sub_prefix}/thisMonth/dateBegin": get_daily_month["begin"],
                    f"{sub_prefix}/thisMonth/dateEnd": get_daily_month["end"],
                    f"{sub_prefix}/thisMonth/base/Wh": get_daily_month["value"],
                    f"{sub_prefix}/thisMonth/base/kWh": round(get_daily_month["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/base/euro": round(get_daily_month["value"] / 1000 * price, 2),
                    # thisWeek
                    f"{sub_prefix}/thisWeek/dateBegin": get_daily_week["begin"],
                    f"{sub_prefix}/thisWeek/dateEnd": get_daily_week["end"],
                    f"{sub_prefix}/thisWeek/base/Wh": get_daily_week["value"],
                    f"{sub_prefix}/thisWeek/base/kWh": round(get_daily_week["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/base/euro": round(get_daily_week["value"] / 1000 * price, 2),
                }

                for week in range(7):
                    begin = self.stat.daily(week)["begin"]
                    begin_day = datetime.strptime(self.stat.daily(week)["begin"], self.date_format).strftime("%A")
                    end = self.stat.daily(week)["end"]
                    value = self.stat.daily(week)["value"]
                    mqtt_data[f"{sub_prefix}/week/{begin_day}/dateBegin"] = begin
                    mqtt_data[f"{sub_prefix}/week/{begin_day}/dateEnd"] = end
                    mqtt_data[f"{sub_prefix}/week/{begin_day}/base/Wh"] = value
                    mqtt_data[f"{sub_prefix}/week/{begin_day}/base/kWh"] = round(value / 1000, 2)
                    mqtt_data[f"{sub_prefix}/week/{begin_day}/base/euro"] = round(value / 1000 * price, 2)

                for month in range(1, 13):
                    get_daily_month = self.stat.get_month(year=year, month=month)
                    mqtt_data[f"{sub_prefix}/month/{month}/dateBegin"] = get_daily_month["begin"]
                    mqtt_data[f"{sub_prefix}/month/{month}/dateEnd"] = get_daily_month["end"]
                    mqtt_data[f"{sub_prefix}/month/{month}/base/Wh"] = get_daily_month["value"]
                    mqtt_data[f"{sub_prefix}/month/{month}/base/kWh"] = round(get_daily_month["value"] / 1000, 2)
                    mqtt_data[f"{sub_prefix}/month/{month}/base/euro"] = round(get_daily_month["value"] / 1000 * price,
                                                                               2)

                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine(
                    (date_end - relativedelta(years=1)).replace(month=12, day=31), datetime.max.time()
                )
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = date_begin

                app.MQTT.publish_multiple(mqtt_data)

            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => No data")

    def daily_linear(self, price):
        app.LOG.log("Génération des données linéaires journalières.")
        date_range = app.DB.get_daily_date_range(self.usage_point_id)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = date_end - relativedelta(years=1)
            idx = 0
            finish = False
            while not finish:
                if idx == 0:
                    key = "year"
                else:
                    key = f"year-{idx}"
                sub_prefix = f"{self.usage_point_id}/{self.measurement_direction}/linear/{key}"
                get_daily_year_linear = self.stat.get_year_linear(idx, )
                get_daily_month_linear = self.stat.get_month_linear(idx)
                get_daily_week_linear = self.stat.get_week_linear(idx)
                mqtt_data = {
                    # thisYear
                    f"{sub_prefix}/thisYear/dateBegin": get_daily_year_linear["begin"],
                    f"{sub_prefix}/thisYear/dateEnd": get_daily_year_linear["end"],
                    f"{sub_prefix}/thisYear/base/Wh": get_daily_year_linear["value"],
                    f"{sub_prefix}/thisYear/base/kWh": round(get_daily_year_linear["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/base/euro": round(get_daily_year_linear["value"] / 1000 * price, 2),
                    # thisMonth
                    f"{sub_prefix}/thisMonth/dateBegin": get_daily_month_linear["begin"],
                    f"{sub_prefix}/thisMonth/dateEnd": get_daily_month_linear["end"],
                    f"{sub_prefix}/thisMonth/base/Wh": get_daily_month_linear["value"],
                    f"{sub_prefix}/thisMonth/base/kWh": round(get_daily_month_linear["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/base/euro": round(get_daily_month_linear["value"] / 1000 * price, 2),
                    # thisWeek
                    f"{sub_prefix}/thisWeek/dateBegin": get_daily_week_linear["begin"],
                    f"{sub_prefix}/thisWeek/dateEnd": get_daily_week_linear["end"],
                    f"{sub_prefix}/thisWeek/base/Wh": get_daily_week_linear["value"],
                    f"{sub_prefix}/thisWeek/base/kWh": round(get_daily_week_linear["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/base/euro": round(get_daily_week_linear["value"] / 1000 * price, 2),
                }

                # CALCUL NEW DATE
                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine(
                    (date_end - relativedelta(years=1)), datetime.max.time()
                )
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = datetime.combine(date_begin, datetime.min.time())
                idx = idx + 1

                app.MQTT.publish_multiple(mqtt_data)

            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => No data")

    def detail_annual(self, price_hp, price_hc=0):
        app.LOG.log("Génération des données annuelles détaillé.")
        date_range = app.DB.get_daily_date_range(self.usage_point_id)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = datetime.combine(date_end.replace(month=1).replace(day=1),
                                                  datetime.min.time())
            finish = False
            while not finish:
                year = int(date_begin_current.strftime('%Y'))
                month = int(datetime.now().strftime('%m'))
                get_detail_year_hp = self.stat.get_year(year=year, measure_type="HP")
                get_detail_year_hc = self.stat.get_year(year=year, measure_type="HC")
                get_detail_month_hp = self.stat.get_month(year=year, month=month, measure_type="HP")
                get_detail_month_hc = self.stat.get_month(year=year, month=month, measure_type="HC")
                get_detail_week_hp = self.stat.get_week(year=year, month=month, measure_type="HP", )
                get_detail_week_hc = self.stat.get_week(year=year, month=month, measure_type="HC", )
                sub_prefix = f"{self.usage_point_id}/{self.measurement_direction}/annual/{year}"
                mqtt_data = {
                    # thisYear - HP
                    f"{sub_prefix}/thisYear/hp/Wh": get_detail_year_hp["value"],
                    f"{sub_prefix}/thisYear/hp/kWh": round(get_detail_year_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/hp/euro": round(get_detail_year_hp["value"] / 1000 * price_hp, 2),
                    # thisYear - HC
                    f"{sub_prefix}/thisYear/hc/Wh": get_detail_year_hc["value"],
                    f"{sub_prefix}/thisYear/hc/kWh": round(get_detail_year_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/hc/euro": round(get_detail_year_hc["value"] / 1000 * price_hc, 2),
                    # thisMonth - HP
                    f"{sub_prefix}/thisMonth/hp/Wh": get_detail_month_hp["value"],
                    f"{sub_prefix}/thisMonth/hp/kWh": round(get_detail_month_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hp/euro": round(get_detail_month_hp["value"] / 1000 * price_hp, 2),
                    # thisMonth - HC
                    f"{sub_prefix}/thisMonth/hc/Wh": get_detail_month_hc["value"],
                    f"{sub_prefix}/thisMonth/hc/kWh": round(get_detail_month_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hc/euro": round(get_detail_month_hc["value"] / 1000 * price_hc, 2),
                    # thisWeek - HP
                    f"{sub_prefix}/thisWeek/hp/Wh": get_detail_week_hp["value"],
                    f"{sub_prefix}/thisWeek/hp/kWh": round(get_detail_week_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hp/euro": round(get_detail_week_hp["value"] / 1000 * price_hp, 2),
                    # thisWeek - HC
                    f"{sub_prefix}/thisWeek/hc/Wh": get_detail_week_hc["value"],
                    f"{sub_prefix}/thisWeek/hc/kWh": round(get_detail_week_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hc/euro": round(get_detail_week_hc["value"] / 1000 * price_hc, 2),
                }

                for week in range(7):
                    # HP
                    begin_hp_day = (
                        datetime.strptime(self.stat.detail(week, "HP")["begin"], self.date_format).strftime("%A")
                    )
                    value_hp = self.stat.detail(week, "HP")["value"]
                    prefix = f"{sub_prefix}/week/{begin_hp_day}/hp"
                    mqtt_data[f"{prefix}/Wh"] = value_hp
                    mqtt_data[f"{prefix}/kWh"] = round(value_hp / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(value_hp / 1000 * price_hp, 2)
                    # HC
                    begin_hc_day = (
                        datetime.strptime(
                            self.stat.detail(week, "HC")["begin"],
                            self.date_format).strftime("%A")
                    )
                    value_hc = self.stat.detail(week, "HC")["value"]
                    prefix = f"{sub_prefix}/week/{begin_hc_day}/hc"
                    mqtt_data[f"{prefix}/Wh"] = value_hc
                    mqtt_data[f"{prefix}/kWh"] = round(value_hc / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(value_hc / 1000 * price_hc, 2)

                for month in range(12):
                    month = month + 1
                    # HP
                    get_detail_month_hp = self.stat.get_month(year=year, month=month, measure_type="HP")
                    prefix = f"{sub_prefix}/month/{month}/hp"
                    mqtt_data[f"{prefix}/Wh"] = get_detail_month_hp["value"]
                    mqtt_data[f"{prefix}/kWh"] = round(get_detail_month_hp["value"] / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(get_detail_month_hp["value"] / 1000 * price_hp, 2)
                    # HC
                    get_detail_month_hc = self.stat.get_month(year=year, month=month, measure_type="HC")
                    prefix = f"{sub_prefix}/month/{month}/hc"
                    mqtt_data[f"{prefix}/Wh"] = get_detail_month_hc["value"]
                    mqtt_data[f"{prefix}/kWh"] = round(get_detail_month_hc["value"] / 1000, 2)
                    mqtt_data[f"{prefix}/euro"] = round(get_detail_month_hc["value"] / 1000 * price_hc, 2)
                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine(
                    (date_end - relativedelta(years=1)).replace(month=12, day=31), datetime.max.time()
                )
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = date_begin

                app.MQTT.publish_multiple(mqtt_data)

            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => No data")

    def detail_linear(self, price_hp, price_hc=0):
        app.LOG.log("Génération des données linéaires détaillées")
        date_range = app.DB.get_detail_date_range(self.usage_point_id)
        if date_range["begin"] and date_range["end"]:
            date_begin = datetime.combine(date_range["begin"], datetime.min.time())
            date_end = datetime.combine(date_range["end"], datetime.max.time())
            date_begin_current = date_end - relativedelta(years=1)
            idx = 0
            finish = False
            while not finish:
                if idx == 0:
                    key = "year"
                else:
                    key = f"year-{idx}"
                sub_prefix = f"{self.usage_point_id}/{self.measurement_direction}/linear/{key}"
                get_daily_year_linear_hp = self.stat.get_year_linear(idx, "HP")
                get_daily_year_linear_hc = self.stat.get_year_linear(idx, "HC")
                get_detail_month_linear_hp = self.stat.get_month_linear(idx, "HP")
                get_detail_month_linear_hc = self.stat.get_month_linear(idx, "HC")
                get_detail_week_linear_hp = self.stat.get_week_linear(idx, "HP")
                get_detail_week_linear_hc = self.stat.get_week_linear(idx, "HC", )
                mqtt_data = {
                    # thisYear
                    f"{sub_prefix}/thisYear/hp/Wh": get_daily_year_linear_hp["value"],
                    f"{sub_prefix}/thisYear/hp/kWh": round(get_daily_year_linear_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/hp/euro": round(get_daily_year_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisYear/hc/Wh": get_daily_year_linear_hc["value"],
                    f"{sub_prefix}/thisYear/hc/kWh": round(get_daily_year_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisYear/hc/euro": round(get_daily_year_linear_hc["value"] / 1000 * price_hc, 2),
                    # thisMonth
                    f"{sub_prefix}/thisMonth/hp/Wh": get_detail_month_linear_hp["value"],
                    f"{sub_prefix}/thisMonth/hp/kWh": round(get_detail_month_linear_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hp/euro": round(get_detail_month_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisMonth/hc/Wh": get_detail_month_linear_hc["value"],
                    f"{sub_prefix}/thisMonth/hc/kWh": round(get_detail_month_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisMonth/hc/euro": round(get_detail_month_linear_hc["value"] / 1000 * price_hc, 2),
                    # thisWeek
                    f"{sub_prefix}/thisWeek/hp/Wh": get_detail_week_linear_hp["value"],
                    f"{sub_prefix}/thisWeek/hp/kWh": round(get_detail_week_linear_hp["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hp/euro": round(get_detail_week_linear_hp["value"] / 1000 * price_hp, 2),
                    f"{sub_prefix}/thisWeek/hc/Wh": get_detail_week_linear_hc["value"],
                    f"{sub_prefix}/thisWeek/hc/kWh": round(get_detail_week_linear_hc["value"] / 1000, 2),
                    f"{sub_prefix}/thisWeek/hc/euro": round(get_detail_week_linear_hc["value"] / 1000 * price_hc, 2),
                }

                # CALCUL NEW DATE
                if date_begin_current == date_begin:
                    finish = True
                date_end = datetime.combine(
                    (date_end - relativedelta(years=1)), datetime.max.time()
                )
                date_begin_current = date_begin_current - relativedelta(years=1)
                if date_begin_current < date_begin:
                    date_begin_current = datetime.combine(date_begin, datetime.min.time())
                idx = idx + 1

                app.MQTT.publish_multiple(mqtt_data)

            app.LOG.log(" => Finish")
        else:
            app.LOG.log(" => No data")

    def max_power(self):
        app.LOG.log("Génération des données de puissance max journalières.")
        max_power_data = app.DB.get_daily_max_power_all(self.usage_point_id, order="asc")
        mqtt_data = {}
        contract = app.DB.get_contract(self.usage_point_id)
        max_value = 0
        if hasattr(contract, "subscribed_power"):
            max_value = int(contract.subscribed_power.split(' ')[0]) * 1000
        for data in max_power_data:
            if data.event_date is not None:
                date = data.event_date.strftime("%A")
                sub_prefix = f"{self.usage_point_id}/power_max/{date}"
                mqtt_data[f"{sub_prefix}/date"] = data.event_date.strftime("%Y-%m-%d")
                mqtt_data[f"{sub_prefix}/event_hour"] = data.event_date.strftime("%H:%M:%S")
                mqtt_data[f"{sub_prefix}/value"] = data.value
                value_w = data.value
                if max_value != 0 and max_value >= value_w:
                    mqtt_data[f"{sub_prefix}/threshold_exceeded"] = 0
                else:
                    mqtt_data[f"{sub_prefix}/threshold_exceeded"] = 1
                threshold_usage = int(100 * value_w / max_value)
                mqtt_data[f"{sub_prefix}/percentage_usage"] = threshold_usage
        # print(mqtt_data)
        app.MQTT.publish_multiple(mqtt_data)
