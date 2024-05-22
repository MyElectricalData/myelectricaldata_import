"""Manage Config table in database."""

import hashlib
import logging
from datetime import datetime, timedelta

from sqlalchemy import asc, delete, desc, func, select, update

from config import MAX_IMPORT_TRY, TIMEZONE_UTC
from database import DB
from db_schema import ConsumptionDaily, ProductionDaily, UsagePoints


class DatabaseDaily:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id, measurement_direction="consumption"):
        """Initialize DatabaseConfig."""
        self.session = DB.session
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        if self.measurement_direction == "consumption":
            self.table = ConsumptionDaily
            self.relation = UsagePoints.relation_consumption_daily
        else:
            self.table = ProductionDaily
            self.relation = UsagePoints.relation_production_daily

    def get_all(self):
        """Retrieve all daily data for a given usage point and measurement direction."""
        data = self.session.scalars(
            select(self.table)
            .join(self.relation)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
            .order_by(self.table.date.desc())
        ).all()
        self.session.close()
        return data

    def get_datatable(
        self,
        order_column="date",
        order_dir="asc",
        search=None,
    ):
        """Retrieve datatable for a given usage point, search term, and measurement direction.

        Args:
            order_column (str, optional): The column to order the datatable by. Defaults to "date".
            order_dir (str, optional): The direction to order the datatable. Defaults to "asc".
            search (str, optional): The search term. Defaults to None.

        Returns:
            list: The datatable.
        """
        yesterday = datetime.combine(datetime.now(tz=TIMEZONE_UTC) - timedelta(days=1), datetime.max.time())
        sort = asc(order_column) if order_dir == "desc" else desc(order_column)
        if search is not None and search != "":
            result = self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(UsagePoints.usage_point_id == self.usage_point_id)
                .where((self.table.date.like(f"%{search}%")) | (self.table.value.like(f"%{search}%")))
                .where(self.table.date <= yesterday)
                .order_by(sort)
            )
        else:
            result = self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(UsagePoints.usage_point_id == self.usage_point_id)
                .where(self.table.date <= yesterday)
                .order_by(sort)
            )
        return result.all()

    def get_count(self):
        """Retrieve the count of daily data for a given usage point and measurement direction.

        Returns:
            int: The count of daily data.
        """
        data = self.session.scalars(
            select([func.count()])
            .select_from(self.table)
            .join(self.relation)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        ).one_or_none()
        self.session.close()
        return data

    def get_date(self, date):
        """Retrieve the data for a given usage point, date, and measurement direction.

        Args:
            date (str): The date.

        Returns:
            object: The data.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        data = self.session.scalars(select(self.table).join(self.relation).where(self.table.id == unique_id)).first()
        self.session.flush()
        self.session.close()
        return data

    def get_state(self, date):
        """Check the state of daily data for a given usage point, date, and measurement direction.

        Args:
            date (str): The date.

        Returns:
            bool: True if the daily data exists, False otherwise.
        """
        if self.get_date(date) is not None:
            return True
        else:
            return False

    def get_last_date(self):
        """Retrieve the last date for a given usage point and measurement direction.

        Returns:
            str: The last date.
        """
        current_data = self.session.scalars(
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .order_by(self.table.date)
        ).first()
        self.session.flush()
        self.session.close()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_last(self):
        """Retrieve the last data point for a given usage point and measurement direction.

        Returns:
            object: The last data point.
        """
        current_data = self.session.scalars(
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .where(self.table.value != 0)
            .order_by(self.table.date.desc())
        ).first()
        self.session.flush()
        self.session.close()
        if current_data is None:
            return False
        else:
            return current_data

    def get_first_date(self):
        """Retrieve the first date for a given usage point and measurement direction.

        Returns:
            str: The first date.
        """
        query = (
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .order_by(self.table.date.desc())
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_fail_count(self, date):
        """Retrieve the fail count for a given usage point, date, and measurement direction.

        Args:
            date (str): The date.

        Returns:
            int: The fail count.
        """
        result = self.get_date(date)
        if hasattr(result, "fail_count"):
            return result.fail_count
        else:
            return 0

    def fail_increment(self, date):
        """Increment the fail count for a given usage point, date, and measurement direction.

        Args:
            date (str): The date.

        Returns:
            int: The updated fail count.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        query = select(self.table).join(self.relation).where(self.table.id == unique_id)
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
            daily.usage_point_id = self.usage_point_id
            daily.date = date
            daily.value = 0
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                self.table(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    value=0,
                    blacklist=0,
                    fail_count=0,
                )
            )
        self.session.flush()
        return fail_count

    def get_range(self, begin, end):
        """Retrieve the range of data for a given usage point, begin date, end date, and measurement direction.

        Args:
            begin (str): The begin date.
            end (str): The end date.

        Returns:
            list: The list of data within the specified range.
        """
        query = (
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .where(self.table.date >= begin)
            .where(self.table.date <= end)
            .order_by(self.table.date.desc())
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).all()
        if current_data is None:
            return False
        else:
            return current_data

    def get(self, begin, end):
        """Retrieve the data for a given usage point, begin date, end date, and measurement direction.

        Args:
            begin (str): The begin date.
            end (str): The end date.

        Returns:
            dict: A dictionary containing the retrieved data.
        """
        delta = end - begin
        result = {"missing_data": False, "date": {}, "count": 0}
        for i in range(delta.days + 1):
            check_date = begin + timedelta(days=i)
            check_date = datetime.combine(check_date, datetime.min.time())
            query_result = self.get_date(check_date)
            check_date = check_date.strftime("%Y-%m-%d")
            if query_result is None:
                # NEVER QUERY
                result["date"][check_date] = {
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
                    result["date"][check_date] = {
                        "status": False,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
                    result["missing_data"] = True
                else:
                    # SUCCESS or BLACKLIST
                    result["date"][check_date] = {
                        "status": True,
                        "blacklist": blacklist,
                        "value": consumption,
                    }
        return result

    def insert(
        self,
        date,
        value,
        blacklist=0,
        fail_count=0,
    ):
        """Insert daily data for a given usage point, date, value, blacklist, fail count, and measurement direction.

        Args:
            date (str): The date of the data.
            value (float): The value of the data.
            blacklist (int, optional): The blacklist status. Defaults to 0.
            fail_count (int, optional): The fail count. Defaults to 0.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        query = select(self.table).join(self.relation).where(self.table.id == unique_id)
        daily = self.session.scalars(query).one_or_none()
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        if daily is not None:
            daily.id = unique_id
            daily.usage_point_id = self.usage_point_id
            daily.date = date
            daily.value = value
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            self.session.add(
                self.table(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    value=value,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def reset(
        self,
        date=None,
    ):
        """Reset the daily data for a given usage point, date, and measurement type.

        Args:
            date (str, optional): The date of the data. Defaults to None.

        Returns:
            bool: True if the data was reset, False otherwise.
        """
        data = self.get_date(date)
        if data is not None:
            values = {
                self.table.value: 0,
                self.table.blacklist: 0,
                self.table.fail_count: 0,
            }
            unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
            self.session.execute(update(self.table, values=values).where(self.table.id == unique_id))
            self.session.flush()
            return True
        else:
            return False

    def delete(self, date=None):
        """Delete the daily data for a given usage point, date, and measurement direction.

        Args:
            date (str, optional): The date of the data. Defaults to None.

        Returns:
            bool: True if the data was deleted, False otherwise.
        """
        if date is not None:
            unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
            self.session.execute(delete(self.table).where(self.table.id == unique_id))
        else:
            self.session.execute(delete(self.table).where(self.table.usage_point_id == self.usage_point_id))
        self.session.flush()
        return True

    def blacklist(self, date, action=True):
        """Blacklist or unblacklist the daily data for a given usage point, date, and measurement direction.

        Args:
            date (str): The date of the data.
            action (bool, optional): The action to perform. True to blacklist, False to unblacklist. Defaults to True.

        Returns:
            bool: True if the data was blacklisted or unblacklisted, False otherwise.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        query = select(self.table).join(self.relation).where(self.table.id == unique_id)
        daily = self.session.scalars(query).one_or_none()
        if daily is not None:
            daily.blacklist = action
        else:
            self.session.add(
                self.table(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    value=0,
                    blacklist=action,
                    fail_count=0,
                )
            )
        self.session.flush()
        return True

    def get_date_range(self):
        """Get the date range for a given usage point.

        Returns:
            dict: A dictionary containing the begin and end dates of the date range.
        """
        return {
            "begin": self.get_last_date(),
            "end": self.get_first_date(),
        }
