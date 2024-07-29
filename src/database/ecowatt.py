"""Manage Config table in database."""

from datetime import datetime

from sqlalchemy import select

from db_schema import Ecowatt

from . import DB


class DatabaseEcowatt:
    """Manage configuration for the database."""

    def __init__(self):
        """Initialize DatabaseConfig."""
        self.session = DB.session()

    def get(self, order="desc"):
        """Retrieve Ecowatt data from the database.

        Args:
            order (str, optional): The order in which to retrieve the data. Defaults to "desc".

        Returns:
            list: A list of Ecowatt data.
        """
        if order == "desc":
            order = Ecowatt.date.desc()
        else:
            order = Ecowatt.date.asc()
        return self.session.scalars(select(Ecowatt).order_by(order)).all()

    def get_range(self, begin, end, order="desc"):
        """Retrieve a range of Ecowatt data from the database.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.
            order (str, optional): The order in which to retrieve the data. Defaults to "desc".

        Returns:
            list: A list of Ecowatt data within the specified range.
        """
        if order == "desc":
            order = Ecowatt.date.desc()
        else:
            order = Ecowatt.date.asc()
        return self.session.scalars(
            select(Ecowatt).where(Ecowatt.date >= begin).where(Ecowatt.date <= end).order_by(order)
        ).all()

    def set(self, date, value, message, detail):
        """Set the Ecowatt data in the database.

        Args:
            date (datetime): The date of the data.
            value (float): The value of the data.
            message (str): The message associated with the data.
            detail (str): The detail information of the data.
        """
        date = datetime.combine(date, datetime.min.time())
        ecowatt = self.get_range(date, date)
        if ecowatt:
            for item in ecowatt:
                item.value = value
                item.message = message
                item.detail = detail
        else:
            self.session.add(Ecowatt(date=date, value=value, message=message, detail=detail))
        self.session.flush()
        return True
