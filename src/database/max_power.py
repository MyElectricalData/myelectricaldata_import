"""Manage Config table in database."""

import hashlib
import logging
from datetime import datetime, timedelta

import pytz
from sqlalchemy import asc, delete, desc, func, select

from config import MAX_IMPORT_TRY
from database import DB
from db_schema import ConsumptionDailyMaxPower, UsagePoints


class DatabaseMaxPower:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id, measurement_direction="consumption"):
        """Initialize DatabaseConfig."""
        self.session = DB.session
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction

    def get_all(self, order="desc"):
        """Retrieve all consumption daily max power records from the database.

        Args:
            order (str, optional): The order in which the records should be sorted. Defaults to "desc".

        Returns:
            list: A list of consumption daily max power records.
        """
        if order == "desc":
            order = ConsumptionDailyMaxPower.date.desc()
        else:
            order = ConsumptionDailyMaxPower.date.asc()
        return self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
            .order_by(order)
        ).all()

    def get_range(self, begin, end):
        """Retrieve the range of consumption daily max power records from the database.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.

        Returns:
            list: A list of consumption daily max power records within the specified range.
        """
        query = (
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.usage_point_id == self.usage_point_id)
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

    def get_power(self, begin, end):
        """Retrieve the power data for a given date range.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.

        Returns:
            dict: A dictionary containing the power data for each date within the range.
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

    def get_last_date(self):
        """Retrieve the last date of consumption daily max power record from the database.

        Returns:
            datetime: The last date of consumption daily max power record.
        """
        current_data = self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.usage_point_id == self.usage_point_id)
            .order_by(ConsumptionDailyMaxPower.date)
        ).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_date(self, date):
        """Retrieve the consumption daily max power record for a given date.

        Args:
            date (datetime): The date for which to retrieve the record.

        Returns:
            ConsumptionDailyMaxPower: The consumption daily max power record for the given date.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        return self.session.scalars(
            select(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(ConsumptionDailyMaxPower.id == unique_id)
        ).one_or_none()

    def insert(self, date, event_date, value, blacklist=0, fail_count=0):  # noqa: PLR0913, D417
        """Insert the daily max power record into the database.

        Args:
            date (datetime): The date of the record.
            event_date (datetime): The event date of the record.
            value (float): The value of the record.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        daily = self.get_date(date)
        if daily is not None:
            daily.id = unique_id
            daily.usage_point_id = self.usage_point_id
            daily.date = date
            daily.event_date = event_date
            daily.value = value
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            self.session.add(
                ConsumptionDailyMaxPower(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    event_date=event_date,
                    value=value,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def get_daily_count(self):
        """Retrieve the count of consumption daily max power records from the database.

        Returns:
            int: The count of consumption daily max power records.
        """
        return self.session.scalars(
            select([func.count()])
            .select_from(ConsumptionDailyMaxPower)
            .join(UsagePoints.relation_consumption_daily_max_power)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        ).one_or_none()

    def get_daily_datatable(self, order_column="date", order_dir="asc", search=None):
        """Retrieve the datatable of consumption daily max power records from the database.

        Args:
            order_column (str, optional): The column to order the datatable by. Defaults to "date".
            order_dir (str, optional): The direction to order the datatable in. Defaults to "asc".
            search (str, optional): The search term to filter the datatable. Defaults to None.

        Returns:
            list: The datatable of consumption daily max power records.
        """
        yesterday = datetime.combine(datetime.now(pytz.utc) - timedelta(days=1), datetime.max.time())
        sort = asc(order_column) if order_dir == "desc" else desc(order_column)
        if search is not None and search != "":
            result = self.session.scalars(
                select(ConsumptionDailyMaxPower)
                .join(UsagePoints.relation_consumption_daily_max_power)
                .where(UsagePoints.usage_point_id == self.usage_point_id)
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
                .where(UsagePoints.usage_point_id == self.usage_point_id)
                .where(ConsumptionDailyMaxPower.date <= yesterday)
                .order_by(sort)
            )
        return result.all()

    def daily_fail_increment(self, date):
        """Increment the fail count for a specific date in the consumption daily max power records.

        Args:
            date (datetime): The date for which to increment the fail count.

        Returns:
            int: The updated fail count.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        daily = self.get_date(date)
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
            daily.event_date = None
            daily.value = 0
            daily.blacklist = blacklist
            daily.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                ConsumptionDailyMaxPower(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    event_date=None,
                    value=0,
                    blacklist=0,
                    fail_count=0,
                )
            )
        self.session.flush()
        return fail_count

    def reset_daily(self, date=None):
        """Reset the daily max power record for a specific date.

        Args:
            date (datetime, optional): The date to reset the record for. Defaults to None.

        Returns:
            bool: True if the reset is successful, False otherwise.
        """
        daily = self.get_date(date)
        if daily is not None:
            daily.event_date = None
            daily.value = 0
            daily.blacklist = 0
            daily.fail_count = 0
            self.session.flush()
            return True
        else:
            return False

    def delete_daily(self, date=None):
        """Delete the daily max power record for a specific date or all records for the usage point.

        Args:
            date (datetime, optional): The date to delete the record for. Defaults to None.

        Returns:
            bool: True if the deletion is successful, False otherwise.
        """
        if date is not None:
            unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
            self.session.execute(delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.id == unique_id))
        else:
            self.session.execute(
                delete(ConsumptionDailyMaxPower).where(ConsumptionDailyMaxPower.usage_point_id == self.usage_point_id)
            )
        self.session.flush()
        return True

    def blacklist_daily(self, date, action=True):
        """Blacklist or unblacklist the daily max power record for a specific date.

        Args:
            date (datetime): The date to blacklist or unblacklist the record for.
            action (bool, optional): True to blacklist the record, False to unblacklist it. Defaults to True.

        Returns:
            bool: True if the operation is successful, False otherwise.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        daily = self.get_date(date)
        if daily is not None:
            daily.blacklist = action
        else:
            self.session.add(
                ConsumptionDailyMaxPower(
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

    def get_fail_count(self, date):
        """Get the fail count for a specific date.

        Args:
            date (datetime): The date to get the fail count for.

        Returns:
            int: The fail count for the specified date.
        """
        result = self.get_date(date)
        if hasattr(result, "fail_count"):
            return result.fail_count
        return 0
