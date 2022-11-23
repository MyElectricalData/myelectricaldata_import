import __main__ as app
import calendar
from datetime import datetime, timezone, timedelta

import pytz
from dateutil.relativedelta import relativedelta

utc = pytz.UTC


class Stat:

    def __init__(self, usage_point_id):
        self.usage_point_id = usage_point_id
        self.usage_point_id_config = app.DB.get_usage_point(self.usage_point_id)
        self.date_format = "%Y-%m-%d"
        self.date_format_detail = "%Y-%m-%d %H:%M:%S"
        self.now_date = datetime.now(timezone.utc)
        self.yesterday_date = datetime.combine(self.now_date - relativedelta(days=1), datetime.max.time())
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

    def daily(self, index=0, measurement_direction="consumption"):
        begin = datetime.combine(self.yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            value = value + data.value
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def detail(self, index, measure_type=None, measurement_direction="consumption"):
        begin = datetime.combine(self.yesterday_date - timedelta(days=index), datetime.min.time())
        end = datetime.combine(begin, datetime.max.time())
        value = 0
        for data in app.DB.get_detail_range(self.usage_point_id, begin, end, measurement_direction):
            if measure_type is None or (measure_type == "HP" and data.measure_type == "HP"):
                value = value + data.value / (60 / data.interval)
            elif measure_type is None or (measure_type == "HC" and data.measure_type == "HC"):
                value = value + data.value / (60 / data.interval)
        return {
            "value": value,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_week_array(self, measurement_direction="consumption"):
        begin = datetime.combine(self.yesterday_date, datetime.min.time())
        begin_return = begin
        end = datetime.combine(self.yesterday_date, datetime.max.time())
        day_idx = 0
        daily_obj = []
        while day_idx < 7:
            day = app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction)
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

    def current_week(self, measurement_direction="consumption"):
        app.LOG.log(" - current_week")
        begin = datetime.combine(self.now_date - relativedelta(weeks=1), datetime.min.time())
        end = datetime.combine(self.yesterday_date, datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_week = self.value_current_week + data.value
        return {
            "value": self.value_current_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_week(self, measurement_direction="consumption"):
        app.LOG.log(" - last_week")
        begin = datetime.combine(self.now_date - relativedelta(weeks=2), datetime.min.time())
        end = datetime.combine(self.yesterday_date - relativedelta(weeks=1), datetime.max.time())
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction)
        #     if day:
        #         for data in day:
        #             last_week = last_week + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_last_week = self.value_last_week + data.value
        return {
            "value": self.value_last_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_week_evolution(self):
        app.LOG.log(" - current_week_evolution")
        if self.value_current_week != 0:
            return ((self.value_current_week * 100) / self.value_last_week) - 100
        else:
            return 0

    def yesterday(self, measurement_direction="consumption"):
        app.LOG.log(" - yesterday")
        begin = datetime.combine(self.yesterday_date, datetime.min.time())
        end = datetime.combine(self.yesterday_date, datetime.max.time())
        data = app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction)
        if data:
            self.value_yesterday = data[0].value
        else:
            self.value_yesterday = 0
        return {
            "value": self.value_yesterday,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_1(self, measurement_direction="consumption"):
        app.LOG.log(" - yesterday_1")
        begin = datetime.combine(self.yesterday_date - timedelta(days=1), datetime.min.time())
        end = datetime.combine(self.yesterday_date - timedelta(days=1), datetime.max.time())
        data = app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction)
        if data:
            self.value_yesterday_1 = data[0].value
        else:
            self.value_yesterday_1 = 0
        return {
            "value": self.value_yesterday_1,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_evolution(self):
        app.LOG.log(" - yesterday_evolution")
        self.yesterday()
        self.yesterday_1()
        if self.value_yesterday != 0:
            return ((100 * self.value_yesterday) / self.value_yesterday_1) - 100
        else:
            return 0

    def current_week_last_year(self, measurement_direction="consumption"):
        app.LOG.log(" - current_week_last_year")
        # begin = datetime.combine(yesterday - relativedelta(years=1), datetime.min.time())
        # end = datetime.combine(yesterday - relativedelta(years=1), datetime.max.time())
        # day_idx = 0
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.measurement_direction)
        #     if day:
        #         for data in day:
        #             current_week_last_year = current_week_last_year + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        begin = datetime.combine((self.now_date - timedelta(weeks=1)) - relativedelta(years=1), datetime.min.time())
        end = datetime.combine(self.yesterday_date - relativedelta(years=1), datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_week_last_year = self.value_current_week_last_year + data.value
        return {
            "value": self.value_current_week_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_month(self, measurement_direction="consumption"):
        app.LOG.log(" - last_month")
        begin = datetime.combine((self.now_date.replace(day=1) - timedelta(days=1)).replace(day=1), datetime.min.time())
        end = datetime.combine(self.yesterday_date.replace(day=1) - timedelta(days=1), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_last_month = self.value_last_month + day.value
        return {
            "value": self.value_last_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month(self, measurement_direction="consumption"):
        app.LOG.log(" - current_month")
        begin = datetime.combine(self.now_date.replace(day=1), datetime.min.time())
        end = self.yesterday_date
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_month = self.value_current_month + day.value
        return {
            "value": self.value_current_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_last_year(self, measurement_direction="consumption"):
        app.LOG.log(" - current_month_last_year")
        begin = datetime.combine(self.now_date.replace(day=1), datetime.min.time()) - relativedelta(years=1)
        end = self.yesterday_date - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_month_last_year = self.value_current_month_last_year + day.value
        return {
            "value": self.value_current_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_evolution(self):
        app.LOG.log(" - current_month_evolution")
        if self.value_current_month != 0:
            # return (self.value_current_month - self.value_current_month_last_year) * 100 / self.value_current_month
            return ((100 * self.value_current_month) / self.value_current_month_last_year) - 100
        else:
            return 0

    def last_month_last_year(self, measurement_direction="consumption"):
        app.LOG.log(" - last_month_last_year")
        begin = datetime.combine(
            (self.now_date.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time()) - relativedelta(years=1)
        end = datetime.combine(
            self.yesterday_date.replace(day=1) - timedelta(days=1),
            datetime.max.time()) - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_last_month_last_year = self.value_last_month_last_year + day.value
        return {
            "value": self.value_last_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def monthly_evolution(self):
        app.LOG.log(" - monthly_evolution")
        self.last_month()
        self.last_month_last_year()
        if self.value_last_month != 0:
            # return (self.value_last_month - self.value_last_month_last_year) * 100 / self.value_last_month
            return ((100 * self.value_last_month) / self.value_last_month_last_year) - 100
        else:
            return 0

    def current_year(self, measurement_direction="consumption"):
        app.LOG.log(" - current_year")
        begin = datetime.combine(self.now_date.replace(month=1).replace(day=1), datetime.min.time())
        end = self.yesterday_date
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_year = self.value_current_year + day.value
        return {
            "value": self.value_current_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_year_last_year(self, measurement_direction="consumption"):
        app.LOG.log(" - current_year_last_year")
        begin = datetime.combine(
            datetime.combine(self.now_date.replace(month=1).replace(day=1), datetime.min.time()) - relativedelta(years=1),
            datetime.min.time())
        end = self.yesterday_date - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_current_year_last_year = self.value_current_year_last_year + day.value
        return {
            "value": self.value_current_year_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_year(self, measurement_direction="consumption"):
        app.LOG.log(" - last_year")
        begin = datetime.combine(self.now_date.replace(month=1).replace(day=1) - relativedelta(years=1),
                                 datetime.min.time())
        last_day_of_month = calendar.monthrange(int(begin.strftime("%Y")), 12)[1]
        end = datetime.combine(begin.replace(day=last_day_of_month).replace(month=12), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, measurement_direction):
            self.value_last_year = self.value_last_year + day.value
        return {
            "value": self.value_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_hc_hp(self, measurement_direction="consumption"):
        app.LOG.log(" - yesterday_hp / yesterday_hc")
        begin = datetime.combine(self.yesterday_date, datetime.min.time())
        end = datetime.combine(self.now_date, datetime.max.time())
        for day in app.DB.get_detail_range(self.usage_point_id, begin, end, measurement_direction):
            if day.measure_type == "HP":
                self.value_yesterday_hp = self.value_yesterday_hp + (day.value / (60 / day.interval))
            if day.measure_type == "HC":
                self.value_yesterday_hc = self.value_yesterday_hc + (day.value / (60 / day.interval))
        return {
            "value": {
                "hc": self.value_yesterday_hc,
                "hp": self.value_yesterday_hp
            },
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def peak_offpeak_percent(self, measurement_direction="consumption"):
        app.LOG.log(" - peak_offpeak_percent_hp / peak_offpeak_percent_hc")
        begin = self.yesterday_date - relativedelta(years=1)
        end = self.yesterday_date
        for day in app.DB.get_detail_range(self.usage_point_id, begin, end, measurement_direction):
            if day.measure_type == "HP":
                self.value_peak_offpeak_percent_hp = self.value_peak_offpeak_percent_hp + (
                            day.value / (60 / day.interval))
            if day.measure_type == "HC":
                self.value_peak_offpeak_percent_hc = self.value_peak_offpeak_percent_hc + (
                            day.value / (60 / day.interval))

        if self.value_peak_offpeak_percent_hp != 0:
            return (self.value_peak_offpeak_percent_hp - self.value_peak_offpeak_percent_hc) * 100 / self.value_peak_offpeak_percent_hp
        else:
            return 0
