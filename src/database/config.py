"""Manage Config table in database."""

import json

from sqlalchemy import select

from db_schema import Config as ConfigTable

from . import DB


class DatabaseConfig:
    """Manage configuration for the database."""

    def __init__(self):
        """Initialize DatabaseConfig."""
        self.session = DB.session()

    def get(self, key):
        """Get data from config table."""
        query = select(ConfigTable).where(ConfigTable.key == key)
        data = self.session.scalars(query).one_or_none()
        self.session.close()
        return data

    def set(self, key, value):
        """Set data from config table."""
        query = select(ConfigTable).where(ConfigTable.key == key)
        config = self.session.scalars(query).one_or_none()
        if config:
            config.value = json.dumps(value)
        else:
            self.session.add(ConfigTable(key=key, value=json.dumps(value)))
        self.session.flush()
        self.session.close()
        DB.refresh_object()
