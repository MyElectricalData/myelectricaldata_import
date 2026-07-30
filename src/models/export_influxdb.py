import ast
import logging
from datetime import datetime, timedelta

import pytz

from dependencies import title
from init import DB, INFLUXDB
from models.stat import Stat


def forceRound(x, n):
    import decimal

    d = decimal.Decimal(repr(x))
    targetdigit = decimal.Decimal("1e%d" % -n)
    chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
    return float(chopped)


class ExportInfluxDB:
    def __init__(self, influxdb_config, usage_point_config, measurement_direction="consumption"):
        self.influxdb_config = influxdb_config
        self.db = DB
        self.usage_point_config = usage_point_config
        self.usage_point_id = self.usage_point_config.usage_point_id
        self.measurement_direction = measurement_direction
        self.stat = Stat(self.usage_point_id, measurement_direction=measurement_direction)
        self.time_format = "%Y-%m-%dT%H:%M:%SZ"
        if "timezone" not in self.influxdb_config or self.influxdb_config["timezone"] == "UTC":
            self.tz = pytz.UTC
        else:
            self.tz = pytz.timezone(self.influxdb_config["timezone"])

    def daily(self, measurement_direction="consumption"):
        current_month = ""
        if measurement_direction == "consumption":
            price = self.usage_point_config.consumption_price_base
        else:
            price = self.usage_point_config.production_price
        logging.info(f'Envoi des données "{measurement_direction.upper()}" dans influxdb')
        get_daily_all = self.db.get_daily_all(self.usage_point_id)
        get_daily_all_count = len(get_daily_all)
        last_data = self.db.get_daily_last_date(self.usage_point_id, measurement_direction)
        first_data = self.db.get_daily_first_date(self.usage_point_id, measurement_direction)
        if last_data and first_data:
            start = datetime.strftime(last_data, self.time_format)
            end = datetime.strftime(first_data, self.time_format)
            influxdb_data = INFLUXDB.count(start, end, measurement_direction)
            count = 1
            for data in influxdb_data:
                for record in data.records:
                    count += record.get_value()
            if get_daily_all_count != count:
                logging.info(f" Cache : {get_daily_all_count} / InfluxDb : {count}")
                for daily in get_daily_all:
                    date = daily.date
                    # start = datetime.strftime(date, "%Y-%m-%dT00:00:00Z")
                    # end = datetime.strftime(date, "%Y-%m-%dT23:59:59Z")
                    if current_month != date.strftime("%m"):
                        logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
                    # if len(INFLUXDB.get(start, end, measurement_direction)) == 0:
                    watt = daily.value
                    kwatt = watt / 1000
                    euro = kwatt * price
                    INFLUXDB.write(
                        measurement=measurement_direction,
                        date=self.tz.localize(date),
                        tags={
                            "usage_point_id": self.usage_point_id,
                            "year": daily.date.strftime("%Y"),
                            "month": daily.date.strftime("%m"),
                        },
                        fields={
                            "Wh": float(watt),
                            "kWh": float(forceRound(kwatt, 5)),
                            "price": float(forceRound(euro, 5)),
                        },
                    )
                    current_month = date.strftime("%m")
                logging.info(f" => OK")
            else:
                logging.info(f" => Données synchronisées ({count} valeurs)")
        else:
            logging.info(f" => Aucune donnée")

    def detail(self, measurement_direction="consumption"):
        current_month = ""
        measurement = f"{measurement_direction}_detail"
        logging.info(f'Envoi des données "{measurement.upper()}" dans influxdb')
        get_detail_all = self.db.get_detail_all(
            usage_point_id=self.usage_point_id, measurement_direction=measurement_direction
        )
        get_detail_all_count = len(get_detail_all)
        last_data = self.db.get_detail_last_date(self.usage_point_id, measurement_direction)
        first_data = self.db.get_detail_first_date(self.usage_point_id, measurement_direction)
        if last_data and first_data:
            start = datetime.strftime(last_data, self.time_format)
            end = datetime.strftime(first_data, self.time_format)
            influxdb_data = INFLUXDB.count(start, end, measurement)
            count = 1
            for data in influxdb_data:
                for record in data.records:
                    count += record.get_value()

            # print(len(get_detail_all))
            # print(count)
            if get_detail_all_count != count:
                logging.info(f" Cache : {get_detail_all_count} / InfluxDb : {count}")
                for index, detail in enumerate(get_detail_all):
                    date = detail.date
                    # start = datetime.strftime(date, self.time_format)
                    if current_month != date.strftime("%m"):
                        logging.info(f" - {date.strftime('%Y')}-{date.strftime('%m')}")
                    # if index < (len(get_detail_all) - 1):
                    #     next_item = get_detail_all[index + 1]
                    #     end = datetime.strftime(next_item.date, self.time_format)
                    # else:
                    #     end = datetime.strftime(date, "%Y-%m-%dT23:59:59Z")
                    # if len(INFLUXDB.get(start, end, measurement)) == 0:
                    watt = detail.value
                    kwatt = watt / 1000
                    watth = watt / (60 / detail.interval)
                    kwatth = watth / 1000
                    if measurement_direction == "consumption":
                        measure_type = self.stat.get_mesure_type(date)
                        if measure_type == "HP":
                            euro = kwatth * self.usage_point_config.consumption_price_hp
                        else:
                            euro = kwatth * self.usage_point_config.consumption_price_hc
                    else:
                        euro = kwatth * self.usage_point_config.production_price
                    INFLUXDB.write(
                        measurement=measurement,
                        date=self.tz.localize(date),
                        tags={
                            "usage_point_id": self.usage_point_id,
                            "year": detail.date.strftime("%Y"),
                            "month": detail.date.strftime("%m"),
                            "internal": detail.interval,
                            "measure_type": measure_type,
                        },
                        fields={
                            "W": float(watt),
                            "kW": float(forceRound(kwatt, 5)),
                            "Wh": float(watth),
                            "kWh": float(forceRound(kwatth, 5)),
                            "price": float(forceRound(euro, 5)),
                        },
                    )
                    current_month = date.strftime("%m")
                logging.info(f" => OK")
            else:
                logging.info(f" => Données synchronisées ({count} valeurs)")
        else:
            logging.info(f" => Aucune donnée")

    def tempo(self):
        """Export Tempo (measurement "tempo").

        One point per day known in the cache: the `color` field (as before). On the current
        day's point only, extra fields are added (same measurement/tags/timestamp: InfluxDB
        merges the fields): `color_tomorrow` (tomorrow's color), `price_<color>` (the 6
        prices, EUR/kWh, from `tempo_config.price`) and `days_<color>` (days consumed per
        color counter, from `tempo_config.days`).
        """
        measurement = "tempo"
        logging.info('Envoi des données "TEMPO" dans influxdb')
        tempo_data = self.db.get_tempo()
        if tempo_data:
            today = datetime.combine(datetime.now(), datetime.min.time())
            for data in tempo_data:
                fields = {"color": data.color}
                if data.date == today:
                    tempo_price = self.db.get_tempo_config("price")
                    if tempo_price:
                        for color, price in tempo_price.items():
                            fields[f"price_{color}"] = float(price)
                    tempo_days = self.db.get_tempo_config("days")
                    if tempo_days:
                        for color, days in tempo_days.items():
                            fields[f"days_{color}"] = int(days)
                    tomorrow = today + timedelta(days=1)
                    tempo_tomorrow = self.db.get_tempo_range(tomorrow, tomorrow)
                    if tempo_tomorrow:
                        fields["color_tomorrow"] = tempo_tomorrow[0].color
                INFLUXDB.write(
                    measurement=measurement,
                    date=self.tz.localize(data.date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                    },
                    fields=fields,
                )
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def ecowatt(self):
        measurement = "ecowatt"
        logging.info(f'Envoi des données "ECOWATT" dans influxdb')
        ecowatt_data = self.db.get_ecowatt()
        if ecowatt_data:
            for data in ecowatt_data:
                INFLUXDB.write(
                    measurement=f"{measurement}_daily",
                    date=self.tz.localize(data.date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                    },
                    fields={"value": data.value, "message": data.message},
                )
                data_detail = ast.literal_eval(data.detail)
                for date, value in data_detail.items():
                    date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    INFLUXDB.write(
                        measurement=f"{measurement}_detail",
                        date=self.tz.localize(date),
                        tags={
                            "usage_point_id": self.usage_point_id,
                        },
                        fields={"value": value},
                    )
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def max_power(self):
        """Export the daily peak power (measurement "power_max").

        One point per day available in the cache (`consumption_daily_max_power`): the peak
        power in VA, the exact timestamp of that peak, and the usage percentage against the
        contract's subscribed power (when known).
        """
        measurement = "power_max"
        logging.info('Envoi des données "POWER MAX" dans influxdb')
        max_power_data = self.db.get_daily_max_power_all(self.usage_point_id, order="asc")
        if max_power_data:
            contract = self.db.get_contract(self.usage_point_id)
            subscribed_power_va = 0
            if hasattr(contract, "subscribed_power") and contract.subscribed_power:
                subscribed_power_va = int(contract.subscribed_power.split(" ")[0]) * 1000
            for data in max_power_data:
                fields = {"value": float(data.value)}
                if data.event_date is not None:
                    fields["event_timestamp"] = data.event_date.strftime("%Y-%m-%dT%H:%M:%S")
                if subscribed_power_va:
                    fields["percentage_usage"] = float(forceRound(100 * data.value / subscribed_power_va, 2))
                INFLUXDB.write(
                    measurement=measurement,
                    date=self.tz.localize(data.date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                    },
                    fields=fields,
                )
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def cost_simulation(self):
        """Export simulated costs (measurement "cost_simulation").

        Source: statistic/price_consumption, a nested JSON {year: {month: {offer:
        {euro,kWh,Wh}}}} with offer among BASE, HC, HP (direct amounts) and TEMPO (amounts
        per sub-period BLUE_HC/BLUE_HP/WHITE_HC/WHITE_HP/RED_HC/RED_HP). One point per
        (year[, month], offer[, TEMPO period]).

        Tag model designed to sum by offer and by year WITHOUT a cartesian product:
        - `granularity` = "year" or "month" distinguishes the yearly total from its 12
          monthly components; summing without filtering on `granularity` would double count.
        - `offer` = BASE / HC / HP / TEMPO; `period` = ALL except for offer=TEMPO where it
          holds the sub-period (BLUE_HC, ...).
        A `sum(euro) group by (year) where granularity="year"` query gives the yearly total
        per offer without having to exclude the monthly rows by hand.
        """
        logging.info('Envoi des données "COST SIMULATION" dans influxdb')
        stat_data = self.db.get_stat(self.usage_point_id, "price_consumption")
        if stat_data:
            price_consumption = ast.literal_eval(stat_data[0].value)
            for year, year_data in price_consumption.items():
                year_int = int(year)
                self._cost_simulation_write(year_int, "00", "year", year_data)
                for month, month_data in year_data.get("month", {}).items():
                    self._cost_simulation_write(year_int, month, "month", month_data)
            logging.info(" => OK")
        else:
            logging.info(" => Pas de donnée")

    def _cost_simulation_write(self, year, month, granularity, data):
        measurement = "cost_simulation"
        date = datetime(year, 1 if granularity == "year" else int(month), 1)
        for offer in ("BASE", "HC", "HP"):
            offer_data = data.get(offer)
            if offer_data:
                INFLUXDB.write(
                    measurement=measurement,
                    date=self.tz.localize(date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                        "year": str(year),
                        "month": month,
                        "granularity": granularity,
                        "offer": offer,
                        "period": "ALL",
                    },
                    fields={
                        "euro": float(offer_data["euro"]),
                        "kWh": float(offer_data["kWh"]),
                        "Wh": float(offer_data["Wh"]),
                    },
                )
        tempo_data = data.get("TEMPO")
        if tempo_data:
            for period, period_data in tempo_data.items():
                INFLUXDB.write(
                    measurement=measurement,
                    date=self.tz.localize(date),
                    tags={
                        "usage_point_id": self.usage_point_id,
                        "year": str(year),
                        "month": month,
                        "granularity": granularity,
                        "offer": "TEMPO",
                        "period": period,
                    },
                    fields={
                        "euro": float(period_data["euro"]),
                        "kWh": float(period_data["kWh"]),
                        "Wh": float(period_data["Wh"]),
                    },
                )

    def contract(self):
        """Export the contract (measurement "contract").

        A single point in time (timestamp = now), overwritten on every cycle. Source:
        db.get_contract(), already used by ExportMqtt.contract(). The subscribed power is
        also converted to a usable VA value (`subscribed_power_va`, e.g. "15 kVA" -> 15000)
        in addition to the original string.
        """
        measurement = "contract"
        logging.info('Envoi des données "CONTRACT" dans influxdb')
        contract_data = self.db.get_contract(self.usage_point_id)
        if hasattr(contract_data, "__table__"):
            subscribed_power_va = 0
            if contract_data.subscribed_power:
                subscribed_power_va = int(contract_data.subscribed_power.split(" ")[0]) * 1000
            fields = {
                "subscribed_power": contract_data.subscribed_power or "",
                "subscribed_power_va": subscribed_power_va,
                "plan": self.usage_point_config.plan or "",
                "meter_type": contract_data.meter_type or "",
                "segment": contract_data.segment or "",
                "distribution_tariff": contract_data.distribution_tariff or "",
                "contract_status": contract_data.contract_status or "",
                "last_activation_date": contract_data.last_activation_date.strftime("%Y-%m-%d")
                if contract_data.last_activation_date
                else "",
            }
            for i in range(7):
                value = getattr(contract_data, f"offpeak_hours_{i}", None)
                fields[f"offpeak_hours_{i}"] = value or ""
            INFLUXDB.write(
                measurement=measurement,
                date=self.tz.localize(datetime.now()),
                tags={
                    "usage_point_id": self.usage_point_id,
                },
                fields=fields,
            )
            logging.info(" => OK")
        else:
            logging.info(" => ERREUR")

    def address(self):
        """Export the delivery point address (measurement "address").

        A single point in time (timestamp = now), overwritten on every cycle. Source:
        db.get_addresse(), already used by ExportMqtt.address(). Text fields only (street,
        postal code, city, INSEE code): no high-cardinality value as a tag, so no tag other
        than usage_point_id.
        """
        measurement = "address"
        logging.info('Envoi des données "ADDRESS" dans influxdb')
        address_data = self.db.get_addresse(self.usage_point_id)
        if hasattr(address_data, "__table__"):
            INFLUXDB.write(
                measurement=measurement,
                date=self.tz.localize(datetime.now()),
                tags={
                    "usage_point_id": self.usage_point_id,
                },
                fields={
                    "street": address_data.street or "",
                    "postal_code": address_data.postal_code or "",
                    "city": address_data.city or "",
                    "insee_code": address_data.insee_code or "",
                },
            )
            logging.info(" => OK")
        else:
            logging.info(" => ERREUR")

    def health(self):
        """Export the collection health (measurement "collect_health").

        A single point in time (timestamp = now), overwritten on every cycle. Source:
        db.get_usage_point(), already used by ExportMqtt.status(). API call quota used and
        limit, timestamp of the last call, last error, and most importantly
        consentement_days_left: number of days left before the Enedis consent expires (can be
        negative if already expired), computed here so it can be alerted on directly from
        InfluxDB/Grafana without recomputing it on the dashboard side.
        """
        measurement = "collect_health"
        logging.info('Envoi des données "HEALTH" dans influxdb')
        usage_point_data = self.db.get_usage_point(self.usage_point_id)
        if hasattr(usage_point_data, "__table__"):
            fields = {"last_error": usage_point_data.last_error or ""}
            if usage_point_data.quota_limit is not None:
                fields["quota_limit"] = int(usage_point_data.quota_limit)
            if usage_point_data.call_number is not None:
                fields["call_number"] = int(usage_point_data.call_number)
            if usage_point_data.quota_reached is not None:
                fields["quota_reached"] = bool(usage_point_data.quota_reached)
            if usage_point_data.ban is not None:
                fields["ban"] = bool(usage_point_data.ban)
            if usage_point_data.last_call is not None:
                fields["last_call"] = usage_point_data.last_call.strftime("%Y-%m-%dT%H:%M:%S")
            if usage_point_data.consentement_expiration is not None:
                fields["consentement_expiration"] = usage_point_data.consentement_expiration.strftime(
                    "%Y-%m-%dT%H:%M:%S"
                )
                fields["consentement_days_left"] = int(
                    (usage_point_data.consentement_expiration - datetime.now()).days
                )
            INFLUXDB.write(
                measurement=measurement,
                date=self.tz.localize(datetime.now()),
                tags={
                    "usage_point_id": self.usage_point_id,
                },
                fields=fields,
            )
            logging.info(" => OK")
        else:
            logging.info(" => ERREUR")
