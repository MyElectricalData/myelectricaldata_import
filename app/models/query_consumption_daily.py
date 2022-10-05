import json
import sys

import datetime

from dateutil.relativedelta import relativedelta

from models.config import get_version
from models.query import Query
from models.log import log, debug, critical
from config import URL, DAILY_MAX_DAYS
from dependencies import CACHE


class ConsumptionDaily:

    def __init__(self, headers, usage_point_id, config, activation_date, offpeak_hours):

        self.cache = CACHE
        self.url = URL

        self.headers = headers
        self.usage_point_id = usage_point_id
        self.config = config
        self.activation_date = activation_date
        self.offpeak_hours = offpeak_hours

        self.daily_max_days = DAILY_MAX_DAYS
        self.max_days_date = datetime.datetime.utcnow() - relativedelta(days=self.daily_max_days)
        base_price = self.config['consumption_price_base']


    def get(self):
        current_cache = self.cache.get_consumption_daily(usage_point_id=self.usage_point_id)
        if current_cache is None:
            # No cache
            log(f" => No cache")
            return self.run()
        else:
            # Refresh cache
            if "refresh_consumption_daily" in self.config and self.config["refresh_consumption_daily"]:
                log(f" => Refresh Cache")
                return self.run()
            else:
                # Get data in cache
                log(f" => Query Cache")
                consumption_daily = json.loads(current_cache[1])
                self.cache.insert_consumption_daily(
                    usage_point_id=self.usage_point_id,
                    consumption_daily=consumption_daily,
                )
                return consumption_daily
