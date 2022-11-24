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
        self.now = datetime.now(timezone.utc)
        self.yesterday = datetime.combine(self.now - relativedelta(days=1), datetime.max.time())
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

    def current_week_array(self, mesure_type):
        begin = datetime.combine(self.yesterday, datetime.min.time())
        begin_return = begin
        end = datetime.combine(self.yesterday, datetime.max.time())
        day_idx = 0
        daily_obj = []
        while day_idx < 7:
            day = app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type)
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

    def current_week(self, mesure_type):
        app.LOG.log(" - current_week")
        begin = datetime.combine(self.now - relativedelta(weeks=1), datetime.min.time())
        end = datetime.combine(self.yesterday, datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_week = self.value_current_week + data.value
        return {
            "value": self.value_current_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_week(self, mesure_type):
        app.LOG.log(" - last_week")
        begin = datetime.combine(self.now - relativedelta(weeks=2), datetime.min.time())
        end = datetime.combine(self.yesterday - relativedelta(weeks=1), datetime.max.time())
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        #     if day:
        #         for data in day:
        #             last_week = last_week + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_last_week = self.value_last_week + data.value
        return {
            "value": self.value_last_week,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_week_evolution(self):
        app.LOG.log(" - current_week_evolution")
        if self.value_current_week != 0:
            return (self.value_current_week - self.value_last_week) * 100 / self.value_current_week
        else:
            return 0

    def yesterday(self, mesure_type):
        app.LOG.log(" - yesterday")
        begin = datetime.combine(self.yesterday, datetime.min.time())
        end = datetime.combine(self.now, datetime.max.time())
        data = app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type)
        if data:
            self.value_yesterday = data[0].value
        else:
            self.value_yesterday = 0
        return {
            "value": self.value_yesterday,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_1(self, mesure_type):
        app.LOG.log(" - yesterday_1")
        begin = datetime.combine(self.yesterday - timedelta(days=1), datetime.min.time())
        end = datetime.combine(self.now - timedelta(days=1), datetime.max.time())
        data = app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type)
        if data:
            self.value_yesterday_1 = data[0].value
        else:
            self.value_yesterday_1 = 0
        return {
            "value": self.yesterday_1,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def yesterday_evolution(self):
        app.LOG.log(" - yesterday_evolution")
        if self.value_yesterday != 0:
            return (self.value_yesterday - self.value_yesterday_1) * 100 / self.value_yesterday
        else:
            return 0

    def current_week_last_year(self, mesure_type):
        app.LOG.log(" - current_week_last_year")
        # begin = datetime.combine(yesterday - relativedelta(years=1), datetime.min.time())
        # end = datetime.combine(yesterday - relativedelta(years=1), datetime.max.time())
        # day_idx = 0
        # while day_idx < 7:
        #     day = app.DB.get_daily_range(self.usage_point_id, begin, end, self.mesure_type)
        #     if day:
        #         for data in day:
        #             current_week_last_year = current_week_last_year + data.value
        #     begin = begin - timedelta(days=1)
        #     end = end - timedelta(days=1)
        #     day_idx = day_idx + 1
        begin = datetime.combine((self.now - timedelta(weeks=1)) - relativedelta(years=1), datetime.min.time())
        end = datetime.combine(self.yesterday - relativedelta(years=1), datetime.max.time())
        for data in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_week_last_year = self.value_current_week_last_year + data.value
        return {
            "value": self.value_current_week_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_month(self, mesure_type):
        app.LOG.log(" - last_month")
        begin = datetime.combine((self.now.replace(day=1) - timedelta(days=1)).replace(day=1), datetime.min.time())
        end = datetime.combine(self.yesterday.replace(day=1) - timedelta(days=1), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_last_month = self.value_last_month + day.value
        return {
            "value": self.value_last_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month(self, mesure_type):
        app.LOG.log(" - current_month")
        begin = datetime.combine(self.now.replace(day=1), datetime.min.time())
        end = self.yesterday
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_month = self.value_current_month + day.value
        return {
            "value": self.value_current_month,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_last_year(self, mesure_type):
        app.LOG.log(" - current_month_last_year")
        begin = datetime.combine(self.now.replace(day=1), datetime.min.time()) - relativedelta(years=1)
        end = self.yesterday - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_month_last_year = self.value_current_month_last_year + day.value
        return {
            "value": self.value_current_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_month_evolution(self):
        app.LOG.log(" - current_month_evolution")
        if self.value_current_month != 0:
            return (self.value_current_month - self.value_current_month_last_year) * 100 / self.value_current_month
        else:
            return 0

    def last_month_last_year(self, mesure_type):
        app.LOG.log(" - last_month_last_year")
        begin = datetime.combine(
            (self.now.replace(day=1) - timedelta(days=1)).replace(day=1),
            datetime.min.time()) - relativedelta(years=1)
        end = datetime.combine(
            self.yesterday.replace(day=1) - timedelta(days=1),
            datetime.max.time()) - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_month_last_year = self.value_current_month_last_year + day.value
        return {
            "value": self.value_current_month_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def monthly_evolution(self):
        app.LOG.log(" - monthly_evolution")
        if self.value_last_month != 0:
            return (self.value_last_month - self.value_last_month_last_year) * 100 / self.value_last_month
        else:
            return 0

    def current_year(self, mesure_type):
        app.LOG.log(" - current_year")
        begin = datetime.combine(self.now.replace(month=1).replace(day=1), datetime.min.time())
        end = self.yesterday
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_year = self.value_current_year + day.value
        return {
            "value": self.value_current_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def current_year_last_year(self, mesure_type):
        app.LOG.log(" - current_year_last_year")
        begin = datetime.combine(
            datetime.combine(self.now.replace(month=1).replace(day=1), datetime.min.time()) - relativedelta(years=1),
            datetime.min.time())
        end = self.yesterday - relativedelta(years=1)
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_current_year_last_year = self.value_current_year_last_year + day.value
        return {
            "value": self.value_current_year_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }

    def last_year(self, mesure_type):
        app.LOG.log(" - last_year")
        begin = datetime.combine(self.now.replace(month=1).replace(day=1) - relativedelta(years=1),
                                 datetime.min.time())
        last_day_of_month = calendar.monthrange(int(begin.strftime("%Y")), 12)[1]
        end = datetime.combine(begin.replace(day=last_day_of_month).replace(month=12), datetime.max.time())
        for day in app.DB.get_daily_range(self.usage_point_id, begin, end, mesure_type):
            self.value_last_year = self.value_last_year + day.value
        return {
            "value": self.value_last_year,
            "begin": begin.strftime(self.date_format),
            "end": end.strftime(self.date_format)
        }
