import calendar
import json
import logging
from datetime import datetime, timezone, timedelta, date

import pytz
from dateutil.relativedelta import relativedelta

from init import CONFIG, DB

utc = pytz.UTC

now_date = datetime.now(timezone.utc)
yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())

class Stat:

    def __init__(self, usage_point_id, measurement_direction=None):
        self.config = CONFIG
        self.db = DB
        self.usage_point_id = usage_point_id
        self.measurement_direction = measurement_direction
        self.usage_point_id_config = self.db.get_usage_point(self.usage_point_id)
        self.usage_point_id_contract = self.db.get_contract(self.usage_point_id)
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
        self.usage_point_id_contract = self.db.get_contract(self.usage_point_id)

    def daily(self, index=0):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            value = value + data.value
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def detail(self, index, measure_type=None):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
            if measure_type is None or (measure_type == "HP" and data.measure_type == "HP"):
                value = value + data.value / (60 / data.interval)
            elif measure_type is None or (measure_type == "HC" and data.measure_type == "HC"):
                value = value + data.value / (60 / data.interval)
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def tempo(self, index):
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
        for data in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
            # print(data)
            hour = int(datetime.strftime(data.date, "%H"))
            if hour < 6:
                color = self.db.get_tempo_range(begin - timedelta(days=1), end - timedelta(days=1))[0].color
                color = f"{color.lower()}_hc"
            elif hour >= 22:
                color = self.db.get_tempo_range(begin + timedelta(days=1), end + timedelta(days=1))[0].color
                color = f"{color.lower()}_hc"
            else:
                color = self.db.get_tempo_range(begin, end)[0].color
                color = f"{color.lower()}_hp"
            value[color] += data.value / (60 / data.interval)
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def tempo_color(self, index=0):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = ""
        for data in self.db.get_tempo_range(begin, end):
            logging.info(f"tempo data: {data}")
            value = value + data.color
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }
        
    def max_power(self, index=0):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        # print(self.db.get_daily_max_power_range(self.usage_point_id, begin, end))
        for data in self.db.get_daily_max_power_range(self.usage_point_id, begin, end):
            # print(data)
            value = value + data.value
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def max_power_over(self, index=0):
        max_power = 0
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        if hasattr(self.usage_point_id_contract,
                   "subscribed_power") and self.usage_point_id_contract.subscribed_power is not None:
            max_power = int(self.usage_point_id_contract.subscribed_power.split(' ')[0])
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        boolv = "true"
        for data in self.db.get_daily_max_power_range(self.usage_point_id, begin, end):
            value = value + data.value
            if (value / 1000) < max_power:
                boolv = "false"
        return {
            "value": boolv,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def max_power_time(self, index=0):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        max_power_time = ''
        # print(self.db.get_daily_max_power_range(self.usage_point_id, begin, end))
        for data in self.db.get_daily_max_power_range(self.usage_point_id, begin, end):
            # print(data)
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
            "end": end.strftime(self.date_format)
        }
        return data

    def current_week_array(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        begin_return = begin
        end = datetime.combine(yesterday_date, datetime.max.time())
        day_idx = 0
        daily_obj = []
        while day_idx < 7:
            day = self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction)
            if day:
                daily_obj.append({
                    "date": day[0].date,
                    "value": day[0].value
                })
            else:
                daily_obj.append({
                    "date": begin,
                    "value": 0
                })
            begin = begin - timedelta(days=1)
            end = end - timedelta(days=1)
            day_idx = day_idx + 1
        return {
            "value": daily_obj,
            "begin": begin_return,
            "end": end
        }

    def current_week(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date - relativedelta(weeks=1), datetime.min.time())
        end = datetime.combine(yesterday_date, datetime.max.time())
        for data in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_week = self.value_current_week + data.value
        logging.debug(f" current_week => {self.value_current_week}")
        return {
            "value": self.value_current_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    # def get_week(self, year):
    #     logging.debug(f"[{year}] current_week")
    #     begin = datetime.combine(now_date - relativedelta(weeks=1), datetime.min.time())
    #     end = datetime.combine(yesterday_date, datetime.max.time())
    #     for data in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
    #         self.value_current_week = self.value_current_week + data.value
    #     logging.debug(f" {self.value_current_week}")
    #     return {
    #         "value": self.value_current_week,
    #         "begin": begin.strftime(self.date_format),
    #         "end": end.strftime(self.date_format)
    #     }

    def last_week(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date - relativedelta(weeks=2), datetime.min.time())
        end = datetime.combine(yesterday_date - relativedelta(weeks=1), datetime.max.time())
        # while day_idx < 7:
        #     day = self.db.get_daily_range(self.usage_point_id, begin, end, self.self.measurement_direction)
        #     if day:
        #         for data in day:
        #             last_week = last_week + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        for data in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_last_week = self.value_last_week + data.value
        logging.debug(f" last_week => {self.value_last_week}")
        return {
            "value": self.value_last_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_week_evolution(self):
        if self.value_last_week != 0:
            self.value_current_week_evolution = ((self.value_current_week * 100) / self.value_last_week) - 100
        logging.debug(f" current_week_evolution => {self.value_current_week_evolution}")
        return self.value_current_week_evolution

    def yesterday(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        end = datetime.combine(yesterday_date, datetime.max.time())
        data = self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction)
        if data:
            self.value_yesterday = data[0].value
        else:
            self.value_yesterday = 0
        logging.debug(f" yesterday => {self.value_yesterday}")
        return {
            "value": self.value_yesterday,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_1(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date - timedelta(days=1), datetime.min.time())
        end = datetime.combine(yesterday_date - timedelta(days=1), datetime.max.time())
        data = self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction)
        if data:
            self.value_yesterday_1 = data[0].value
        else:
            self.value_yesterday_1 = 0
        logging.debug(f" yesterday_1 => {self.value_yesterday_1}")
        return {
            "value": self.value_yesterday_1,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_evolution(self):
        self.yesterday()
        self.yesterday_1()
        if self.value_yesterday_1 != 0:
            self.value_yesterday_evolution = ((100 * self.value_yesterday) / self.value_yesterday_1) - 100
        logging.debug(f" yesterday_evolution => {self.value_yesterday_evolution}")
        return self.value_yesterday_evolution

    def current_week_last_year(self):
        # begin = datetime.combine(yesterday - relativedelta(years=1), datetime.min.time())
        # end = datetime.combine(yesterday - relativedelta(years=1), datetime.max.time())
        # day_idx = 0
        # while day_idx < 7:
        #     day = self.db.get_daily_range(self.usage_point_id, begin, end, self.self.measurement_direction)
        #     if day:
        #         for data in day:
        #             current_week_last_year = current_week_last_year + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine((now_date - timedelta(weeks=1)) - relativedelta(years=1), datetime.min.time())
        end = datetime.combine(yesterday_date - relativedelta(years=1), datetime.max.time())
        for data in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_week_last_year = self.value_current_week_last_year + data.value
        logging.debug(f" current_week_last_year => {self.value_current_week_last_year}")
        return {
            "value": self.value_current_week_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_month(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine((now_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                                 datetime.min.time())
        end = datetime.combine(yesterday_date.replace(day=1) - timedelta(days=1), datetime.max.time())
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_last_month = self.value_last_month + day.value
        logging.debug(f" last_month => {self.value_last_month}")
        return {
            "value": self.value_last_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(day=1), datetime.min.time())
        end = yesterday_date
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_month = self.value_current_month + day.value
        logging.debug(f" current_month => {self.value_current_month}")
        return {
            "value": self.value_current_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_last_year(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(day=1), datetime.min.time()) - relativedelta(years=1)
        end = yesterday_date - relativedelta(years=1)
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_month_last_year = self.value_current_month_last_year + day.value
        logging.debug(f" current_month_last_year => {self.value_current_month_last_year}")
        return {
            "value": self.value_current_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_evolution(self):
        if self.value_current_month_last_year != 0:
            self.value_current_month_evolution = (
                                                         (
                                                                 100 * self.value_current_month) / self.value_current_month_last_year
                                                 ) - 100
        logging.debug(f" current_month_evolution => {self.value_current_month_evolution}")
        return self.value_current_month_evolution

    def last_month_last_year(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            (now_date.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time()) - relativedelta(years=1)
        end = datetime.combine(
            yesterday_date.replace(day=1) - timedelta(days=1),
            datetime.max.time()) - relativedelta(years=1)
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_last_month_last_year = self.value_last_month_last_year + day.value
        logging.debug(f" last_month_last_year => {self.value_last_month_last_year}")
        return {
            "value": self.value_last_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def monthly_evolution(self):
        self.last_month()
        self.last_month_last_year()
        if self.value_last_month_last_year != 0:
            self.value_monthly_evolution = ((100 * self.value_last_month) / self.value_last_month_last_year) - 100
        logging.debug(f" monthly_evolution => {self.value_monthly_evolution}")
        return self.value_monthly_evolution

    def current_year(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(now_date.replace(month=1, day=1), datetime.min.time())
        end = yesterday_date
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_year = self.value_current_year + day.value
        logging.debug(f" current_year => {self.value_current_year}")
        return {
            "value": self.value_current_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_year_last_year(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(
            datetime.combine(now_date.replace(month=1, day=1), datetime.min.time()) - relativedelta(
                years=1),
            datetime.min.time())
        end = yesterday_date - relativedelta(years=1)
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_current_year_last_year = self.value_current_year_last_year + day.value
        logging.debug(f" current_year_last_year => {self.value_current_year_last_year}")
        return {
            "value": self.value_current_year_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_year(self):
        now_date = datetime.now(timezone.utc)
        begin = datetime.combine(now_date.replace(month=1, day=1) - relativedelta(years=1),
                                 datetime.min.time())
        last_day_of_month = calendar.monthrange(int(begin.strftime("%Y")), 12)[1]
        end = datetime.combine(begin.replace(month=1, day=last_day_of_month), datetime.max.time())
        for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
            self.value_last_year = self.value_last_year + day.value
        logging.debug(f" last_year => {self.value_last_year}")
        return {
            "value": self.value_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yearly_evolution(self):
        self.current_year()
        self.current_year_last_year()
        if self.value_last_month_last_year != 0:
            self.value_yearly_evolution = ((100 * self.value_current_year) / self.value_current_year_last_year) - 100
        logging.debug(f" yearly_evolution => {self.value_yearly_evolution}")
        return self.value_yearly_evolution

    def yesterday_hc_hp(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = datetime.combine(yesterday_date, datetime.min.time())
        end = datetime.combine(now_date, datetime.max.time())
        for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
            if day.measure_type == "HP":
                self.value_yesterday_hp = self.value_yesterday_hp + (day.value / (60 / day.interval))
            if day.measure_type == "HC":
                self.value_yesterday_hc = self.value_yesterday_hc + (day.value / (60 / day.interval))
        logging.debug(f" yesterday_hc => HC : {self.value_yesterday_hc}")
        logging.debug(f" yesterday_hp => HP : {self.value_yesterday_hp}")
        return {
            "value": {
                "hc": self.value_yesterday_hc,
                "hp": self.value_yesterday_hp
            },
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def peak_offpeak_percent(self):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        begin = yesterday_date - relativedelta(years=1)
        end = yesterday_date
        value_peak_offpeak_percent_hp = 0
        value_peak_offpeak_percent_hc = 0
        value_peak_offpeak_percent_hp_vs_hc = 0
        for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
            if day.measure_type == "HP":
                value_peak_offpeak_percent_hp = value_peak_offpeak_percent_hp + day.value
            if day.measure_type == "HC":
                value_peak_offpeak_percent_hc = value_peak_offpeak_percent_hc + day.value
        if value_peak_offpeak_percent_hc != 0:
            value_peak_offpeak_percent_hp_vs_hc = abs(((100 * value_peak_offpeak_percent_hc) / value_peak_offpeak_percent_hp) - 100)
        logging.debug(f" peak_offpeak_percent_hp VS peak_offpeak_percent_hc => {value_peak_offpeak_percent_hp_vs_hc}")
        return value_peak_offpeak_percent_hp_vs_hc

    # STAT V2
    def get_year(self, year, measure_type=None):
        now_date = datetime.now(timezone.utc)
        begin = datetime.combine(now_date.replace(year=year, month=1, day=1), datetime.min.time())
        last_day_of_month = calendar.monthrange(year, 12)[1]
        end = datetime.combine(now_date.replace(year=year, month=12, day=last_day_of_month),
                               datetime.max.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_year_linear(self, idx, measure_type=None):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - relativedelta(years=1), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_month(self, year, month=None, measure_type=None):
        now_date = datetime.now(timezone.utc)
        if month is None:
            month = int(datetime.now().strftime('%m'))
        begin = datetime.combine(now_date.replace(year=year, month=month, day=1),
                                 datetime.min.time())
        last_day_of_month = calendar.monthrange(year, month)[1]
        end = datetime.combine(now_date.replace(year=year, month=month, day=last_day_of_month),
                               datetime.max.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_month_linear(self, idx, measure_type=None):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - relativedelta(months=1), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_week(self, year, month=None, measure_type=None):
        now_date = datetime.now(timezone.utc)
        if month is None:
            month = int(datetime.now().strftime('%m'))
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        begin = datetime.combine(
            now_date.replace(year=year, month=month, day=int(start.strftime("%d"))),
            datetime.min.time())
        end = datetime.combine(
            now_date.replace(year=year, month=month, day=int(start.strftime("%d"))),
            datetime.max.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_week_linear(self, idx, measure_type=None):
        now_date = datetime.now(timezone.utc)
        yesterday_date = datetime.combine(now_date - relativedelta(days=1), datetime.max.time())
        end = datetime.combine(yesterday_date - relativedelta(years=idx), datetime.max.time())
        begin = datetime.combine(end - timedelta(days=7), datetime.min.time())
        value = 0
        if measure_type is None:
            for day in self.db.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction):
                value = value + day.value
        else:
            for day in self.db.get_detail_range(self.usage_point_id, begin, end, self.measurement_direction):
                if day.measure_type == measure_type:
                    value = value + (day.value / (60 / day.interval))
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def get_price(self):
        data = self.db.get_stat(self.usage_point_id, f"price_{self.measurement_direction}")
        return json.loads(data[0].value)
        # return ast.literal_eval()

    def generate_price(self):
        data = self.db.get_detail_all(self.usage_point_id, self.measurement_direction)
        result = {}
        last_month = ""
        if data:
            tempo_config = self.db.get_tempo_config("price")
            tempo_data = self.db.get_tempo_range(data[0].date, data[-1].date)
            for item in data:
                year = item.date.strftime("%Y")
                month = item.date.strftime("%m")
                if month != last_month:
                    logging.info(f" - {year} / {month}")
                measure_type = item.measure_type
                tempo_date = datetime.combine(item.date, datetime.min.time())
                interval = item.interval
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
                        "month": {}
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
                        "HP": {"euro": 0, "kWh": 0, "Wh": 0}
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
                kwh = (wh / 1000)
                # YEARS
                result[year]["BASE"]["Wh"] += wh
                result[year]["BASE"]["kWh"] += kwh
                result[year]["BASE"]["euro"] += (kwh * price)
                result[year][measure_type]["Wh"] += wh
                result[year][measure_type]["kWh"] += kwh
                result[year][measure_type]["euro"] += (kwh * price_hc_hp)

                # MONTH
                result[year]["month"][month]["BASE"]["Wh"] += wh
                result[year]["month"][month]["BASE"]["kWh"] += kwh
                result[year]["month"][month]["BASE"]["euro"] += (kwh * price)
                result[year]["month"][month][measure_type]["Wh"] += wh
                result[year]["month"][month][measure_type]["kWh"] += kwh
                result[year]["month"][month][measure_type]["euro"] += (kwh * price_hc_hp)

                # TEMPO
                if tempo_config:
                    hour = int(item.date.strftime("%H"))
                    if 6 <= hour < 22:
                        measure_type = "HP"
                    else:
                        measure_type = "HC"
                    tempo_output = [x for x in tempo_data if x.date == tempo_date]
                    if tempo_output:
                        color = tempo_output[0].color
                        tempo_price = tempo_config[f"{color.lower()}_{measure_type.lower()}"]
                        if type(tempo_price) == str:
                            tempo_price = float(tempo_price.replace(",", "."))
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["Wh"] += wh
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["kWh"] += kwh
                        result[year]["TEMPO"][f"{color}_{measure_type}"]["euro"] += kwh * tempo_price
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["Wh"] += wh
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["kWh"] += kwh
                        result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["euro"] += kwh * tempo_price
                last_month = month
            self.db.set_stat(self.usage_point_id, f"price_{self.measurement_direction}", json.dumps(result))
        return json.dumps(result)

    def delete(self):
        self.db.del_stat(self.usage_point_id)

# w = item.value
# kw = (item.value / 1000) / (60 / interval)
#
# # YEARS
# result[year]["BASE"]["w"] += w
# result[year]["BASE"]["kw"] += kw
# result[year]["BASE"]["euro"] += kw * price
# result[year][measure_type]["w"] += w
# result[year][measure_type]["kw"] += kw
# result[year][measure_type]["euro"] += (kw * price_hc_hp)
#
# # MONTH
# result[year]["month"][month]["BASE"]["w"] += w
# result[year]["month"][month]["BASE"]["kw"] += kw
# result[year]["month"][month]["BASE"]["euro"] += (kw * price)
# result[year]["month"][month][measure_type]["w"] += w
# result[year]["month"][month][measure_type]["kw"] += kw
# result[year]["month"][month][measure_type]["euro"] += (kw * price_hc_hp)
#
# # TEMPO
# if tempo_config:
#     hour = int(item.date.strftime("%H"))
#     if 6 <= hour < 22:
#         measure_type = "HP"
#     else:
#         measure_type = "HC"
#     tempo_output = [x for x in tempo_data if x.date == tempo_date]
#     if tempo_output:
#         color = tempo_output[0].color
#
#         tempo_price = tempo_config[f"price_{color.lower()}_{measure_type.lower()}"]
#         result[year]["TEMPO"][f"{color}_{measure_type}"]["w"] += w
#         result[year]["TEMPO"][f"{color}_{measure_type}"]["kw"] += kw
#         result[year]["TEMPO"][f"{color}_{measure_type}"]["euro"] += (kw * tempo_price)
#         result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["w"] += w
#         result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["kw"] += kw
#         result[year]["month"][month]["TEMPO"][f"{color}_{measure_type}"]["euro"] += (kw * tempo_price)
# last_month = month
