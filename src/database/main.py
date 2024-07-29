"""Manage all database operations."""
import logging
import subprocess
import sys
import traceback
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import NullPool

from const import TIMEZONE
from db_schema import (
    Config as ConfigSchema,
)
from utils import get_version, load_config


class Database:
    """Represents a database connection and provides methods for database operations."""

    def __init__(self):
        """Initialize a Database object."""
        self.config = load_config()
        self.application_path = self.config.application_path
        self.application_path_data = self.config.application_path_data
        self.db_file = f"{self.application_path_data}/myelectricaldata.db"

        # MIGRATE TO 1.0.0
        old_path = Path(f"{self.application_path_data}/cache.db")
        if old_path.exists():
            old_path.rename(self.db_file)

        # DBURI CONFIGURATION
        backend: dict = self.config.config.get("backend", None)
        if backend is None or "uri" not in backend:
            path = self.db_file
            self.uri = f"sqlite:////{path}"
            logging.critical(f"Create new database file : {path}")
        elif backend["uri"].startswith("sqlite") or backend["uri"].startswith("postgresql"):
            self.uri = backend["uri"]
            if backend["uri"].startswith("sqlite"):
                path = self.uri.split("///")[1]
                if not Path(path).exists():
                    logging.critical(f"Create new database file : {path}")
                    Path(self.db_file).touch()
        else:
            logging.critical("Database not supported (only SQLite & PostgresSQL)")
            sys.exit(1)

        self.engine = create_engine(
            self.uri,
            echo=False,
            query_cache_size=0,
            isolation_level="READ UNCOMMITTED",
            poolclass=NullPool,
        )

        subprocess.run(
            f"cd {self.application_path}; DB_URL='{self.uri}' alembic upgrade head",
            shell=True,  # noqa: S602
            check=True,
        )

        self.session_factory = sessionmaker(self.engine, autocommit=True, autoflush=True)
        self.session = scoped_session(self.session_factory)
        self.inspector = inspect(self.engine)
        self.lock_file = f"{self.application_path_data}/.lock"

    def init_database(self):
        """Initialize the database with default values."""
        try:
            logging.info("Configure Databases")
            query = select(ConfigSchema).where(ConfigSchema.key == "day")
            day = self.session().scalars(query).one_or_none()
            if day:
                day.value = datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d")
            else:
                self.session().add(ConfigSchema(key="day", value=datetime.now(tz=TIMEZONE).strftime("%Y-%m-%d")))
            logging.info(" => day")
            query = select(ConfigSchema).where(ConfigSchema.key == "call_number")
            if not self.session().scalars(query).one_or_none():
                self.session().add(ConfigSchema(key="call_number", value="0"))
            logging.info(" => call_number")
            query = select(ConfigSchema).where(ConfigSchema.key == "max_call")
            if not self.session().scalars(query).one_or_none():
                self.session().add(ConfigSchema(key="max_call", value="500"))
            logging.info(" => max_call")
            query = select(ConfigSchema).where(ConfigSchema.key == "version")
            version = self.session().scalars(query).one_or_none()
            if version:
                version.value = get_version()
            else:
                self.session().add(ConfigSchema(key="version", value=get_version()))
            logging.info(" => version")
            query = select(ConfigSchema).where(ConfigSchema.key == "lock")
            if not self.session().scalars(query).one_or_none():
                self.session().add(ConfigSchema(key="lock", value="0"))
            logging.info(" => lock")
            query = select(ConfigSchema).where(ConfigSchema.key == "lastUpdate")
            if not self.session().scalars(query).one_or_none():
                self.session().add(ConfigSchema(key="lastUpdate", value=str(datetime.now(tz=TIMEZONE))))
            logging.info(" => lastUpdate")
            logging.info(" Success")
        except Exception as e:
            traceback.print_exc()
            logging.error(e)
            logging.critical("Database initialize failed!")

    def purge_database(self):
        """Purges the SQLite database."""
        logging.info("Reset SQLite Database")
        if Path(f"{self.application_path_data}/cache.db").exists():
            Path(f"{self.application_path_data}/cache.db").unlink()
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
        with Path(self.lock_file).open("xt", encoding="UTF-8") as f:
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
        self.session().expire_all()
