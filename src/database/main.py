"""Manage all database operations."""

import logging
import subprocess
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from config import TIMEZONE
from db_schema import (
    Config as ConfigSchema,
)
from dependencies import APPLICATION_PATH, APPLICATION_PATH_DATA, get_version
from models.config import Config

available_database = ["sqlite", "postgresql"]


class Database:
    """Represents a database connection and provides methods for database operations."""

    def __init__(self, path=APPLICATION_PATH_DATA):
        """Initialize a Database object.

        Args:
            config (Config): The configuration object.
            path (str, optional): The path to the database. Defaults to APPLICATION_PATH_DATA.
        """
        self.path = path

        # DBURI CONFIGURATION

        if "storage_uri" in Config().config:
            storage_uri = self.config["storage_uri"]
        else:
            storage_uri = False
        if not storage_uri or storage_uri.startswith("sqlite"):
            self.db_name = "cache.db"
            self.db_path = f"{self.path}/{self.db_name}"
            self.uri = f"sqlite:///{self.db_path}?check_same_thread=False"
        else:
            self.storage_type = self.config.storage_config().split(":")[0]
            if self.storage_type in available_database:
                self.uri = self.config.storage_config()
            else:
                logging.critical(f"Database {self.storage_type} not supported (only SQLite & PostgresSQL)")

        subprocess.run(
            f"cd {APPLICATION_PATH}; DB_URL='{self.uri}' alembic upgrade head", shell=True, check=True  # noqa: S602
        )

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

    def init_database(self):
        """Initialize the database with default values."""
        try:
            logging.info("Configure Databases")
            query = select(ConfigSchema).where(ConfigSchema.key == "day")
            day = self.session.scalars(query).one_or_none()
            if day:
                day.value = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d")
            else:
                self.session.add(ConfigSchema(key="day", value=datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d")))
            logging.info(" => day")
            query = select(ConfigSchema).where(ConfigSchema.key == "call_number")
            if not self.session.scalars(query).one_or_none():
                self.session.add(ConfigSchema(key="call_number", value="0"))
            logging.info(" => call_number")
            query = select(ConfigSchema).where(ConfigSchema.key == "max_call")
            if not self.session.scalars(query).one_or_none():
                self.session.add(ConfigSchema(key="max_call", value="500"))
            logging.info(" => max_call")
            query = select(ConfigSchema).where(ConfigSchema.key == "version")
            version = self.session.scalars(query).one_or_none()
            if version:
                version.value = get_version()
            else:
                self.session.add(ConfigSchema(key="version", value=get_version()))
            logging.info(" => version")
            query = select(ConfigSchema).where(ConfigSchema.key == "lock")
            if not self.session.scalars(query).one_or_none():
                self.session.add(ConfigSchema(key="lock", value="0"))
            logging.info(" => lock")
            query = select(ConfigSchema).where(ConfigSchema.key == "lastUpdate")
            if not self.session.scalars(query).one_or_none():
                self.session.add(ConfigSchema(key="lastUpdate", value=str(datetime.now(tz=TIMEZONE))))
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
        if Path(f"{self.path}/cache.db").exists():
            Path(f"{self.path}/cache.db").unlink()
            logging.info(" => Success")
        else:
            logging.info(" => No cache detected")

    def lock_status(self):
        """Check the lock status of the database.

        Returns:
            bool: True if the database is locked, False otherwise.
        """
        if Path(self.lock_file).exists():
            return True
        else:
            return False

    def lock(self):
        """Locks the database.

        Returns:
            bool: True if the database is locked, False otherwise.
        """
        with Path(self.lock_file).open("xt") as f:
            f.write(str(datetime.now(tz=TIMEZONE)))
            f.close()
        return self.lock_status()

    def unlock(self):
        """Unlocks the database.

        Returns:
            bool: True if the database is unlocked, False otherwise.
        """
        if Path(self.lock_file).exists():
            Path(self.lock_file).unlink()
        return self.lock_status()

    def refresh_object(self):
        """Refresh the ORM objects."""
        self.session.expire_all()
