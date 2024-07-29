"""Manage Tempo table in database."""

import json
from datetime import datetime

from sqlalchemy import select

from db_schema import Tempo, TempoConfig

from . import DB


class DatabaseTempo:
    """Manage configuration for the database."""

    def __init__(self):
        """Initialize DatabaseTempo."""
        self.session = DB.session()

    def get(self, order="desc"):
        """Retrieve Tempo data from the database.

        Args:
            order (str, optional): The order in which to retrieve the data. Defaults to "desc".

        Returns:
            list: List of Tempo data.
        """
        if order == "desc":
            order = Tempo.date.desc()
        else:
            order = Tempo.date.asc()
        return self.session.scalars(select(Tempo).order_by(order)).all()

    def get_range(self, begin, end, order="desc"):
        """Retrieve Tempo data within a specified date range from the database.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.
            order (str, optional): The order in which to retrieve the data. Defaults to "desc".

        Returns:
            list: List of Tempo data within the specified date range.
        """
        if order == "desc":
            order = Tempo.date.desc()
        else:
            order = Tempo.date.asc()
        return self.session.scalars(
            select(Tempo).where(Tempo.date >= begin).where(Tempo.date <= end).order_by(order)
        ).all()

    def set(self, date, color):
        """Set the color for a specific date in the Tempo data.

        Args:
            date (datetime): The date for which to set the color.
            color (str): The color to set.

        Returns:
            bool: True if the operation is successful.
        """
        date = datetime.combine(date, datetime.min.time())
        tempo = self.get_range(date, date)
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
    def get_config(self, key):
        """Retrieve the value of a configuration key from the database.

        Args:
            key (str): The key of the configuration.

        Returns:
            Any: The value associated with the key, or None if the key is not found.
        """
        query = select(TempoConfig).where(TempoConfig.key == key)
        data = self.session.scalars(query).one_or_none()
        if data is not None:
            data = json.loads(data.value)
        self.session.close()
        return data

    def set_config(self, key, value):
        """Set the value of a configuration key in the database.

        Args:
            key (str): The key of the configuration.
            value (Any): The value to set.

        Returns:
            None
        """
        query = select(TempoConfig).where(TempoConfig.key == key)
        config = self.session.scalars(query).one_or_none()
        if config:
            config.value = json.dumps(value)
        else:
            self.session.add(TempoConfig(key=key, value=json.dumps(value)))
        self.session.flush()
        self.session.close()
