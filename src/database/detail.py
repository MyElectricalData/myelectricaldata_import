"""Manage Config table in database."""

import hashlib
import logging
from datetime import datetime, timedelta

import pytz
from sqlalchemy import asc, delete, desc, func, select

from config import MAX_IMPORT_TRY
from db_schema import ConsumptionDetail, ProductionDetail, UsagePoints
from database import DB


class DatabaseDetail:
    """Manage configuration for the database."""

    def __init__(self, usage_point_id, measurement_direction="consumption"):
        """Initialize DatabaseConfig."""
        self.session = DB.session
        self.min_entry = 300
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        if self.measurement_direction == "consumption":
            self.table = ConsumptionDetail
            self.relation = UsagePoints.relation_consumption_detail
        else:
            self.table = ProductionDetail
            self.relation = UsagePoints.relation_production_detail

    def get_all(
        self,
        begin=None,
        end=None,
        order_dir="desc",
    ):
        """Retrieve all records from the database.

        Args:
            begin (datetime, optional): The start date of the range. Defaults to None.
            end (datetime, optional): The end date of the range. Defaults to None.
            order_dir (str, optional): The order direction. Defaults to "desc".

        Returns:
            list: A list of records.
        """
        sort = asc("date") if order_dir == "desc" else desc("date")
        if begin is None and end is None:
            return self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(self.table.usage_point_id == self.usage_point_id)
                .order_by(sort)
            ).all()
        elif begin is not None and end is None:
            return self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(self.table.usage_point_id == self.usage_point_id)
                .filter(self.table.date >= begin)
                .order_by(sort)
            ).all()
        elif end is not None and begin is None:
            return self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(self.table.usage_point_id == self.usage_point_id)
                .filter(self.table.date <= end)
                .order_by(sort)
            ).all()
        else:
            return self.session.scalars(
                select(self.table)
                .join(self.relation)
                .where(self.table.usage_point_id == self.usage_point_id)
                .filter(self.table.date <= end)
                .filter(self.table.date >= begin)
                .order_by(sort)
            ).all()

    def get_datatable(
        self,
        order_column="date",
        order_dir="asc",
        search=None,
    ):
        """Retrieve datatable from the database.

        Args:
            order_column (str, optional): The column to order the datatable by. Defaults to "date".
            order_dir (str, optional): The order direction. Defaults to "asc".
            search (str, optional): The search query to filter the datatable. Defaults to None.

        Returns:
            list: A list of datatable records.
        """
        yesterday = datetime.combine(datetime.now(tz=pytz.utc) - timedelta(days=1), datetime.max.time())
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
        """Retrieve the count of records for a specific usage point and measurement direction.

        Returns:
            int: The count of records.
        """
        return self.session.scalars(
            select([func.count()])
            .select_from(self.table)
            .join(self.relation)
            .where(UsagePoints.usage_point_id == self.usage_point_id)
        ).one_or_none()

    def get_date(self, date):
        """Retrieve the data for a specific date from the database.

        Args:
            date (str): The date in the format 'YYYY-MM-DD'.

        Returns:
            object: The data for the specified date.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        return self.session.scalars(select(self.table).join(self.relation).where(self.table.id == unique_id)).first()

    def get_range(
        self,
        begin,
        end,
        order="desc",
    ):
        """Retrieve a range of data from the database.

        Args:
            begin (datetime): The start of the range.
            end (datetime): The end of the range.
            order (str, optional): The order direction. Defaults to "desc".

        Returns:
            list: A list of data records within the specified range.
        """
        if order == "desc":
            order = self.table.date.desc()
        else:
            order = self.table.date.asc()
        query = (
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .where(self.table.date >= begin)
            .where(self.table.date <= end)
            .order_by(order)
        )
        logging.debug(query.compile(compile_kwargs={"literal_binds": True}))
        current_data = self.session.scalars(query).all()
        if current_data is None:
            return False
        else:
            return current_data

    def get(self, begin, end):
        """Retrieve data for a specific range from the database.

        Args:
            begin (datetime): The start of the range.
            end (datetime): The end of the range.

        Returns:
            dict: A dictionary containing the retrieved data.
        """
        delta = begin - begin

        result = {"missing_data": False, "date": {}, "count": 0}

        for _ in range(delta.days + 1):
            query_result = self.get_all(
                begin=begin,
                end=end,
            )
            time_delta = abs(int((begin - end).total_seconds() / 60))
            total_internal = 0
            for query in query_result:
                total_internal = total_internal + query.interval
            total_time = abs(total_internal - time_delta)
            if total_time > self.min_entry:
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

    def get_state(self, date):
        """Get the state of a specific data record in the database.

        Args:
            date (datetime): The date of the data record.

        Returns:
            bool: True if the data record exists, False otherwise.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        current_data = self.session.scalars(
            select(self.table).join(self.relation).where(self.table.id == unique_id)
        ).one_or_none()
        if current_data is None:
            return False
        else:
            return True

    def insert(  # noqa: PLR0913
        self,
        date,
        value,
        interval,
        blacklist=0,
        fail_count=0,
    ):
        """Insert a new record into the database for the given consumption or production detail.

        Args:
            date (datetime): The date of the record.
            value (float): The value of the record.
            interval (int): The interval of the record.
            blacklist (int, optional): The blacklist status of the record. Defaults to 0.
            fail_count (int, optional): The fail count of the record. Defaults to 0.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        detail = self.get_date(date)
        if detail is not None:
            detail.id = unique_id
            detail.usage_point_id = self.usage_point_id
            detail.date = date
            detail.value = value
            detail.interval = interval
            detail.measure_type = self.measurement_direction
            detail.blacklist = blacklist
            detail.fail_count = fail_count
        else:
            self.session.add(
                self.table(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=self.measurement_direction,
                    blacklist=blacklist,
                    fail_count=fail_count,
                )
            )
        self.session.flush()

    def reset(self, date=None):
        """Reset the values of a consumption or production detail record.

        Args:
            date (datetime, optional): The date of the record. Defaults to None.

        Returns:
            bool: True if the reset was successful, False otherwise.
        """
        detail = self.get_date(date)
        if detail is not None:
            detail.value = 0
            detail.interval = 0
            detail.blacklist = 0
            detail.fail_count = 0
            self.session.flush()
            return True
        else:
            return False

    def reset_range(self, begin, end):
        """Reset the values of consumption or production detail records within a specified range.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.

        Returns:
            bool: True if the reset was successful, False otherwise.
        """
        detail = self.get_range(begin, end)
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

    def delete(self, date=None):
        """Delete a consumption or production detail record.

        Args:
            date (datetime, optional): The date of the record. Defaults to None.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if date is not None:
            unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
            self.session.execute(delete(self.table).where(self.table.id == unique_id))
        else:
            self.session.execute(delete(self.table).where(self.table.usage_point_id == self.usage_point_id))
        self.session.flush()
        return True

    def delete_range(self, date):
        """Delete a range of consumption or production detail records.

        Args:
            date (datetime): The date of the records to be deleted.

        Returns:
            bool: True if the deletion was successful, False otherwise.
        """
        if date is not None:
            unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
            self.session.execute(delete(self.table).where(self.table.id == unique_id))
        else:
            self.session.execute(delete(self.table).where(self.table.usage_point_id == self.usage_point_id))
        self.session.flush()
        return True

    def get_ratio_hc_hp(self, begin, end):
        """Calculate the ratio of high consumption (HC) to high production (HP) for a given usage point and time range.

        Args:
            begin (datetime): The start date of the range.
            end (datetime): The end date of the range.

        Returns:
            dict: A dictionary with the ratio of HC and HP.
        """
        result = {
            "HC": 0,
            "HP": 0,
        }
        detail_data = self.get_all(
            begin=begin,
            end=end,
        )
        for data in detail_data:
            result[data.measure_type] = result[data.measure_type] + data.value
        return result

    def get_fail_count(self, date):
        """Get the fail count for a specific usage point, date, and measurement type.

        Args:
            date (datetime): The date of the record.

        Returns:
            int: The fail count for the specified usage point, date, and measurement type.
        """
        return self.get_detail_date(date).fail_count

    def fail_increment(self, date):
        """Increment the fail count for a specific usage point, date, and measurement type.

        Args:
            date (datetime): The date of the record.

        Returns:
            int: The updated fail count.
        """
        unique_id = hashlib.md5(f"{self.usage_point_id}/{date}".encode("utf-8")).hexdigest()  # noqa: S324
        query = select(self.table).join(self.relation).where(self.table.id == unique_id)
        detail = self.session.scalars(query).one_or_none()
        if detail is not None:
            fail_count = int(detail.fail_count) + 1
            if fail_count >= MAX_IMPORT_TRY:
                blacklist = 1
                fail_count = 0
            else:
                blacklist = 0
            detail.usage_point_id = self.usage_point_id
            detail.date = date
            detail.value = 0
            detail.interval = 0
            detail.measure_type = "HP"
            detail.blacklist = blacklist
            detail.fail_count = fail_count
        else:
            fail_count = 0
            self.session.add(
                self.table(
                    id=unique_id,
                    usage_point_id=self.usage_point_id,
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

    def get_last_date(self):
        """Get the last date for a specific usage point and measurement type.

        Returns:
            datetime: The last date for the specified usage point and measurement type.
        """
        current_data = self.session.scalars(
            select(self.table)
            .join(self.relation)
            .where(self.table.usage_point_id == self.usage_point_id)
            .order_by(self.table.date)
        ).first()
        if current_data is None:
            return False
        else:
            return current_data.date

    def get_first_date(self):
        """Get the first date for a specific usage point and measurement type.

        Returns:
            datetime: The first date for the specified usage point and measurement type.
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

    def get_date_range(self):
        """Get the date range (begin and end dates) for a specific usage point.

        Returns:
            dict: A dictionary containing the begin and end dates.
        """
        return {
            "begin": self.get_last_date(self.usage_point_id),
            "end": self.get_first_date(self.usage_point_id),
        }
