"""Manage all database operations."""
import hashlib
import json
import logging
import os
import traceback
from datetime import datetime, timedelta
from os.path import exists

from sqlalchemy import asc, create_engine, delete, desc, func, inspect, select, update
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import MAX_IMPORT_TRY
from db_schema import (
    Addresses,
    Config,
    ConsumptionDaily,
    ConsumptionDailyMaxPower,
    ConsumptionDetail,
    Contracts,
    Ecowatt,
    ProductionDaily,
    ProductionDetail,
    Statistique,
    Tempo,
    TempoConfig,
    UsagePoints,
)
from dependencies import APPLICATION_PATH, APPLICATION_PATH_DATA, get_version, str2bool, title, title_warning

# available_database = ["sqlite", "postgresql", "mysql+pymysql"]
available_database = ["sqlite", "postgresql"]


class Database:
    """Represents a database connection and provides methods for database operations."""

    def __init__(self, config, path=APPLICATION_PATH_DATA):
        """Initialize a Database object.

        Args:
            config (Config): The configuration object.
            path (str, optional): The path to the database. Defaults to APPLICATION_PATH_DATA.
        """
        self.config = config
        self.path = path

        if not self.config.storage_config() or self.config.storage_config().startswith("sqlite"):
            self.db_name = "cache.db"
            self.db_path = f"{self.path}/{self.db_name}"
            self.uri = f"sqlite:///{self.db_path}?check_same_thread=False"
        else:
            self.storage_type = self.config.storage_config().split(":")[0]
            if self.storage_type in available_database:
                self.uri = self.config.storage_config()
            else:
                logging.critical(f"Database {self.storage_type} not supported (only SQLite & PostgresSQL)")

        os.system(f"cd {APPLICATION_PATH}; DB_URL='{self.uri}' alembic upgrade head ")

        self.engine = create_engine(
            self.uri,
            echo=False,
            query_cache_size=0,
            isolation_level="READ UNCOMMITTED",
            poolclass=NullPool,
        )
        self.session = scoped_session(sessionmaker(self.engine, autocommit=True, autoflush=True))
        self.inspector = inspect(self.engine)

        self.lock_file = f"{self.path}/.lock"

        # MIGRATE v7 to v8
        if os.path.isfile(f"{self.path}/enedisgateway.db"):
            title_warning("=> Migration de l'ancienne base de données vers la nouvelle structure.")
            self.migratev7tov8()

    def migratev7tov8(self):
        """Migrates the database from version 7 to version 8."""
        uri = f"sqlite:///{self.path}/enedisgateway.db"
        engine = create_engine(uri, echo=True, query_cache_size=0)
        session = scoped_session(sessionmaker(engine, autocommit=True, autoflush=True))

        for measurement_direction in ["consumption", "production"]:
            logging.warning(f'Migration des "{measurement_direction}_daily"')
            if measurement_direction == "consumption":
                table = ConsumptionDaily
            else:
                table = ProductionDaily
            daily_data = session.execute(f"select * from {measurement_direction}_daily order by date").all()
            current_date = ""
            year_value = 0
            bulk_insert = []
            for daily in daily_data:
                usage_point_id = daily[0]
                date = datetime.strptime(daily[1], "%Y-%m-%d")
                value = daily[2]
                year_value = year_value + value
                bulk_insert.append(
                    table(
                        usage_point_id=usage_point_id,
                        date=date,
                        value=value,
                        blacklist=0,
                        fail_count=0,
                    )
                )
                if current_date != date.strftime("%Y"):
                    logging.warning(f" - {date.strftime('%Y')} => {round(year_value / 1000, 2)}kW")
                    current_date = date.strftime("%Y")
                    year_value = 0
            self.session.add_all(bulk_insert)

            logging.warning(f'Migration des "{measurement_direction}_detail"')
            if measurement_direction == "consumption":
                table = ConsumptionDetail
            else:
                table = ProductionDetail
            detail_data = session.execute(f"select * from {measurement_direction}_detail order by date").all()
            current_date = ""
            day_value = 0
            bulk_insert = []
            for detail in detail_data:
                usage_point_id = detail[0]
                date = datetime.strptime(detail[1], "%Y-%m-%d %H:%M:%S") - timedelta(minutes=30)
                value = detail[2]
                interval = detail[3]
                measure_type = detail[4]
                day_value = day_value + value / (60 / interval)
                bulk_insert.append(
                    table(
                        usage_point_id=usage_point_id,
                        date=date,
                        value=value,
                        interval=interval,
                        measure_type=measure_type,
                        blacklist=0,
                        fail_count=0,
                    )
                )
                if current_date != date.strftime("%m"):
                    logging.warning(f" - {date.strftime('%Y-%m')} => {round(day_value / 1000, 2)}kW")
                    current_date = date.strftime("%m")
                    day_value = 0
            self.session.add_all(bulk_insert)
        os.replace(f"{self.path}/enedisgateway.db", f"{self.path}/enedisgateway.db.migrate")

    def init_database(self):
        """Initialize the database with default values."""
        try:
            logging.info("Configure Databases")
            query = select(Config).where(Config.key == "day")
            day = self.session.scalars(query).one_or_none()
            if day:
                day.value = datetime.now().strftime("%Y-%m-%d")
            else:
                self.session.add(Config(key="day", value=datetime.now().strftime("%Y-%m-%d")))
            logging.info(" => day")
            query = select(Config).where(Config.key == "call_number")
            if not self.session.scalars(query).one_or_none():
                self.session.add(Config(key="call_number", value="0"))
            logging.info(" => call_number")
            query = select(Config).where(Config.key == "max_call")
            if not self.session.scalars(query).one_or_none():
                self.session.add(Config(key="max_call", value="500"))
            logging.info(" => max_call")
            query = select(Config).where(Config.key == "version")
            version = self.session.scalars(query).one_or_none()
            if version:
                version.value = get_version()
            else:
                self.session.add(Config(key="version", value=get_version()))
            logging.info(" => version")
            query = select(Config).where(Config.key == "lock")
            if not self.session.scalars(query).one_or_none():
                self.session.add(Config(key="lock", value="0"))
            logging.info(" => lock")
            query = select(Config).where(Config.key == "lastUpdate")
            if not self.session.scalars(query).one_or_none():
                self.session.add(Config(key="lastUpdate", value=str(datetime.now())))
            logging.info(" => lastUpdate")
            logging.info(" Success")
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            logging.critical("Database initialize failed!")

    def purge_database(self):
        """Purges the SQLite database."""
        logging.separator_warning()
        logging.info("Reset SQLite Database")
        if os.path.exists(f"{self.path}/cache.db"):
            os.remove(f"{self.path}/cache.db")
            logging.info(" => Success")
        else:
            logging.info(" => No cache detected")

    def lock_status(self):
        """Check the lock status of the database.

        Returns:
            bool: True if the database is locked, False otherwise.
        """
        if exists(self.lock_file):
            return True
        else:
            return False

    def lock(self):
        """Locks the database.

        Returns:
            bool: True if the database is locked, False otherwise.
        """
        with open(self.lock_file, "xt") as f:
            f.write(str(datetime.now()))
            f.close()
        return self.lock_status()

    def unlock(self):
        """Unlocks the database.

        Returns:
            bool: True if the database is unlocked, False otherwise.
        """
        if os.path.exists(self.lock_file):
            os.remove(self.lock_file)
        return self.lock_status()

    def clean_database(self, current_usage_point_id):
        """Clean the database by removing unused data.

        Args:
            current_usage_point_id (list): List of current usage point IDs.

        Returns:
            bool: True if the database is cleaned successfully, False otherwise.
        """
        for usage_point in self.get_usage_point_all():
            if usage_point.usage_point_id not in current_usage_point_id:
                logging.warning(f"- Suppression du point de livraison {usage_point.usage_point_id}")
                self.delete_usage_point(usage_point.usage_point_id)
                self.delete_addresse(usage_point.usage_point_id)
                self.delete_daily(usage_point.usage_point_id)
                self.delete_detail(usage_point.usage_point_id)
                self.delete_daily_max_power(usage_point.usage_point_id)
        return True

    def refresh_object(self):
        """Refreshe the ORM objects."""
        title("Refresh ORM Objects")
        self.session.expire_all()

    # ----------------------------------------------------------------------------------------------------------------
    # CONFIG
    # ----------------------------------------------------------------------------------------------------------------
    def get_config(self, key):
        query = select(Config).where(Config.key == key)
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set_config(self, key, value):
        query = select(Config).where(Config.key == key)
        config = self.session.scalars(query).one_or_none()
        if config:
            config.value = json.dumps(value)
        else:
            self.session.add(Config(key=key, value=json.dumps(value)))
        self.session.flush()
        self.session.close()
        self.refresh_object()

    # ----------------------------------------------------------------------------------------------------------------
    # USAGE POINTS
    # ----------------------------------------------------------------------------------------------------------------
    def get_usage_point_all(self):
        query = select(UsagePoints)
        data = self.session.scalars(query).all()
        self.session.close()
        return data

    def get_usage_point(self, usage_point_id):
        query = select(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id)
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def get_usage_point_plan(self, usage_point):
        data = self.get_usage_point(usage_point)
        if data.plan in ["HP/HC"]:
            return "HC/HP"
        return data.plan

    def set_usage_point(self, usage_point_id, data):
        query = select(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()

        if usage_points is not None:
            if "enable" in data and data["enable"] is not None:
                usage_points.enable = str2bool(data["enable"])
            if "name" in data and data["name"] is not None:
                usage_points.name = data["name"]
            if "cache" in data and data["cache"] is not None:
                usage_points.cache = str2bool(data["cache"])
            if "consumption" in data and data["consumption"] is not None:
                usage_points.consumption = str2bool(data["consumption"])
            if "consumption_detail" in data and data["consumption_detail"] is not None:
                usage_points.consumption_detail = str2bool(data["consumption_detail"])
            if "consumption_max_power" in data and data["consumption_max_power"] is not None:
                usage_points.consumption_max_power = str2bool(data["consumption_max_power"])
            if "production" in data and data["production"] is not None:
                usage_points.production = str2bool(data["production"])
            if "production_detail" in data and data["production_detail"] is not None:
                usage_points.production_detail = str2bool(data["production_detail"])
            if "production_price" in data and data["production_price"] is not None:
                usage_points.production_price = data["production_price"]
            if "consumption_price_base" in data and data["consumption_price_base"] is not None:
                usage_points.consumption_price_base = data["consumption_price_base"]
            if "consumption_price_hc" in data and data["consumption_price_hc"] is not None:
                usage_points.consumption_price_hc = data["consumption_price_hc"]
            if "consumption_price_hp" in data and data["consumption_price_hp"] is not None:
                usage_points.consumption_price_hp = data["consumption_price_hp"]
            if "offpeak_hours_0" in data and data["offpeak_hours_0"] is not None:
                usage_points.offpeak_hours_0 = data["offpeak_hours_0"]
            if "offpeak_hours_1" in data and data["offpeak_hours_1"] is not None:
                usage_points.offpeak_hours_1 = data["offpeak_hours_1"]
            if "offpeak_hours_2" in data and data["offpeak_hours_2"] is not None:
                usage_points.offpeak_hours_2 = data["offpeak_hours_2"]
            if "offpeak_hours_3" in data and data["offpeak_hours_3"] is not None:
                usage_points.offpeak_hours_3 = data["offpeak_hours_3"]
            if "offpeak_hours_4" in data and data["offpeak_hours_4"] is not None:
                usage_points.offpeak_hours_4 = data["offpeak_hours_4"]
            if "offpeak_hours_5" in data and data["offpeak_hours_5"] is not None:
                usage_points.offpeak_hours_5 = data["offpeak_hours_5"]
            if "offpeak_hours_6" in data and data["offpeak_hours_6"] is not None:
                usage_points.offpeak_hours_6 = data["offpeak_hours_6"]
            if "plan" in data and data["plan"] is not None:
                usage_points.plan = data["plan"]
            else:
                usage_points.plan = "BASE"
            if "refresh_addresse" in data and data["refresh_addresse"] is not None:
                usage_points.refresh_addresse = str2bool(data["refresh_addresse"])
            if "refresh_contract" in data and data["refresh_contract"] is not None:
                usage_points.refresh_contract = str2bool(data["refresh_contract"])
            if "token" in data and data["token"] is not None:
                usage_points.token = data["token"]
            if "progress" in data and data["progress"] is not None:
                usage_points.progress = data["progress"]
            if "progress_status" in data and data["progress_status"] is not None:
                usage_points.progress_status = data["progress_status"]
            if "consumption_max_date" in data:
                if data["consumption_max_date"] and data["consumption_max_date"] is not None:
                    consumption_max_date = data["consumption_max_date"]
                    if isinstance(consumption_max_date, datetime):
                        usage_points.consumption_max_date = consumption_max_date
                    else:
                        usage_points.consumption_max_date = datetime.strptime(consumption_max_date, "%Y-%m-%d")
            if "consumption_detail_max_date" in data:
                if data["consumption_detail_max_date"] and data["consumption_detail_max_date"] is not None:
                    consumption_detail_max_date = data["consumption_detail_max_date"]
                    if isinstance(consumption_detail_max_date, datetime):
                        usage_points.consumption_detail_max_date = consumption_detail_max_date
                    else:
                        usage_points.consumption_detail_max_date = datetime.strptime(
                            consumption_detail_max_date, "%Y-%m-%d"
                        )
            if "production_max_date" in data:
                if data["production_max_date"] and data["production_max_date"] is not None:
                    production_max_date = data["production_max_date"]
                    if isinstance(production_max_date, datetime):
                        usage_points.production_max_date = production_max_date
                    else:
                        usage_points.production_max_date = datetime.strptime(production_max_date, "%Y-%m-%d")
            if "production_detail_max_date" in data:
                if data["production_detail_max_date"] and data["production_detail_max_date"] is not None:
                    production_detail_max_date = data["production_detail_max_date"]
                    if isinstance(production_detail_max_date, datetime):
                        usage_points.production_detail_max_date = production_detail_max_date
                    else:
                        usage_points.production_detail_max_date = datetime.strptime(
                            production_detail_max_date, "%Y-%m-%d"
                        )
            if "call_number" in data and data["call_number"] is not None:
                usage_points.call_number = data["call_number"]
            if "quota_reached" in data and data["quota_reached"] is not None:
                usage_points.quota_reached = str2bool(data["quota_reached"])
            if "quota_limit" in data and data["quota_limit"] is not None:
                usage_points.quota_limit = data["quota_limit"]
            if "quota_reset_at" in data and data["quota_reset_at"] is not None:
                usage_points.quota_reset_at = data["quota_reset_at"]
            if "last_call" in data and data["last_call"] is not None:
                usage_points.last_call = data["last_call"]
            if "ban" in data and data["ban"] is not None:
                usage_points.ban = str2bool(data["ban"])
            if "consentement_expiration" in data and data["consentement_expiration"] is not None:
                usage_points.consentement_expiration = data["consentement_expiration"]
        else:
            if "enable" in data and data["enable"] is not None:
                enable = data["enable"]
            else:
                enable = True
            if "name" in data and data["name"] is not None:
                name = data["name"]
            else:
                name = ""
            if "cache" in data and data["cache"] is not None:
                cache = data["cache"]
            else:
                cache = True
            if "consumption" in data and data["consumption"] is not None:
                consumption = data["consumption"]
            else:
                consumption = True
            if "consumption_max_power" in data and data["consumption_max_power"] is not None:
                consumption_max_power = data["consumption_max_power"]
            else:
                consumption_max_power = True
            if "consumption_detail" in data and data["consumption_detail"] is not None:
                consumption_detail = data["consumption_detail"]
            else:
                consumption_detail = True
            if "production" in data and data["production"] is not None:
                production = data["production"]
            else:
                production = False
            if "production_detail" in data and data["production_detail"] is not None:
                production_detail = data["production_detail"]
            else:
                production_detail = False
            if "production_price" in data and data["production_price"] is not None:
                production_price = data["production_price"]
            else:
                production_price = 0
            if (
                "consumption_price_base" in data
                and data["consumption_price_base"] is not None
                and data["consumption_price_base"] != ""
            ):
                consumption_price_base = data["consumption_price_base"]
            else:
                consumption_price_base = 0
            if (
                "consumption_price_hc" in data
                and data["consumption_price_hc"] is not None
                and data["consumption_price_hc"] != ""
            ):
                consumption_price_hc = data["consumption_price_hc"]
            else:
                consumption_price_hc = 0
            if (
                "consumption_price_hp" in data
                and data["consumption_price_hp"] is not None
                and data["consumption_price_hp"] != ""
            ):
                consumption_price_hp = data["consumption_price_hp"]
            else:
                consumption_price_hp = 0
            if "offpeak_hours_0" in data and data["offpeak_hours_0"] is not None:
                offpeak_hours_0 = data["offpeak_hours_0"]
            else:
                offpeak_hours_0 = ""
            if "offpeak_hours_1" in data and data["offpeak_hours_1"] is not None:
                offpeak_hours_1 = data["offpeak_hours_1"]
            else:
                offpeak_hours_1 = ""
            if "offpeak_hours_2" in data and data["offpeak_hours_2"] is not None:
                offpeak_hours_2 = data["offpeak_hours_2"]
            else:
                offpeak_hours_2 = ""
            if "offpeak_hours_3" in data and data["offpeak_hours_3"] is not None:
                offpeak_hours_3 = data["offpeak_hours_3"]
            else:
                offpeak_hours_3 = ""
            if "offpeak_hours_4" in data and data["offpeak_hours_4"] is not None:
                offpeak_hours_4 = data["offpeak_hours_4"]
            else:
                offpeak_hours_4 = ""
            if "offpeak_hours_5" in data and data["offpeak_hours_5"] is not None:
                offpeak_hours_5 = data["offpeak_hours_5"]
            else:
                offpeak_hours_5 = ""
            if "offpeak_hours_6" in data and data["offpeak_hours_6"] is not None:
                offpeak_hours_6 = data["offpeak_hours_6"]
            else:
                offpeak_hours_6 = ""
            if "plan" in data and data["plan"] is not None:
                plan = data["plan"]
            else:
                plan = "BASE"
            if "refresh_addresse" in data and data["refresh_addresse"] is not None:
                refresh_addresse = data["refresh_addresse"]
            else:
                refresh_addresse = False
            if "refresh_contract" in data and data["refresh_contract"] is not None:
                refresh_contract = data["refresh_contract"]
            else:
                refresh_contract = False
            if "token" in data and data["token"] is not None:
                token = data["token"]
            else:
                token = ""
            progress = 0
            if "progress" in data and data["progress"] is not None:
                progress = data["progress"]
            progress_status = ""
            if "progress_status" in data and data["progress_status"] is not None:
                progress_status = data["progress_status"]
            consumption_max_date = None
            if "consumption_max_date" in data:
                if not data["consumption_max_date"] or data["consumption_max_date"] is None:
                    consumption_max_date = None
                else:
                    consumption_max_date = data["consumption_max_date"]
                    if not isinstance(consumption_max_date, datetime):
                        consumption_max_date = datetime.strptime(consumption_max_date, "%Y-%m-%d")
            consumption_detail_max_date = None
            if "consumption_detail_max_date" in data:
                if "consumption_detail_max_date" in data or data["consumption_detail_max_date"] is None:
                    if not data["consumption_detail_max_date"] or data["consumption_detail_max_date"] is None:
                        consumption_detail_max_date = None
                    else:
                        consumption_detail_max_date = data["consumption_detail_max_date"]
                        if not isinstance(consumption_detail_max_date, datetime):
                            consumption_detail_max_date = datetime.strptime(consumption_detail_max_date, "%Y-%m-%d")
            production_max_date = None
            if "production_max_date" in data:
                if not data["production_max_date"] or data["production_max_date"] is None:
                    production_max_date = None
                else:
                    production_max_date = data["production_max_date"]
                    if not isinstance(production_max_date, datetime):
                        production_max_date = datetime.strptime(production_max_date, "%Y-%m-%d")
            production_detail_max_date = None
            if "production_detail_max_date" in data:
                if not data["production_detail_max_date"] or data["production_detail_max_date"] is None:
                    production_detail_max_date = None
                else:
                    production_detail_max_date = data["production_detail_max_date"]
                    if isinstance(production_detail_max_date, datetime):
                        production_detail_max_date = production_detail_max_date
                    else:
                        production_detail_max_date = datetime.strptime(production_detail_max_date, "%Y-%m-%d")

            if "call_number" in data and data["call_number"] is not None:
                call_number = data["call_number"]
            else:
                call_number = 0
            if "quota_reached" in data and data["quota_reached"] is not None:
                quota_reached = str2bool(data["quota_reached"])
            else:
                quota_reached = False
            if "quota_limit" in data and data["quota_limit"] is not None:
                quota_limit = data["quota_limit"]
            else:
                quota_limit = 0
            if "quota_reset_at" in data and data["quota_reset_at"] is not None:
                quota_reset_at = data["quota_reset_at"]
            else:
                quota_reset_at = None
            if "last_call" in data and data["last_call"] is not None:
                last_call = data["last_call"]
            else:
                last_call = None
            if "ban" in data and data["ban"] is not None:
                ban = str2bool(data["ban"])
            else:
                ban = False
            if "consentement_expiration" in data and data["consentement_expiration"] is not None:
                consentement_expiration = data["consentement_expiration"]
            else:
                consentement_expiration = None

            self.session.add(
                UsagePoints(
                    usage_point_id=usage_point_id,
                    name=name,
                    cache=str2bool(cache),
                    consumption=str2bool(consumption),
                    consumption_detail=str2bool(consumption_detail),
                    consumption_max_power=str2bool(consumption_max_power),
                    production=str2bool(production),
                    production_detail=str2bool(production_detail),
                    production_price=production_price,
                    consumption_price_base=consumption_price_base,
                    consumption_price_hc=consumption_price_hc,
                    consumption_price_hp=consumption_price_hp,
                    offpeak_hours_0=offpeak_hours_0,
                    offpeak_hours_1=offpeak_hours_1,
                    offpeak_hours_2=offpeak_hours_2,
                    offpeak_hours_3=offpeak_hours_3,
                    offpeak_hours_4=offpeak_hours_4,
                    offpeak_hours_5=offpeak_hours_5,
                    offpeak_hours_6=offpeak_hours_6,
                    plan=plan,
                    refresh_addresse=str2bool(refresh_addresse),
                    refresh_contract=str2bool(refresh_contract),
                    token=token,
                    progress=progress,
                    progress_status=progress_status,
                    enable=str2bool(enable),
                    consumption_max_date=consumption_max_date,
                    consumption_detail_max_date=consumption_detail_max_date,
                    production_max_date=production_max_date,
                    production_detail_max_date=production_detail_max_date,
                    call_number=call_number,
                    quota_reached=str2bool(quota_reached),
                    quota_limit=quota_limit,
                    quota_reset_at=quota_reset_at,
                    last_call=last_call,
                    ban=str2bool(ban),
                    consentement_expiration=consentement_expiration,
                )
            )
        self.session.flush()
        self.session.close()

    def progress(self, usage_point_id, increment):
        query = select(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        usage_points.progress = usage_points.progress + increment
        self.session.close()

    def last_call_update(self, usage_point_id):
        query = select(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        usage_points.last_call = datetime.now()
        self.session.flush()
        self.session.close()

    def usage_point_update(
        self,
        usage_point_id,
        consentement_expiration=None,
        call_number=None,
        quota_reached=None,
        quota_limit=None,
        quota_reset_at=None,
        last_call=None,
        ban=None,
    ):
        query = select(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id)
        usage_points = self.session.scalars(query).one_or_none()
        if consentement_expiration is not None:
            usage_points.consentement_expiration = consentement_expiration
        if call_number is not None:
            usage_points.call_number = call_number
        if quota_reached is not None:
            usage_points.quota_reached = quota_reached
        if quota_limit is not None:
            usage_points.quota_limit = quota_limit
        if quota_reset_at is not None:
            usage_points.quota_reset_at = quota_reset_at
        if last_call is not None:
            usage_points.last_call = last_call
        if ban is not None:
            usage_points.ban = ban
        self.session.flush()
        self.session.close()

    def delete_usage_point(self, usage_point_id):
        self.session.execute(delete(Addresses).where(Addresses.usage_point_id == usage_point_id))
        self.session.execute(delete(Contracts).where(Contracts.usage_point_id == usage_point_id))
        self.session.execute(
            delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.usage_point_id == usage_point_id)
        )
        self.session.execute(delete(ConsumptionDetail).where(ConsumptionDetail.usage_point_id == usage_point_id))
        self.session.execute(delete(ConsumptionDaily).where(ConsumptionDaily.usage_point_id == usage_point_id))
        self.session.execute(delete(ProductionDetail).where(ProductionDetail.usage_point_id == usage_point_id))
        self.session.execute(delete(ProductionDaily).where(ProductionDaily.usage_point_id == usage_point_id))
        self.session.execute(delete(UsagePoints).where(UsagePoints.usage_point_id == usage_point_id))
        self.session.flush()
        self.session.close()
        return True

    def get_error_log(self, usage_point_id):
        data = self.get_usage_point(usage_point_id)
        return data.last_error

    def set_error_log(self, usage_point_id, message):
        values = {UsagePoints.last_error: message}
        self.session.execute(update(UsagePoints, values=values).where(UsagePoints.usage_point_id == usage_point_id))
        self.session.flush()
        return True

    # ----------------------------------------------------------------------------------------------------------------
    # ADDRESSES
    # ----------------------------------------------------------------------------------------------------------------
    def get_addresse(self, usage_point_id):
        query = (
            select(Addresses).join(UsagePoints.relation_addressess).where(UsagePoints.usage_point_id == usage_point_id)
        )
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set_addresse(self, usage_point_id, data, count=0):
        query = (
            select(Addresses).join(UsagePoints.relation_addressess).where(Addresses.usage_point_id == usage_point_id)
        )
        addresses = self.session.scalars(query).one_or_none()
        if addresses is not None:
            addresses.street = data["street"]
            addresses.locality = data["locality"]
            addresses.postal_code = data["postal_code"]
            addresses.insee_code = data["insee_code"]
            addresses.city = data["city"]
            addresses.country = data["country"]
            addresses.geo_points = data["geo_points"]
            addresses.count = count
        else:
            self.session.add(
                Addresses(
                    usage_point_id=usage_point_id,
                    street=data["street"],
                    locality=data["locality"],
                    postal_code=data["postal_code"],
                    insee_code=data["insee_code"],
                    city=data["city"],
                    country=data["country"],
                    geo_points=data["geo_points"],
                    count=count,
                )
            )
        self.session.flush()
        self.session.close()

    def delete_addresse(self, usage_point_id):
        self.session.execute(delete(Addresses).where(Addresses.usage_point_id == usage_point_id))
        self.session.flush()
        self.session.close()
        return True

    # ----------------------------------------------------------------------------------------------------------------
    # CONTRACTS
    # ----------------------------------------------------------------------------------------------------------------
    def get_contract(self, usage_point_id):
        query = (
            select(Contracts).join(UsagePoints.relation_contract).where(UsagePoints.usage_point_id == usage_point_id)
        )
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set_contract(
        self,
        usage_point_id,
        data,
        count=0,
    ):
        query = (
            select(Contracts).join(UsagePoints.relation_contract).where(UsagePoints.usage_point_id == usage_point_id)
        )
        contract = self.session.scalars(query).one_or_none()
        if contract is not None:
            contract.usage_point_status = data["usage_point_status"]
            contract.meter_type = data["meter_type"]
            contract.segment = data["segment"]
            contract.subscribed_power = data["subscribed_power"]
            contract.last_activation_date = data["last_activation_date"]
            contract.distribution_tariff = data["distribution_tariff"]
            contract.offpeak_hours_0 = data["offpeak_hours_0"]
            contract.offpeak_hours_1 = data["offpeak_hours_1"]
            contract.offpeak_hours_2 = data["offpeak_hours_2"]
            contract.offpeak_hours_3 = data["offpeak_hours_3"]
            contract.offpeak_hours_4 = data["offpeak_hours_4"]
            contract.offpeak_hours_5 = data["offpeak_hours_5"]
            contract.offpeak_hours_6 = data["offpeak_hours_6"]
            contract.contract_status = data["contract_status"]
            contract.last_distribution_tariff_change_date = data["last_distribution_tariff_change_date"]
            contract.count = count
        else:
            self.session.add(
                Contracts(
                    usage_point_id=usage_point_id,
                    usage_point_status=data["usage_point_status"],
                    meter_type=data["meter_type"],
                    segment=data["segment"],
                    subscribed_power=data["subscribed_power"],
                    last_activation_date=data["last_activation_date"],
                    distribution_tariff=data["distribution_tariff"],
                    offpeak_hours_0=data["offpeak_hours_0"],
                    offpeak_hours_1=data["offpeak_hours_1"],
                    offpeak_hours_2=data["offpeak_hours_2"],
                    offpeak_hours_3=data["offpeak_hours_3"],
                    offpeak_hours_4=data["offpeak_hours_4"],
                    offpeak_hours_5=data["offpeak_hours_5"],
                    offpeak_hours_6=data["offpeak_hours_6"],
                    contract_status=data["contract_status"],
                    last_distribution_tariff_change_date=data["last_distribution_tariff_change_date"],
                    count=count,
                )
            )
        self.session.flush()
        self.session.close()

    # ----------------------------------------------------------------------------------------------------------------
    # DAILY
    # ----------------------------------------------------------------------------------------------------------------
    def get_daily_all(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        data = self.session.scalars(
            select(table)
            .join(relation)
            .where(UsagePoints.usage_point_id == usage_point_id)
            .order_by(table.date.desc())
        ).all()
        self.session.close()
        return data

    def get_daily_datatable(
        self,
        usage_point_id,
        order_column="date",
        order_dir="asc",
        search=None,
        measurement_direction="consumption",
    ):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily

        sort = asc(order_column) if order_dir == "desc" else desc(order_column)

        yesterday = datetime.combine(datetime.now() - timedelta(days=1), datetime.max.time())
        if search is not None and search != "":
            result = self.session.scalars(
                select(table)
                .join(relation)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where((table.date.like(f"%{search}%")) | (table.value.like(f"%{search}%")))
                .where(table.date <= yesterday)
                .order_by(sort)
            )
        else:
            result = self.session.scalars(
                select(table)
                .join(relation)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where(table.date <= yesterday)
                .order_by(sort)
            )
        return result.all()

    def get_daily_count(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        data = self.session.scalars(
            select([func.count()])
            .select_from(table)
            .join(relation)
            .where(UsagePoints.usage_point_id == usage_point_id)
        ).one_or_none()
        self.session.close()
        return data

    def get_daily_date(self, usage_point_id, date, measurement_direction="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        data = self.session.scalars(select(table).join(relation).where(table.id == unique_id)).first()
        self.session.flush()
        self.session.close()
        return data

    def get_daily_state(self, usage_point_id, date, measurement_direction="consumption"):
        if self.get_daily_date(usage_point_id, date, measurement_direction) is not None:
            return True
        else:
            return False

    def get_daily_last_date(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        current_data = self.session.scalars(
            select(table).join(relation).where(table.usage_point_id == usage_point_id).order_by(table.date)
        ).first()
        self.session.flush()
        self.session.close()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_daily_last(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        current_data = self.session.scalars(
            select(table)
            .join(relation)
            .where(table.usage_point_id == usage_point_id)
            .where(table.value != 0)
            .order_by(table.date.desc())
        ).first()
        self.session.flush()
        self.session.close()
        if current_data is None:
            return False
        else:
            return current_data

    def get_daily_first_date(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        query = select(table).join(relation).where(table.usage_point_id == usage_point_id).order_by(table.date.desc())
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_daily_fail_count(self, usage_point_id, date, measurement_direction="consumption"):
        result = self.get_daily_date(usage_point_id, date, measurement_direction)
        if hasattr(result, "fail_count"):
            return result.fail_count
        else:
            return 0

    def daily_fail_increment(self, usage_point_id, date, measurement_direction="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        query = select(table).join(relation).where(table.id == unique_id)
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        daily = self.session.scalars(query).one_or_none()
        if daily is not None:
            fail_count = int(daily.fail_count) + 1
            if fail_count >= MAX_IMPORT_TRY:
                blacklist = 1
                fail_count = 0
            else:
                blacklist = 0
            daily.id = unique_id
            daily.usage_point_id = usage_point_id
            daily.date = date
            daily.value = 0
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                table(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=0,
                    blacklist=0,
                    fail_count=0,
                )
            )
        self.session.flush()
        return fail_count

    def get_daily_range(self, usage_point_id, begin, end, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        query = (
            select(table)
            .join(relation)
            .where(table.usage_point_id == usage_point_id)
            .where(table.date >= begin)
            .where(table.date <= end)
            .order_by(table.date.desc())
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).all()
        if current_data is None:
            return False
        else:
            return current_data

    def get_daily(self, usage_point_id, begin, end, measurement_direction="consumption"):
        delta = end - begin
        result = {"missing_data": False, "date": {}, "count": 0}
        for i in range(delta.days + 1):
            checkDate = begin + timedelta(days=i)
            checkDate = datetime.combine(checkDate, datetime.min.time())
            query_result = self.get_daily_date(usage_point_id, checkDate, measurement_direction)
            checkDate = checkDate.strftime("%Y-%m-%d")
            if query_result is None:
                # NEVER QUERY
                result["date"][checkDate] = {
                    "status": False,
                    "blacklist": 0,
                    "value": 0,
                }
                result["missing_data"] = True
            else:
                consumption = query_result.value
                blacklist = query_result.blacklist
                if consumption == 0:
                    # ENEDIS RETURN NO DATA
                    result["date"][checkDate] = {
                        "status": False,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
                    result["missing_data"] = True
                else:
                    # SUCCESS or BLACKLIST
                    result["date"][checkDate] = {
                        "status": True,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
        return result

    def insert_daily(
        self,
        usage_point_id,
        date,
        value,
        blacklist=0,
        fail_count=0,
        measurement_direction="consumption",
    ):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        query = select(table).join(relation).where(table.id == unique_id)
        daily = self.session.scalars(query).one_or_none()
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        if daily is not None:
            daily.id = unique_id
            daily.usage_point_id = usage_point_id
            daily.date = date
            daily.value = value
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            self.session.add(
                table(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=value,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def reset_daily(self, usage_point_id, date=None, mesure_type="consumption"):
        data = self.get_daily_date(usage_point_id, date, mesure_type)
        if mesure_type == "consumption":
            table = ConsumptionDaily
        else:
            table = ProductionDaily
        if data is not None:
            values = {
                table.value: 0,
                table.blacklist: 0,
                table.fail_count: 0,
            }
            unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
            self.session.execute(update(table, values=values).where(table.id == unique_id))
            self.session.flush()
            return True
        else:
            return False

    def delete_daily(self, usage_point_id, date=None, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDaily
        else:
            table = ProductionDaily
        if date is not None:
            unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
            self.session.execute(delete(table).where(table.id == unique_id))
        else:
            self.session.execute(delete(table).where(table.usage_point_id == usage_point_id))
        self.session.flush()
        return True

    def blacklist_daily(self, usage_point_id, date, action=True, measurement_direction="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDaily
            relation = UsagePoints.relation_consumption_daily
        else:
            table = ProductionDaily
            relation = UsagePoints.relation_production_daily
        query = select(table).join(relation).where(table.id == unique_id)
        daily = self.session.scalars(query).one_or_none()
        if daily is not None:
            daily.blacklist = action
        else:
            self.session.add(
                table(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=0,
                    blacklist=action,
                    fail_count=0,
                )
            )
        self.session.flush()
        return True

    def get_daily_date_range(self, usage_point_id):
        return {
            "begin": self.get_daily_last_date(usage_point_id),
            "end": self.get_daily_first_date(usage_point_id),
        }

    # -----------------------------------------------------------------------------------------------------------------
    # DETAIL CONSUMPTION
    # -----------------------------------------------------------------------------------------------------------------
    def get_detail_all(
        self,
        usage_point_id,
        begin=None,
        end=None,
        measurement_direction="consumption",
        order_dir="desc",
    ):
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        sort = asc("date") if order_dir == "desc" else desc("date")
        if begin is None and end is None:
            return self.session.scalars(
                select(table).join(relation).where(table.usage_point_id == usage_point_id).order_by(sort)
            ).all()
        elif begin is not None and end is None:
            return self.session.scalars(
                select(table)
                .join(relation)
                .where(table.usage_point_id == usage_point_id)
                .filter(table.date >= begin)
                .order_by(sort)
            ).all()
        elif end is not None and begin is None:
            return self.session.scalars(
                select(table)
                .join(relation)
                .where(table.usage_point_id == usage_point_id)
                .filter(table.date <= end)
                .order_by(sort)
            ).all()
        else:
            return self.session.scalars(
                select(table)
                .join(relation)
                .where(table.usage_point_id == usage_point_id)
                .filter(table.date <= end)
                .filter(table.date >= begin)
                .order_by(sort)
            ).all()

    def get_detail_datatable(
        self,
        usage_point_id,
        order_column="date",
        order_dir="asc",
        search=None,
        measurement_direction="consumption",
    ):
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        yesterday = datetime.combine(datetime.now() - timedelta(days=1), datetime.max.time())
        sort = asc(order_column) if order_dir == "desc" else desc(order_column)
        if search is not None and search != "":
            result = self.session.scalars(
                select(table)
                .join(relation)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where((table.date.like(f"%{search}%")) | (table.value.like(f"%{search}%")))
                .where(table.date <= yesterday)
                .order_by(sort)
            )
        else:
            result = self.session.scalars(
                select(table)
                .join(relation)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where(table.date <= yesterday)
                .order_by(sort)
            )
        return result.all()

    def get_detail_count(self, usage_point_id, measurement_direction="consumption"):
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        return self.session.scalars(
            select([func.count()])
            .select_from(table)
            .join(relation)
            .where(UsagePoints.usage_point_id == usage_point_id)
        ).one_or_none()

    def get_detail_date(self, usage_point_id, date, measurement_direction="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        return self.session.scalars(select(table).join(relation).where(table.id == unique_id)).first()

    def get_detail_range(
        self,
        usage_point_id,
        begin,
        end,
        measurement_direction="consumption",
        order="desc",
    ):
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        if order == "desc":
            order = table.date.desc()
        else:
            order = table.date.asc()
        query = (
            select(table)
            .join(relation)
            .where(table.usage_point_id == usage_point_id)
            .where(table.date >= begin)
            .where(table.date <= end)
            .order_by(order)
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).all()
        if current_data is None:
            return False
        else:
            return current_data

    def get_detail(self, usage_point_id, begin, end, measurement_direction="consumption"):
        # begin = datetime.combine(begin, datetime.min.time())
        # end = datetime.combine(end, datetime.max.time())

        delta = begin - begin

        result = {"missing_data": False, "date": {}, "count": 0}

        for i in range(delta.days + 1):
            query_result = self.get_detail_all(
                usage_point_id=usage_point_id,
                begin=begin,
                end=end,
                measurement_direction=measurement_direction,
            )
            time_delta = abs(int((begin - end).total_seconds() / 60))
            total_internal = 0
            for query in query_result:
                total_internal = total_internal + query.interval
            total_time = abs(total_internal - time_delta)
            if total_time > 300:
                logging.info(f" - {total_time}m absente du relevé.")
                result["missing_data"] = True
            else:
                for query in query_result:
                    result["date"][query.date] = {
                        "value": query.value,
                        "interval": query.interval,
                        "measure_type": query.measure_type,
                        "blacklist": query.blacklist,
                    }
            return result

    def get_detail_state(self, usage_point_id, date, measurement_direction="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if measurement_direction == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        current_data = self.session.scalars(select(table).join(relation).where(table.id == unique_id)).one_or_none()
        if current_data is None:
            return False
        else:
            return True

    # def insert_detail_bulk(self, data, mesure_type="consumption"):
    #     if mesure_type == "consumption":
    #         table = ConsumptionDetail
    #     else:
    #         table = ProductionDetail
    #     begin = ""
    #     end = ""
    #     for scalar in data:
    #         if begin == "":
    #             begin = scalar.date
    #         end = scalar.date
    #     self.session.execute(
    #         table.__table__.delete().filter(ConsumptionDetail.date.between(begin, end))
    #     )
    #     self.session.add_all(data)

    def insert_detail(
        self,
        usage_point_id,
        date,
        value,
        interval,
        measure_type,
        blacklist=0,
        fail_count=0,
        mesure_type="consumption",
    ):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if mesure_type == "consumption":
            table = ConsumptionDetail
        else:
            table = ProductionDetail
        detail = self.get_detail_date(usage_point_id, date, mesure_type)
        if detail is not None:
            detail.id = unique_id
            detail.usage_point_id = usage_point_id
            detail.date = date
            detail.value = value
            detail.interval = interval
            detail.measure_type = measure_type
            detail.blacklist = blacklist
            detail.fail_count = fail_count
        else:
            self.session.add(
                table(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def reset_detail(self, usage_point_id, date=None, mesure_type="consumption"):
        detail = self.get_detail_date(usage_point_id, date, mesure_type)
        if detail is not None:
            detail.value = 0
            detail.interval = 0
            detail.blacklist = 0
            detail.fail_count = 0
            self.session.flush()
            return True
        else:
            return False

    def reset_detail_range(self, usage_point_id, begin, end, mesure_type="consumption"):
        detail = self.get_detail_range(usage_point_id, begin, end, mesure_type)
        if detail is not None:
            for row in detail:
                row.value = 0
                row.interval = 0
                row.blacklist = 0
                row.fail_count = 0
            self.session.flush()
            return True
        else:
            return False

    def delete_detail(self, usage_point_id, date=None, mesure_type="consumption"):
        if mesure_type == "consumption":
            table = ConsumptionDetail
        else:
            table = ProductionDetail
        if date is not None:
            unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
            self.session.execute(delete(table).where(table.id == unique_id))
        else:
            self.session.execute(delete(table).where(table.usage_point_id == usage_point_id))
        self.session.flush()
        return True

    def delete_detail_range(self, usage_point_id, date, mesure_type="consumption"):
        if mesure_type == "consumption":
            table = ConsumptionDetail
        else:
            table = ProductionDetail
        if date is not None:
            unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
            self.session.execute(delete(table).where(table.id == unique_id))
        else:
            self.session.execute(delete(table).where(table.usage_point_id == usage_point_id))
        self.session.flush()
        return True

    def get_ratio_hc_hp(self, usage_point_id, begin, end, mesure_type="consumption"):
        result = {
            "HC": 0,
            "HP": 0,
        }
        detail_data = self.get_detail_all(
            usage_point_id=usage_point_id,
            begin=begin,
            end=end,
            measurement_direction=mesure_type,
        )
        for data in detail_data:
            result[data.measure_type] = result[data.measure_type] + data.value
        return result

    def get_detail_fail_count(self, usage_point_id, date, mesure_type="consumption"):
        return self.get_detail_date(usage_point_id, date, mesure_type).fail_count

    def detail_fail_increment(self, usage_point_id, date, mesure_type="consumption"):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        if mesure_type == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        query = select(table).join(relation).where(table.id == unique_id)
        detail = self.session.scalars(query).one_or_none()
        if detail is not None:
            fail_count = int(detail.fail_count) + 1
            if fail_count >= MAX_IMPORT_TRY:
                blacklist = 1
                fail_count = 0
            else:
                blacklist = 0
            detail.usage_point_id = usage_point_id
            detail.date = date
            detail.value = 0
            detail.interval = 0
            detail.measure_type = "HP"
            detail.blacklist = blacklist
            detail.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                table(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=0,
                    interval=0,
                    measure_type="HP",
                    blacklist=0,
                    fail_count=0,
                )
            )
        self.session.flush()
        return fail_count

    def get_detail_last_date(self, usage_point_id, mesure_type="consumption"):
        if mesure_type == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        current_data = self.session.scalars(
            select(table).join(relation).where(table.usage_point_id == usage_point_id).order_by(table.date)
        ).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_detail_first_date(self, usage_point_id, mesure_type="consumption"):
        if mesure_type == "consumption":
            table = ConsumptionDetail
            relation = UsagePoints.relation_consumption_detail
        else:
            table = ProductionDetail
            relation = UsagePoints.relation_production_detail
        query = select(table).join(relation).where(table.usage_point_id == usage_point_id).order_by(table.date.desc())
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_detail_date_range(self, usage_point_id):
        return {
            "begin": self.get_detail_last_date(usage_point_id),
            "end": self.get_detail_first_date(usage_point_id),
        }

    # -----------------------------------------------------------------------------------------------------------------
    # DAILY POWER
    # -----------------------------------------------------------------------------------------------------------------
    def get_daily_max_power_all(self, usage_point_id, order="desc"):
        if order == "desc":
            order = ConsumptionDailyMaxPower.date.desc()
        else:
            order = ConsumptionDailyMaxPower.date.asc()
        return self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(UsagePoints.usage_point_id == usage_point_id)
            .order_by(order)
        ).all()

    def get_daily_max_power_range(self, usage_point_id, begin, end):
        query = (
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.usage_point_id == usage_point_id)
            .where(ConsumptionDailyMaxPower.date >= begin)
            .where(ConsumptionDailyMaxPower.date <= end)
            .order_by(ConsumptionDailyMaxPower.date.desc())
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).all()
        if current_data is None:
            return False
        else:
            return current_data

    def get_daily_power(self, usage_point_id, begin, end):
        delta = end - begin
        result = {"missing_data": False, "date": {}, "count": 0}
        for i in range(delta.days + 1):
            checkDate = begin + timedelta(days=i)
            checkDate = datetime.combine(checkDate, datetime.min.time())
            query_result = self.get_daily_max_power_date(usage_point_id, checkDate)
            checkDate = checkDate.strftime("%Y-%m-%d")
            if query_result is None:
                # NEVER QUERY
                result["date"][checkDate] = {
                    "status": False,
                    "blacklist": 0,
                    "value": 0,
                }
                result["missing_data"] = True
            else:
                consumption = query_result.value
                blacklist = query_result.blacklist
                if consumption == 0:
                    # ENEDIS RETURN NO DATA
                    result["date"][checkDate] = {
                        "status": False,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
                    result["missing_data"] = True
                else:
                    # SUCCESS or BLACKLIST
                    result["date"][checkDate] = {
                        "status": True,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
        return result

    def get_daily_max_power_last_date(self, usage_point_id):
        current_data = self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.usage_point_id == usage_point_id)
            .order_by(ConsumptionDailyMaxPower.date)
        ).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_daily_max_power_date(self, usage_point_id, date):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        return self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.id == unique_id)
        ).one_or_none()

    def insert_daily_max_power(self, usage_point_id, date, event_date, value, blacklist=0, fail_count=0):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        daily = self.get_daily_max_power_date(usage_point_id, date)
        if daily is not None:
            daily.id = unique_id
            daily.usage_point_id = usage_point_id
            daily.date = date
            daily.event_date = event_date
            daily.value = value
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            self.session.add(
                ConsumptionDailyMaxPower(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    event_date=event_date,
                    value=value,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def get_daily_max_power_count(self, usage_point_id):
        return self.session.scalars(
            select([func.count()])
            .select_from(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(UsagePoints.usage_point_id == usage_point_id)
        ).one_or_none()

    def get_daily_max_power_datatable(self, usage_point_id, order_column="date", order_dir="asc", search=None):
        yesterday = datetime.combine(datetime.now() - timedelta(days=1), datetime.max.time())
        sort = asc(order_column) if order_dir == "desc" else desc(order_column)
        if search is not None and search != "":
            result = self.session.scalars(
                select(ConsumptionDailyMaxPower)
                .join(UsagePoints.relation_consumption_daily_max_power)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where(
                    (ConsumptionDailyMaxPower.date.like(f"%{search}%"))
                    | (ConsumptionDailyMaxPower.value.like(f"%{search}%"))
                )
                .where(ConsumptionDailyMaxPower.date <= yesterday)
                .order_by(sort)
            )
        else:
            result = self.session.scalars(
                select(ConsumptionDailyMaxPower)
                .join(UsagePoints.relation_consumption_daily_max_power)
                .where(UsagePoints.usage_point_id == usage_point_id)
                .where(ConsumptionDailyMaxPower.date <= yesterday)
                .order_by(sort)
            )
        return result.all()

    def daily_max_power_fail_increment(self, usage_point_id, date):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        daily = self.get_daily_max_power_date(usage_point_id, date)
        if daily is not None:
            fail_count = int(daily.fail_count) + 1
            if fail_count >= MAX_IMPORT_TRY:
                blacklist = 1
                fail_count = 0
            else:
                blacklist = 0
            daily.id = unique_id
            daily.usage_point_id = usage_point_id
            daily.date = date
            daily.event_date = None
            daily.value = 0
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                ConsumptionDailyMaxPower(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    event_date=None,
                    value=0,
                    blacklist=0,
                    fail_count=0,
                )
            )
        self.session.flush()
        return fail_count

    def reset_daily_max_power(self, usage_point_id, date=None):
        daily = self.get_daily_max_power_date(usage_point_id, date)
        if daily is not None:
            daily.event_date = None
            daily.value = 0
            daily.blacklist = 0
            daily.fail_count = 0
            self.session.flush()
            return True
        else:
            return False

    def delete_daily_max_power(self, usage_point_id, date=None):
        if date is not None:
            unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
            self.session.execute(delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.id == unique_id))
        else:
            self.session.execute(
                delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.usage_point_id == usage_point_id)
            )
        self.session.flush()
        return True

    def blacklist_daily_max_power(self, usage_point_id, date, action=True):
        unique_id = hashlib.md5(f"{usage_point_id}/{date}".encode("utf-8")).hexdigest()
        daily = self.get_daily_max_power_date(usage_point_id, date)
        if daily is not None:
            daily.blacklist = action
        else:
            self.session.add(
                ConsumptionDailyMaxPower(
                    id=unique_id,
                    usage_point_id=usage_point_id,
                    date=date,
                    value=0,
                    blacklist=action,
                    fail_count=0,
                )
            )
        self.session.flush()
        return True

    def get_daily_max_power_fail_count(self, usage_point_id, date):
        result = self.get_daily_max_power_date(usage_point_id, date)
        if hasattr(result, "fail_count"):
            return result.fail_count
        else:
            return 0

    # -----------------------------------------------------------------------------------------------------------------
    # TEMPO
    # -----------------------------------------------------------------------------------------------------------------
    def get_tempo(self, order="desc"):
        if order == "desc":
            order = Tempo.date.desc()
        else:
            order = Tempo.date.asc()
        return self.session.scalars(select(Tempo).order_by(order)).all()

    def get_tempo_range(self, begin, end, order="desc"):
        if order == "desc":
            order = Tempo.date.desc()
        else:
            order = Tempo.date.asc()
        return self.session.scalars(
            select(Tempo).where(Tempo.date >= begin).where(Tempo.date <= end).order_by(order)
        ).all()

    def set_tempo(self, date, color):
        date = datetime.combine(date, datetime.min.time())
        tempo = self.get_tempo_range(date, date)
        if tempo:
            for item in tempo:
                item.color = color
        else:
            self.session.add(Tempo(date=date, color=color))
        self.session.flush()
        return True

    # -----------------------------------------------------------------------------------------------------------------
    # TEMPO CONFIG
    # -----------------------------------------------------------------------------------------------------------------
    def get_tempo_config(self, key):
        query = select(TempoConfig).where(TempoConfig.key == key)
        data = self.session.scalars(query).one_or_none()
        if data is not None:
            data = json.loads(data.value)
        self.session.close()
        return data

    def set_tempo_config(self, key, value):
        query = select(TempoConfig).where(TempoConfig.key == key)
        config = self.session.scalars(query).one_or_none()
        if config:
            config.value = json.dumps(value)
        else:
            self.session.add(TempoConfig(key=key, value=json.dumps(value)))
        self.session.flush()
        self.session.close()

    # -----------------------------------------------------------------------------------------------------------------
    # ECOWATT
    # -----------------------------------------------------------------------------------------------------------------
    def get_ecowatt(self, order="desc"):
        if order == "desc":
            order = Ecowatt.date.desc()
        else:
            order = Ecowatt.date.asc()
        return self.session.scalars(select(Ecowatt).order_by(order)).all()

    def get_ecowatt_range(self, begin, end, order="desc"):
        if order == "desc":
            order = Ecowatt.date.desc()
        else:
            order = Ecowatt.date.asc()
        return self.session.scalars(
            select(Ecowatt).where(Ecowatt.date >= begin).where(Ecowatt.date <= end).order_by(order)
        ).all()

    def set_ecowatt(self, date, value, message, detail):
        date = datetime.combine(date, datetime.min.time())
        ecowatt = self.get_ecowatt_range(date, date)
        if ecowatt:
            for item in ecowatt:
                item.value = value
                item.message = message
                item.detail = detail
        else:
            self.session.add(Ecowatt(date=date, value=value, message=message, detail=detail))
        self.session.flush()
        return True

    # ----------------------------------------------------------------------------------------------------------------
    # STATISTIQUES
    # ----------------------------------------------------------------------------------------------------------------
    def get_stat(self, usage_point_id, key):
        return self.session.scalars(
            select(Statistique)
            .join(UsagePoints.relation_stats)
            .where(Statistique.usage_point_id == usage_point_id)
            .where(Statistique.key == key)
        ).all()

    def set_stat(self, usage_point_id, key, value):
        current_value = self.get_stat(usage_point_id, key)
        if current_value:
            for item in current_value:
                item.value = value
        else:
            self.session.add(Statistique(usage_point_id=usage_point_id, key=key, value=value))
        self.session.flush()
        return True

    def del_stat(self, usage_point_id):
        self.session.execute(delete(Statistique).where(Statistique.usage_point_id == usage_point_id))
