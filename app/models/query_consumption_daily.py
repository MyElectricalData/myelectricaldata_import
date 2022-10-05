import datetime

from dateutil.relativedelta import relativedelta

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

        self.base_price = self.config['consumption_price_base']

    def run(self, begin, end):

        response = {}

        lastYears = datetime.datetime.strptime(end, '%Y-%m-%d')
        lastYears = lastYears + relativedelta(years=-1)
        if lastYears < self.activation_date:
            dateBegin = self.activation_date
            dateBegin = dateBegin.strftime('%Y-%m-%d')

        response['dateBegin'] = begin
        response['dateEnded'] = end

        data = {
            "type": f"daily_consumption",
            "usage_point_id": str(self.usage_point_id),
            "start": str(begin),
            "end": str(end),
        }

        try:
            current_data = self.cache.get_consumption_daily(usage_point_id=self.usage_point_id, begin=begin, end=end)
            print(current_data)

    #         new_date = []
    #         current_data = checkHistoryDaily(cur, mode, pdl, dateBegin, dateEnded)
    #         mesures = {}
    #         if current_data['missing_data'] == False:
    #             f.log(f"All data loading beetween {dateBegin} / {dateEnded}")
    #             f.log(f" => Load data from cache")
    #             for date, data in current_data['date'].items():
    #                 mesures[date] = data['value']
    #         else:
    #             f.log(f"Data is missing between {dateBegin} / {dateEnded}")
    #             f.log(f" => Load data from API")
    #             daily = f.apiRequest(cur, con, pdl, type="POST", url=f"{url}", headers=headers, data=json.dumps(data))
    #             if not "error_code" in daily:
    #                 meter_reading = daily['meter_reading']
    #                 f.log("Import data :")
    #                 for interval_reading in meter_reading["interval_reading"]:
    #                     date = interval_reading['date']
    #                     value = interval_reading['value']
    #                     cur.execute(
    #                         f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{interval_reading['date']}','{interval_reading['value']}','0')")
    #                     new_date.append(interval_reading['date'])
    #                     mesures[date] = value
    #                 f.splitLog(new_date)
    #
    #                 not_found_data = []
    #                 for date, date_data in current_data['date'].items():
    #                     if not date in new_date:
    #                         not_found_data.append(date)
    #                         current_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
    #                         current_day = datetime.datetime.today().date()
    #                         if date_data['fail'] == 0 and date_data['value'] == 0:
    #                             if current_day == current_date:
    #                                 fail = 0
    #                             else:
    #                                 fail = 1
    #                             cur.execute(
    #                                 f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{date}','0','{fail}')")
    #                             # cur.execute(f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{date}','0','1')")
    #                         else:
    #                             if current_day != current_date:
    #                                 fail = 0
    #                             else:
    #                                 fail = date_data['fail']
    #                             cur.execute(
    #                                 f"UPDATE {mode}_daily SET fail = {fail + 1} WHERE pdl = '{pdl}' and date = '{date}'")
    #                             # cur.execute(f"UPDATE {mode}_daily SET fail = {date_data['fail'] + 1} WHERE pdl = '{pdl}' and date = '{date}'")
    #
    #                 if not_found_data != []:
    #                     f.log("Data not found :")
    #                     f.splitLog(not_found_data)
    #
    #             elif daily['error_code'] == 2:
    #                 f.log(f"Fetch data error detected beetween {dateBegin} / {dateEnded}")
    #                 f.log(f" => Load data from cache")
    #                 for date, data in current_data['date'].items():
    #                     mesures[date] = data['value']
    #
    #         list_date = list(reversed(sorted(mesures.keys())))
    #
    #         dateEnded = datetime.datetime.strptime(dateEnded, '%Y-%m-%d')
    #         dateWeek = dateEnded + relativedelta(days=-7)
    #         dateMonths = dateEnded + relativedelta(months=-1)
    #         dateYears = dateEnded + relativedelta(years=-1)
    #         j1 = dateEnded + relativedelta(days=-1)
    #         j1 = j1.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j2 = dateEnded + relativedelta(days=-2)
    #         j2 = j2.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j3 = dateEnded + relativedelta(days=-3)
    #         j3 = j3.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j4 = dateEnded + relativedelta(days=-4)
    #         j4 = j4.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j5 = dateEnded + relativedelta(days=-5)
    #         j5 = j5.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j6 = dateEnded + relativedelta(days=-6)
    #         j6 = j6.replace(hour=0, minute=0, second=0, microsecond=0)
    #         j7 = dateEnded + relativedelta(days=-7)
    #         j7 = j7.replace(hour=0, minute=0, second=0)
    #
    #         energyWeek = 0
    #         energyMonths = 0
    #         energyYears = 0
    #
    #         for date in list_date:
    #             value = int(mesures[date])
    #             current_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    #             day = current_date.strftime('%A')
    #
    #             # WEEK DAYS
    #             if current_date == j1:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j2:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j3:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j4:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j5:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j6:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             if current_date == j7:
    #                 response[f"{day}"] = {
    #                     "value": value,
    #                     "date": date
    #                 }
    #             # LAST WEEK
    #             if current_date >= dateWeek:
    #                 energyWeek = int(energyWeek) + int(value)
    #             # LAST MONTH
    #             if current_date >= dateMonths:
    #                 energyMonths = int(energyMonths) + int(value)
    #             # LAST YEARS
    #             if current_date >= dateYears:
    #                 energyYears = int(energyYears) + int(value)
    #
    #         response['this_week'] = {
    #             "value": energyWeek,
    #             "date": date
    #         }
    #         response['this_month'] = {
    #             "value": energyMonths,
    #             "date": date
    #         }
    #         response['this_year'] = {
    #             "value": energyYears,
    #             "date": date
    #         }
        except Exception as e:
            log("=====> ERROR : Exception <======")
            log(e)
            for error_key, error_msg in daily.items():
                response[error_key] = error_msg
                log(f"==> {error_key} => {error_msg}")
    #
    #     return response
    #
    # def checkHistoryDaily(cur, mode, pdl, dateBegin, dateEnded):


    def get(self):

        lastYears = datetime.datetime.utcnow() - relativedelta(years=1)
        dateBegin = lastYears.strftime('%Y-%m-%d')

        dateEnded = datetime.datetime.utcnow()
        dateEnded = dateEnded.strftime('%Y-%m-%d')

        data = self.run(lastYears, dateEnded)
    #     lastData = {}
    #     data = dailyBeetwen(headers, cur, con, url, pdl, mode, dateBegin, dateEnded, last_activation_date)
    #     if "error_code" in data:
    #         f.publish(client, f"{pdl}/{mode}/current_year/error", str(1))
    #         for key, value in data.items():
    #             f.publish(client, f"{pdl}/{mode}/current_year/errorMsg/{key}", str(value))
    #     else:
    #         f.publish(client, f"{pdl}/{mode}/current_year/error", str(0))
    #         for key, value in data.items():
    #             if key != "dateBegin" and key != "dateEnded":
    #                 current_value = int(value["value"])
    #                 current_date = value["date"]
    #                 current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d')
    #                 day = current_date.strftime('%A')
    #                 f.publish(client, f"{pdl}/{mode}/current_year/{key}", str(current_value))
    #                 ha_discovery[pdl].update({
    #                     f"{mode}_{key.replace('-', '_')}": {
    #                         "value": round(int(current_value) / 1000, 2),
    #                         "unit_of_meas": "kWh",
    #                         "device_class": "energy",
    #                         "state_class": "total_increasing",
    #                         "attributes": {}
    #                     }
    #                 })
    #                 if not "kw" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                     ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["W"] = round(current_value)
    #                 if not "day" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                     ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["day"] = day.capitalize()
    #                 if not "date" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                     ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["date"] = value["date"]
    #                 today = datetime.datetime.utcnow()
    #                 today = today.strftime('%A')
    #                 if day == today:
    #                     today = True
    #                 else:
    #                     today = False
    #                 if not "today" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                     ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["today"] = today
    #             else:
    #                 f.publish(client, f"{pdl}/{mode}/current_year/{key}", str(value))
    #
    #             if "current_value" in locals():
    #                 if base_price != 0 and 'current_value' in locals():
    #                     if isinstance(current_value, int):
    #                         roundValue = round(int(current_value) / 1000 * base_price, 2)
    #                         f.publish(client, f"{pdl}/{mode}_price/current_year/{key}", roundValue)
    #                         if key != "dateBegin" and key != "dateEnded":
    #                             if not f"price" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"][
    #                                 'attributes'].keys():
    #                                 ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][f"price"] = str(
    #                                     roundValue)
    #             lastData = data
    #     current_year = 1
    #
    #     dateEnded = dateBegin
    #     dateEndedDelta = datetime.datetime.strptime(dateEnded, '%Y-%m-%d')
    #     dateBegin = dateEndedDelta + relativedelta(years=-1)
    #     dateBegin = dateBegin.strftime('%Y-%m-%d')
    #     while max_days_date <= datetime.datetime.strptime(dateEnded, '%Y-%m-%d'):
    #         f.log(f"Year => {dateEndedDelta.strftime('%Y')}")
    #         if last_activation_date > datetime.datetime.strptime(dateEnded, '%Y-%m-%d'):
    #             f.log(" - Skip (activation date > dateEnded)")
    #         else:
    #             data = dailyBeetwen(headers, cur, con, url, pdl, mode, dateBegin, dateEnded, last_activation_date)
    #             if "error_code" in data:
    #                 f.publish(client, f"{pdl}/{mode}/year-{current_year}/error", str(1))
    #                 for key, value in data.items():
    #                     f.publish(client, f"{pdl}/{mode}/year-{current_year}/errorMsg/{key}", str(value))
    #             else:
    #                 f.publish(client, f"{pdl}/{mode}/year-{current_year}/error", str(0))
    #                 for key, value in data.items():
    #                     if key != "dateBegin" and key != "dateEnded":
    #                         current_value = int(value["value"])
    #                         current_date = value["date"]
    #                         current_date = datetime.datetime.strptime(current_date, '%Y-%m-%d')
    #                         day = current_date.strftime('%A')
    #                         f.publish(client, f"{pdl}/{mode}/year-{current_year}/{key}", str(current_value))
    #                         if f"{mode}_{key.replace('-', '_')}" in ha_discovery[pdl]:
    #                             # CALC VARIATION
    #                             if key in lastData:
    #                                 if current_value != 0:
    #                                     variation = (lastData[key]["value"] - current_value) / current_value * 100
    #                                     variation = int(variation)
    #                                     if variation > 0:
    #                                         variation = f"+{variation}"
    #                                 else:
    #                                     variation = 999
    #                                 if current_year == 1:
    #                                     queue = "diff"
    #                                 else:
    #                                     queue = f"history_year_{current_year - 1}_diff"
    #                                 if not f"variation_year_{current_year}" in \
    #                                        ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                                     ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                         queue] = str(
    #                                         variation)
    #                             # SET HISTORY ATTRIBUTES
    #                             if not f"history_year_{current_year}" in \
    #                                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                                 ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                     f"history_year_{current_year}"] = str(current_value)
    #                             if not f"history_year_{current_year}_kw" in \
    #                                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                                 ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                     f"history_year_{current_year}_kw"] = round(int(current_value) / 1000, 2)
    #                             if not f"history_year_{current_year}_day" in \
    #                                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                                 ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                     f"history_year_{current_year}_day"] = day.capitalize()
    #                             if not f"history_year_{current_year}_date" in \
    #                                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
    #                                 ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                     f"history_year_{current_year}_date"] = value["date"]
    #
    #                         if "current_value" in locals():
    #                             if base_price != 0:
    #                                 if isinstance(current_value, int):
    #                                     roundValue = round(int(current_value) / 1000 * base_price, 2)
    #                                     f.publish(client, f"{pdl}/{mode}_price/year-{current_year}/{key}", roundValue)
    #                                     if not f"{mode}_{key.replace('-', '_')}" in ha_discovery[pdl].keys():
    #                                         ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"] = {
    #                                             "attributes": {}
    #                                         }
    #                                     if not f"price_year_{current_year}" in \
    #                                            ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"][
    #                                                'attributes'].keys():
    #                                         ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
    #                                             f"price_year_{current_year}"] = str(roundValue)
    #                     else:
    #                         f.publish(client, f"{pdl}/{mode}/year-{current_year}/{key}", str(value))
    #
    #         dateEnded = dateBegin
    #         dateEndedDelta = datetime.datetime.strptime(dateEnded, '%Y-%m-%d')
    #         dateBegin = dateEndedDelta + relativedelta(years=-1)
    #         if dateBegin < max_days_date:
    #             dateBegin = max_days_date
    #         dateBegin = dateBegin.strftime('%Y-%m-%d')
    #         current_year = current_year + 1
    #     return ha_discovery
    #
