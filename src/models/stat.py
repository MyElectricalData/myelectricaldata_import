"""Generate all statistical data for a usage point."""
import calendar
import json
import logging
from datetime import date, datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from const import TEMPO_BEGIN, TEMPO_END
from database.contracts import DatabaseContracts
from database.daily import DatabaseDaily
from database.detail import DatabaseDetail
from database.max_power import DatabaseMaxPower
from database.statistique import DatabaseStatistique
from database.tempo import DatabaseTempo
from database.usage_points import DatabaseUsagePoints
from utils import is_between

now_date = datetime.now(timezone.utc)
yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())


class Stat:  # pylint: disable=R0902,R0904
    """The 'Stat' class represents a statistical analysis tool for a usage point.

    It provides various methods to calculate and retrieve statistical data related to the usage point.

    Attributes:
        - config: The configuration object for the usage point.
        - db: The database object for accessing data related to the usage point.
        - usage_point_id: The ID of the usage point.
        - measurement_direction: The measurement direction for the usage point.
        - usage_point_id_config: The configuration object for the usage point ID.
        - usage_point_id_contract: The contract object for the usage point ID.
        - date_format: The format string for date representation.
        - date_format_detail: The format string for detailed date representation.
        - value_current_week: The value of the current week.
        - value_current_week_last_year: The value of the current week in the last year.
        - value_last_week: The value of the last week.
        - value_yesterday: The value of yesterday.
        - value_yesterday_1: The value of the day before yesterday.
        - value_last_month: The value of the last month.
        - value_current_month: The value of the current month.
        - value_current_month_last_year: The value of the current month in the last year.
        - value_last_month_last_year: The value of the last month in the last year.
        - value_current_year: The value of the current year.
        - value_current_year_last_year: The value of the current year in the last year.
        - value_last_year: The value of the last year.
        - value_yesterday_hp: The value of yesterday for high peak measurement type.
        - value_yesterday_hc: The value of yesterday for high consumption measurement type.
        - value_peak_offpeak_percent_hp: The percentage value of peak and off-peak for high peak measurement type.
        - value_peak_offpeak_percent_hc: The percentage value of peak and off-peak for high consumption.
        - value_current_week_evolution: The evolution value of the current week.
        - value_yesterday_evolution: The evolution value of yesterday.
        - value_current_month_evolution: The evolution value of the current month.
        - value_peak_offpeak_percent_hp_vs_hc: The percentage value of peak and off-peak for high peak/consumption.
        - value_monthly_evolution: The evolution value of the monthly data.
        - value_yearly_evolution: The evolution value of the yearly data.

    Methods:
        - daily(index=0): Returns the daily data for the specified index.
        - detail(index, measure_type=None): Returns the detailed data for the specified index and measure type.
        - tempo(index): Returns the tempo data for the specified index.
        - tempo_color(index=0): Returns the tempo color data for the specified index.
        - max_power(index=0): Returns the maximum power data for the specified index.
        - max_power_over(index=0): Returns the maximum power over data for the specified index.
        - max_power_time(index=0): Returns the maximum power time data for the specified index.
        - current_week_array(): Returns the current week data as an array.
        - current_week(): Returns the current week data.
        - last_week(): Returns the last week data.
        - current_week_evolution(): Returns the evolution value of the current week.
        - yesterday(): Returns the yesterday data.
        - yesterday_1(): Returns the day before yesterday data.
        - yesterday_evolution(): Returns the evolution value of yesterday.
        - current_week_last_year(): Returns the current week data in the last year.
        - last_month(): Returns the last month data.
        - current_month(): Returns the current month data.
        - current_month_last_year(): Returns the current month data in the last year.
        - current_month_evolution(): Returns the evolution value of the current month.
        - last_month_last_year(): Returns the last month data in the last year.
        - monthly_evolution(): Returns the evolution value of the monthly data.
        - current_year(): Returns the current year data.
        - current_year_last_year(): Returns the current year data in the last year.
        - last_year(): Returns the last year data.
        - yearly_evolution(): Returns the evolution value of the yearly data.
        - yesterday_hc_hp(): Returns the yesterday data for high consumption and high peak measurement types.
        - peak_offpeak_percent(): Returns the percentage value of peak and off-peak.
        - get_year(year, measure_type=None): Returns the yearly data for the specified year and measure type.
        - get_year_linear(idx, measure_type=None): Returns the linear yearly data for the specified index and
                                                   measure type.
        - get_month(year, month=None, measure_type=None): Returns the monthly data for the specified year, month,
                                                          and measure type.
        - get_month_linear(idx, measure_type=None): Returns the linear monthly data for the specified index
                                                    and measure type.
        - get_week(year, month=None, measure_type=None): Returns the weekly data for the specified year, month,
                                                         and measure type.
        - get_week_linear(idx, measure_type=None): Returns the linear weekly data for the specified index
                                                   and measure type.
        - get_price(): Returns the price data.
        - get_mesure_type(date): Returns the measure type for the specified date.
        - generate_price(): Generates and saves the price data.
        - get_daily(date, mesure_type): Returns the daily data for the specified date and measure type.
        - delete(): Deletes the statistical data for the usage point.
    """

    def __init__(self, usage_point_id, measurement_direction=None):
        """Initialize a new instance of the 'Stat' class.

        Parameters:
            usage_point_id (int): The ID of the usage point.
            measurement_direction (str, optional): The measurement direction for the usage point. Defaults to None.

        Attributes:
            config (object): The configuration object for the usage point.
            db (object): The database object for accessing data related to the usage point.
            usage_point_id (int): The ID of the usage point.
            measurement_direction (str): The measurement direction for the usage point.
            usage_point_id_config (object): The configuration object for the usage point ID.
            usage_point_id_contract (object): The contract object for the usage point ID.
            date_format (str): The format string for date representation.
            date_format_detail (str): The format string for detailed date representation.
            value_current_week (int): The value of the current week.
            value_current_week_last_year (int): The value of the current week in the last year.
            value_last_week (int): The value of the last week.
            value_yesterday (int): The value of yesterday.
            value_yesterday_1 (int): The value of the day before yesterday.
            value_last_month (int): The value of the last month.
            value_current_month (int): The value of the current month.
            value_current_month_last_year (int): The value of the current month in the last year.
            value_last_month_last_year (int): The value of the last month in the last year.
            value_current_year (int): The value of the current year.
            value_current_year_last_year (int): The value of the current year in the last year.
            value_last_year (int): The value of the last year.
            value_yesterday_hp (int): The value of yesterday for high peak measurement type.
            value_yesterday_hc (int): The value of yesterday for high consumption measurement type.
            value_peak_offpeak_percent_hp (int): The percentage value of peak and off-peak for high peak
                                                 measurement type.
            value_peak_offpeak_percent_hc (int): The percentage value of peak and off-peak for high consumption
                                                 measurement type.
            value_current_week_evolution (int): The evolution value of the current week.
            value_yesterday_evolution (int): The evolution value of yesterday.
            value_current_month_evolution (int): The evolution value of the current month.
            value_peak_offpeak_percent_hp_vs_hc (int): The percentage value of peak and off-peak for high peak and
                                                       high consumption measurement types.
            value_monthly_evolution (int): The evolution value of the monthly data.
            value_yearly_evolution (int): The evolution value of the yearly data.

        Returns:
            None
        """
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        self.usage_point_id_config = DatabaseUsagePoints(self.usage_point_id).get()
        self.usage_point_id_contract = DatabaseContracts(self.usage_point_id).get()
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        # STAT
        self.value_current_week = 0
        self.value_current_week_last_year = 0
        self.value_last_week = 0
        self.value_yesterday = 0
        self.value_yesterday_1 = 0
        self.value_last_month = 0
        self.value_current_month = 0
        self.value_current_month_last_year = 0
        self.value_last_month_last_year = 0
        self.value_current_year = 0
        self.value_current_year_last_year = 0
        self.value_last_year = 0
        self.value_yesterday_hp = 0
        self.value_yesterday_hc = 0
        self.value_peak_offpeak_percent_hp = 0
        self.value_peak_offpeak_percent_hc = 0
        self.value_current_week_evolution = 0
        self.value_yesterday_evolution = 0
        self.value_current_month_evolution = 0
        self.value_peak_offpeak_percent_hp_vs_hc = 0
        self.value_monthly_evolution = 0
        self.value_yearly_evolution = 0
        self.usage_point_id_contract = DatabaseContracts(self.usage_point_id).get()

    def daily(self, index=0):
        """Calculate the daily value for the given index.

        Args:
            index (int, optional): The index for the number of days ago. Defaults to 0.

        Returns:
            dict: A dictionary containing the calculated value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            value = value + data.value
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def detail(self, index, measure_type=None):
        """Calculate the detailed value for the given index and measure type.

        Args:
            index (int): The index for the number of days ago.
            measure_type (str, optional): The measure type (HP or HC). Defaults to None.

        Returns:
            dict: A dictionary containing the calculated value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            day_measure_type = self.get_mesure_type(data.date)
            day_interval = data.interval if hasattr(data, "interval") and data.interval != 0 else 1
            if measure_type is None or (measure_type == "HP" and day_measure_type == "HP"):
                value = value + data.value / (60 / day_interval)
            elif measure_type is None or (measure_type == "HC" and day_measure_type == "HC"):
                value = value + data.value / (60 / day_interval)
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def tempo(self, index):
        """Calculate the tempo value for the given index.

        Args:
            index (int): The index for the number of days ago.

        Returns:
            dict: A dictionary containing the calculated value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = {
            "blue_hc": 0,
            "blue_hp": 0,
            "white_hc": 0,
            "white_hp": 0,
            "red_hc": 0,
            "red_hp": 0,
        }
        for data in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            hour = int(datetime.strftime(data.date, "%H"))
            if hour < TEMPO_BEGIN:
                color = DatabaseTempo().get_range(begin - timedelta(days=1), end - timedelta(days=1))[0].color
                color = f"{color.lower()}_hc"
            elif hour >= TEMPO_END:
                color = DatabaseTempo().get_range(begin + timedelta(days=1), end + timedelta(days=1))[0].color
                color = f"{color.lower()}_hc"
            else:
                color = DatabaseTempo().get_range(begin, end)[0].color
                color = f"{color.lower()}_hp"
            value[color] += data.value / (60 / data.interval)
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def tempo_color(self, index=0):
        """Calculate the tempo color for the given index.

        Args:
            index (int, optional): The index for the number of days ago. Defaults to 0.

        Returns:
            dict: A dictionary containing the tempo color value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = ""
        for data in DatabaseTempo().get_range(begin, end):
            logging.debug(f"tempo data: {data}")
            value = value + data.color
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def max_power(self, index=0):
        """Calculate the maximum power for the given index.

        Args:
            index (int, optional): The index for the number of days ago. Defaults to 0.

        Returns:
            dict: A dictionary containing the maximum power value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in DatabaseMaxPower(self.usage_point_id).get_range(begin, end):
            value = value + data.value
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def max_power_over(self, index=0):
        """Calculate if the maximum power is exceeded for the given index.

        Args:
            index (int, optional): The index for the number of days ago. Defaults to 0.

        Returns:
            dict: A dictionary indicating if the maximum power is exceeded, begin date, and end date.
        """
        max_power = 0
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        if (
            hasattr(self.usage_point_id_contract, "subscribed_power")
            and self.usage_point_id_contract.subscribed_power is not None
        ):
            max_power = int(self.usage_point_id_contract.subscribed_power.split(" ")[0])
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        boolv = "true"
        for data in DatabaseMaxPower(self.usage_point_id).get_range(begin, end):
            value = value + data.value
            if (value / 1000) < max_power:
                boolv = "false"
        return {
            "value": boolv,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def max_power_time(self, index=0):
        """Calculate the maximum power time for the given index.

        Args:
            index (int, optional): The index for the number of days ago. Defaults to 0.

        Returns:
            dict: A dictionary containing the maximum power time value, begin date, and end date.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        max_power_time = ""
        for data in DatabaseMaxPower(self.usage_point_id).get_range(begin, end):
            if data.event_date is None or data.event_date == "":
                max_power_time = data.date
            else:
                max_power_time = data.event_date
        if isinstance(max_power_time, datetime):
            value = max_power_time.strftime(self.date_format_detail)
        else:
            value = None
        data = {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }
        return data

    def current_week_array(self):
        """Calculate the array of values for the current week.

        Returns:
            list: A list containing the values for each day of the current week.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        begin_return = begin
        end = datetime.combine(yesterday_date, datetime.max.time())
        day_idx = 0
        daily_obj = []
        id_max = 7
        while day_idx < id_max:
            day = DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end)
            if day:
                daily_obj.append({"date": day[0].date, "value": day[0].value})
            else:
                daily_obj.append({"date": begin, "value": 0})
            begin = begin - timedelta(days=1)
            end = end - timedelta(days=1)
            day_idx = day_idx + 1
        return {"value": daily_obj, "begin": begin_return, "end": end}

    def current_week(self):
        """Calculate the total value for the current week.

        Returns:
            dict: A dictionary containing the total value, begin date, and end date of the current week.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date - relativedelta(weeks=1), datetime.min.time())
        end = datetime.combine(yesterday_date, datetime.max.time())
        for data in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_week = self.value_current_week + data.value
        logging.debug(f" current_week => {self.value_current_week}")
        return {
            "value": self.value_current_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def last_week(self):
        """Calculate the total value for the last week.

        Returns:
            dict: A dictionary containing the total value, begin date, and end date of the last week.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date - relativedelta(weeks=2), datetime.min.time())
        end = datetime.combine(yesterday_date - relativedelta(weeks=1), datetime.max.time())
        for data in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_last_week = self.value_last_week + data.value
        logging.debug(f" last_week => {self.value_last_week}")
        return {
            "value": self.value_last_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def current_week_evolution(self):
        """Calculate the evolution of the current week's value compared to the previous week.

        Returns:
            float: The percentage change in value between the current week and the previous week.
        """
        if self.value_last_week != 0:
            self.value_current_week_evolution = ((self.value_current_week * 100) / self.value_last_week) - 100
        logging.debug(f" current_week_evolution => {self.value_current_week_evolution}")
        return self.value_current_week_evolution

    def yesterday(self):
        """Calculate the value for yesterday.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of yesterday.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        end = datetime.combine(yesterday_date, datetime.max.time())
        data = DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end)
        if data:
            self.value_yesterday = data[0].value
        else:
            self.value_yesterday = 0
        logging.debug(f" yesterday => {self.value_yesterday}")
        return {
            "value": self.value_yesterday,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def yesterday_1(self):
        """Calculate the value for the day before yesterday.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the day before yesterday.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=1), datetime.min.time())
        end = datetime.combine(yesterday_date - timedelta(days=1), datetime.max.time())
        data = DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end)
        if data:
            self.value_yesterday_1 = data[0].value
        else:
            self.value_yesterday_1 = 0
        logging.debug(f" yesterday_1 => {self.value_yesterday_1}")
        return {
            "value": self.value_yesterday_1,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def yesterday_evolution(self):
        """Calculate the evolution of the value for yesterday compared to the day before yesterday.

        Returns:
            float: The percentage change in value between yesterday and the day before yesterday.
        """
        self.yesterday()
        self.yesterday_1()
        if self.value_yesterday_1 != 0:
            self.value_yesterday_evolution = ((100 * self.value_yesterday) / self.value_yesterday_1) - 100
        logging.debug(f" yesterday_evolution => {self.value_yesterday_evolution}")
        return self.value_yesterday_evolution

    def current_week_last_year(self):
        """Calculate the value for the current week of the last year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the current week of the last year.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            (now_date - timedelta(weeks=1)) - relativedelta(years=1),
            datetime.min.time(),
        )
        end = datetime.combine(yesterday_date - relativedelta(years=1), datetime.max.time())
        for data in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_week_last_year = self.value_current_week_last_year + data.value
        logging.debug(f" current_week_last_year => {self.value_current_week_last_year}")
        return {
            "value": self.value_current_week_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def last_month(self):
        """Calculate the value for the last month.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the last month.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            (now_date.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time(),
        )
        end = datetime.combine(yesterday_date.replace(day=1) - timedelta(days=1), datetime.max.time())
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_last_month = self.value_last_month + day.value
        logging.debug(f" last_month => {self.value_last_month}")
        return {
            "value": self.value_last_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def current_month(self):
        """Calculate the value for the current month.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the current month.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(day=1), datetime.min.time())
        end = yesterday_date
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_month = self.value_current_month + day.value
        logging.debug(f" current_month => {self.value_current_month}")
        return {
            "value": self.value_current_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def current_month_last_year(self):
        """Calculate the value for the current month of the last year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the current month of the last year.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(day=1), datetime.min.time()) - relativedelta(years=1)
        end = yesterday_date - relativedelta(years=1)
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_month_last_year = self.value_current_month_last_year + day.value
        logging.debug(f" current_month_last_year => {self.value_current_month_last_year}")
        return {
            "value": self.value_current_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def current_month_evolution(self):
        """Calculate the evolution of the current month compared to the same month of the previous year.

        Returns:
            float: The percentage evolution of the current month.
        """
        if self.value_current_month_last_year != 0:
            self.value_current_month_evolution = (
                (100 * self.value_current_month) / self.value_current_month_last_year
            ) - 100
        logging.debug(f" current_month_evolution => {self.value_current_month_evolution}")
        return self.value_current_month_evolution

    def last_month_last_year(self):
        """Calculate the value for the last month of the last year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the last month of the last year.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            (now_date.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time(),
        ) - relativedelta(years=1)
        end = datetime.combine(yesterday_date.replace(day=1) - timedelta(days=1), datetime.max.time()) - relativedelta(
            years=1
        )
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_last_month_last_year = self.value_last_month_last_year + day.value
        logging.debug(f" last_month_last_year => {self.value_last_month_last_year}")
        return {
            "value": self.value_last_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def monthly_evolution(self):
        """Calculate the monthly evolution based on the last month and the last month of the previous year.

        Returns:
            float: The percentage monthly evolution.
        """
        self.last_month()
        self.last_month_last_year()
        if self.value_last_month_last_year != 0:
            self.value_monthly_evolution = ((100 * self.value_last_month) / self.value_last_month_last_year) - 100
        logging.debug(f" monthly_evolution => {self.value_monthly_evolution}")
        return self.value_monthly_evolution

    def current_year(self):
        """Calculate the value for the current year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the current year.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(month=1, day=1), datetime.min.time())
        end = yesterday_date
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_year = self.value_current_year + day.value
        logging.debug(f" current_year => {self.value_current_year}")
        return {
            "value": self.value_current_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def current_year_last_year(self):
        """Calculate the value for the current year of the last year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the current year of the last year.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            datetime.combine(now_date.replace(month=1, day=1), datetime.min.time()) - relativedelta(years=1),
            datetime.min.time(),
        )
        end = yesterday_date - relativedelta(years=1)
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_current_year_last_year = self.value_current_year_last_year + day.value
        logging.debug(f" current_year_last_year => {self.value_current_year_last_year}")
        return {
            "value": self.value_current_year_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def last_year(self):
        """Calculate the value for the last year.

        Returns:
            dict: A dictionary containing the value, begin date, and end date of the last year.
        """
        now_date = datetime.now(timezone.utc)
        begin = datetime.combine(
            now_date.replace(month=1, day=1) - relativedelta(years=1),
            datetime.min.time(),
        )
        last_day_of_month = calendar.monthrange(int(begin.strftime("%Y")), 12)[1]
        end = datetime.combine(begin.replace(month=1, day=last_day_of_month), datetime.max.time())
        for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            self.value_last_year = self.value_last_year + day.value
        logging.debug(f" last_year => {self.value_last_year}")
        return {
            "value": self.value_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def yearly_evolution(self):
        """Calculate the yearly evolution based on the current year and the last year.

        Returns:
            float: The percentage yearly evolution.
        """
        self.current_year()
        self.current_year_last_year()
        if self.value_last_month_last_year != 0:
            self.value_yearly_evolution = ((100 * self.value_current_year) / self.value_current_year_last_year) - 100
        logging.debug(f" yearly_evolution => {self.value_yearly_evolution}")
        return self.value_yearly_evolution

    def yesterday_hc_hp(self):
        """Calculate the value for yesterday's HC and HP.

        Returns:
            dict: A dictionary containing the values for HC and HP, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        end = datetime.combine(now_date, datetime.max.time())
        for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            measure_type = self.get_mesure_type(day.date)
            day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
            if measure_type == "HP":
                self.value_yesterday_hp = self.value_yesterday_hp + (day.value / (60 / day_interval))
            if measure_type == "HC":
                self.value_yesterday_hc = self.value_yesterday_hc + (day.value / (60 / day_interval))
        logging.debug(f" yesterday_hc => HC : {self.value_yesterday_hc}")
        logging.debug(f" yesterday_hp => HP : {self.value_yesterday_hp}")
        return {
            "value": {"hc": self.value_yesterday_hc, "hp": self.value_yesterday_hp},
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def peak_offpeak_percent(self):
        """Calculate the percentage difference between peak and off-peak values.

        Returns:
            float: The percentage difference between peak and off-peak values.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = yesterday_date - relativedelta(years=1)
        end = yesterday_date
        value_peak_offpeak_percent_hp = 0
        value_peak_offpeak_percent_hc = 0
        value_peak_offpeak_percent_hp_vs_hc = 0
        for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            measure_type = self.get_mesure_type(day.date)
            if measure_type == "HP":
                value_peak_offpeak_percent_hp = value_peak_offpeak_percent_hp + day.value
            if measure_type == "HC":
                value_peak_offpeak_percent_hc = value_peak_offpeak_percent_hc + day.value
        if value_peak_offpeak_percent_hc != 0:
            value_peak_offpeak_percent_hp_vs_hc = abs(
                ((100 * value_peak_offpeak_percent_hc) / value_peak_offpeak_percent_hp) - 100
            )
        logging.debug(f" peak_offpeak_percent_hp VS peak_offpeak_percent_hc => {value_peak_offpeak_percent_hp_vs_hc}")
        return value_peak_offpeak_percent_hp_vs_hc

    # STAT V2
    def get_year(self, year, measure_type=None):
        """Retrieve the data for a specific year.

        Args:
            year (int): The year for which to retrieve the data.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        begin = datetime.combine(now_date.replace(year=year, month=1, day=1), datetime.min.time())
        last_day_of_month = calendar.monthrange(year, 12)[1]
        end = datetime.combine(
            now_date.replace(year=year, month=12, day=last_day_of_month),
            datetime.max.time(),
        )
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_year_linear(self, idx, measure_type=None):
        """Retrieve the linear data for a specific year.

        Args:
            idx (int): The index of the year.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - relativedelta(years=1), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_month(self, year, month=None, measure_type=None):
        """Retrieve the data for a specific month.

        Args:
            year (int): The year for which to retrieve the data.
            month (int, optional): The month for which to retrieve the data. Defaults to None.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        if month is None:
            month = int(datetime.now().strftime("%m"))
        begin = datetime.combine(now_date.replace(year=year, month=month, day=1), datetime.min.time())
        last_day_of_month = calendar.monthrange(year, month)[1]
        end = datetime.combine(
            now_date.replace(year=year, month=month, day=last_day_of_month),
            datetime.max.time(),
        )
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_month_linear(self, idx, measure_type=None):
        """Retrieve the linear data for a specific month.

        Args:
            idx (int): The index of the month.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - relativedelta(months=1), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_week(self, year, month=None, measure_type=None):
        """Retrieve the data for a specific week.

        Args:
            year (int): The year for which to retrieve the data.
            month (int, optional): The month for which to retrieve the data. Defaults to None.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        if month is None:
            month = int(datetime.now().strftime("%m"))
        # adapt for day in leap-year
        if datetime.now().strftime("%m%d") == "0229" and int(year) != int(datetime.now().strftime("%Y")):
            today = date.today() + timedelta(days=1)
        else:
            today = date.today()
        start = today.replace(year=year, month=month) - timedelta(days=today.replace(year=year, month=month).weekday())
        end = start + timedelta(days=6)
        begin = datetime.combine(
            start,
            datetime.min.time(),
        )
        end = datetime.combine(
            end,
            datetime.max.time(),
        )
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_week_linear(self, idx, measure_type=None):
        """Retrieve the linear data for a specific week.

        Args:
            idx (int): The index of the week.
            measure_type (str, optional): The type of measurement. Defaults to None.

        Returns:
            dict: A dictionary containing the retrieved data, along with the begin and end dates.
        """
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - timedelta(days=7), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in DatabaseDaily(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                value = value + day.value
        else:
            for day in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
                day_measure_type = self.get_mesure_type(day.date)
                if day_measure_type == measure_type:
                    day_interval = day.interval if hasattr(day, "interval") and day.interval != 0 else 1
                    value = value + (day.value / (60 / day_interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format),
        }

    def get_price(self):
        """Retrieve the price data for the measurement direction.

        Returns:
            dict: A dictionary containing the price data.
        """
        data = DatabaseStatistique(self.usage_point_id).get(f"price_{self.measurement_direction}")
        if len(data) == 0:
            return {}
        return json.loads(data[0].value)

    def get_mesure_type(self, measurement_date):
        """Determine the measurement type (HP or HC) based on the given date and off-peak hours.

        Args:
            measurement_date (datetime): The date for which to determine the measurement type.

        Returns:
            str: The measurement type, either "HP" (high peak) or "HC" (off-peak).
        """
        offpeak_hours = {}
        for i in range(0, 7):
            offpeak_hours[i] = getattr(self.usage_point_id_config, f"offpeak_hours_{i}")
        # GET WEEKDAY
        date_days = measurement_date.weekday()
        date_hour_minute = measurement_date.strftime("%H:%M")
        measure_type = "HP"
        day_offpeak_hours = offpeak_hours[date_days]
        if day_offpeak_hours is not None:
            for offpeak_hour in day_offpeak_hours.split(";"):
                if offpeak_hour != "None" and offpeak_hour != "" and offpeak_hour is not None:
                    offpeak_begin = offpeak_hour.split("-")[0].replace("h", ":").replace("H", ":")
                    # FORMAT HOUR WITH 2 DIGIT
                    offpeak_begin = datetime.strptime(offpeak_begin, "%H:%M")
                    offpeak_begin = datetime.strftime(offpeak_begin, "%H:%M")
                    offpeak_stop = offpeak_hour.split("-")[1].replace("h", ":").replace("H", ":")
                    # FORMAT HOUR WITH 2 DIGIT
                    offpeak_stop = datetime.strptime(offpeak_stop, "%H:%M")
                    offpeak_stop = datetime.strftime(offpeak_stop, "%H:%M")
                    result = is_between(date_hour_minute, (offpeak_begin, offpeak_stop))
                    if result:
                        measure_type = "HC"
        return measure_type

    def generate_price(self):  # noqa: C901, PLR0912, PLR0915
        """Generate the price for the usage point based on the measurement data.

        Returns:
            str: JSON string representing the calculated price.
        """
        data = DatabaseDetail(self.usage_point_id, self.measurement_direction).get_all()
        result = {}
        last_month = ""
        if data:
            tempo_config = DatabaseTempo().get_config("price")
            tempo_data = DatabaseTempo().get_range(data[0].date, data[-1].date)
            for item in data:
                year = item.date.strftime("%Y")
                month = item.date.strftime("%m")
                if month != last_month:
                    logging.info(f" - {year} / {month}")

                measure_type = self.get_mesure_type(item.date)

                tempo_date = datetime.combine(item.date, datetime.min.time())
                interval = item.interval if hasattr(item, "interval") and item.interval != 0 else 1
                if year not in result:
                    result[year] = {
                        "BASE": {"euro": 0, "kWh": 0, "Wh": 0},
                        "TEMPO": {
                            "BLUE_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "BLUE_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                            "WHITE_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "WHITE_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                            "RED_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "RED_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                        },
                        "HC": {"euro": 0, "kWh": 0, "Wh": 0},
                        "HP": {"euro": 0, "kWh": 0, "Wh": 0},
                        "month": {},
                    }
                if month not in result[year]["month"]:
                    result[year]["month"][month] = {
                        "BASE": {"euro": 0, "kWh": 0, "Wh": 0},
                        "TEMPO": {
                            "BLUE_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "BLUE_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                            "WHITE_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "WHITE_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                            "RED_HC": {"euro": 0, "kWh": 0, "Wh": 0},
                            "RED_HP": {"euro": 0, "kWh": 0, "Wh": 0},
                        },
                        "HC": {"euro": 0, "kWh": 0, "Wh": 0},
                        "HP": {"euro": 0, "kWh": 0, "Wh": 0},
                    }
                if self.measurement_direction == "consumption":
                    price = self.usage_point_id_config.consumption_price_base
                else:
                    price = self.usage_point_id_config.production_price
                if measure_type == "HP":
                    price_hc_hp = self.usage_point_id_config.consumption_price_hp
                else:
                    price_hc_hp = self.usage_point_id_config.consumption_price_hc
                wh = (item.value) / (60 / interval)
                kwh = wh / 1000
                # YEARS
                result[year]["BASE"]["Wh"] += wh
                result[year]["BASE"]["kWh"] += kwh
                result[year]["BASE"]["euro"] += kwh * price
                result[year][measure_type]["Wh"] += wh
                result[year][measure_type]["kWh"] += kwh
                result[year][measure_type]["euro"] += kwh * price_hc_hp

                # MONTH
                result[year]["month"][month]["BASE"]["Wh"] += wh
                result[year]["month"][month]["BASE"]["kWh"] += kwh
                result[year]["month"][month]["BASE"]["euro"] += kwh * price
                result[year]["month"][month][measure_type]["Wh"] += wh
                result[year]["month"][month][measure_type]["kWh"] += kwh
                result[year]["month"][month][measure_type]["euro"] += kwh * price_hc_hp

                # TEMPO
                if tempo_config:
                    hour = int(item.date.strftime("%H"))
                    if TEMPO_BEGIN <= hour < TEMPO_END:
                        measure_type = "HP"
                    else:
                        measure_type = "HC"
                    tempo_output = [x for x in tempo_data if x.date == tempo_date]
                    if tempo_output:
                        color = tempo_output[0].color
                        tempo_price = tempo_config[f"{color.lower()}_{measure_type.lower()}"]
                        if isinstance(tempo_price, str):
                            tempo_price = float(tempo_price.replace(",", "."))
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["Wh"] += wh
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["kWh"] += kwh
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["euro"] += kwh * tempo_price
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["Wh"] += wh
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["kWh"] += kwh
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["euro"] += kwh * tempo_price
                last_month = month
            DatabaseStatistique(self.usage_point_id).set(
                f"price_{self.measurement_direction}",
                json.dumps(result),
            )
        else:
            logging.error(" => Aucune donnée en cache.")
        return json.dumps(result)

    def get_daily(self, specific_date, mesure_type):
        """Get the daily value for a specific date and measurement type.

        Args:
            specific_date (datetime.date): The date for which to retrieve the daily value.
            mesure_type (str): The measurement type.

        Returns:
            float: The daily value.
        """
        begin = datetime.combine(specific_date, datetime.min.time())
        end = datetime.combine(specific_date, datetime.max.time())
        value = 0
        for item in DatabaseDetail(self.usage_point_id, self.measurement_direction).get_range(begin, end):
            if self.get_mesure_type(item.date).upper() == mesure_type.upper():
                day_interval = item.interval if hasattr(item, "interval") and item.interval != 0 else 1
                value += item.value / (60 / day_interval)
        return value

    def delete(self):
        """Delete the data from the database."""
        DatabaseStatistique(self.usage_point_id).delete()
