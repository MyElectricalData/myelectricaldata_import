import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from pprint import pprint
import locale
import pytz

from importlib import import_module
main = import_module("main")
f = import_module("function")

# locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
# timezone = pytz.timezone('Europe/Paris')


def getDaily(headers, cur, con, client, pdl, pdl_config, mode="consumption", last_activation_date=datetime.utcnow()):
    max_days = pdl_config['max_daily_days']
    max_days_date = datetime.utcnow() + relativedelta(days=-max_days)
    base_price = pdl_config['consumption_price_base']

    url = main.url

    ha_discovery = {
        pdl: {}
    }

    # Check activation data
    last_activation_date = last_activation_date.split("+")[0]
    last_activation_date = datetime.strptime(last_activation_date, '%Y-%m-%d')

    lastYears = datetime.utcnow() - relativedelta(years=1)
    dateBegin = lastYears.strftime('%Y-%m-%d')
    dateEnded = datetime.now() - relativedelta(days=0)
    dateEnded = dateEnded.strftime('%Y-%m-%d') 
    f.log(f"Checking last year with max_days_date: {max_days_date} / dateBegin: {datetime.strptime(dateBegin, '%Y-%m-%d')} / dateEnded: {datetime.strptime(dateEnded, '%Y-%m-%d')}")
    lastData = {}
    data = dailyBeetwen(headers, cur, con, url, pdl, mode, dateBegin, dateEnded, last_activation_date)
    if "error_code" in data:
        f.publish(client, f"{pdl}/{mode}/current_year/error", str(1))
        for key, value in data.items():
            f.publish(client, f"{pdl}/{mode}/current_year/errorMsg/{key}", str(value))
    else:
        f.publish(client, f"{pdl}/{mode}/current_year/error", str(0))
        for key, value in data.items():
            if key != "dateBegin" and key != "dateEnded":
                current_value = int(value["value"])
                current_date = value["date"]
                current_date = datetime.strptime(current_date, '%Y-%m-%d')
                day = current_date.strftime('%A')
                f.publish(client, f"{pdl}/{mode}/current_year/{key}", str(current_value))
                ha_discovery[pdl].update({
                    f"{mode}_{key.replace('-', '_')}": {
                        "value": round(int(current_value) / 1000, 2),
                        "unit_of_meas": "kWh",
                        "device_class": "energy",
                        "state_class": "total_increasing",
                        "attributes": {}
                    }
                })
                if not "kw" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["W"] = round(current_value)
                if not "day" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["day"] = day.capitalize()
                if not "date" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["date"] = value["date"]
                today = datetime.utcnow()
                today = today.strftime('%A')
                if day == today:
                    today = True
                else:
                    today = False
                if not "today" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes']["today"] = today
            else:
                f.publish(client, f"{pdl}/{mode}/current_year/{key}", str(value))

            if "current_value" in locals():
                if base_price != 0 and 'current_value' in locals():
                    if isinstance(current_value, int):
                        roundValue = round(int(current_value) / 1000 * base_price, 2)
                        f.publish(client, f"{pdl}/{mode}_price/current_year/{key}", roundValue)
                        if key != "dateBegin" and key != "dateEnded":
                            if not f"price" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][f"price"] = str(
                                    roundValue)
            lastData = data
    current_year = 1

    dateEnded = dateBegin
    dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
    dateBegin = dateEndedDelta + relativedelta(years=-1)
    if dateBegin < max_days_date:
            dateBegin = max_days_date
            f.log(f"dateBegin=max_days_date = : {dateBegin}")
    dateBegin = dateBegin.strftime('%Y-%m-%d')
    f.log(f"Checking older years with max_days_date: {max_days_date} / dateBegin: {datetime.strptime(dateBegin, '%Y-%m-%d')} / dateEnded: {datetime.strptime(dateEnded, '%Y-%m-%d')}")
    while max_days_date <= datetime.strptime(dateEnded, '%Y-%m-%d'):
        f.log(f"Year => {dateEndedDelta.strftime('%Y')}")
        if last_activation_date > datetime.strptime(dateEnded, '%Y-%m-%d'):
            f.log(" - Skip (activation date > dateEnded)")
        else:
            data = dailyBeetwen(headers, cur, con, url, pdl, mode, dateBegin, dateEnded, last_activation_date)
            if "error_code" in data:
                f.publish(client, f"{pdl}/{mode}/year-{current_year}/error", str(1))
                for key, value in data.items():
                    f.publish(client, f"{pdl}/{mode}/year-{current_year}/errorMsg/{key}", str(value))
            else:
                f.publish(client, f"{pdl}/{mode}/year-{current_year}/error", str(0))
                for key, value in data.items():
                    if key != "dateBegin" and key != "dateEnded":
                        current_value = int(value["value"])
                        current_date = value["date"]
                        current_date = datetime.strptime(current_date, '%Y-%m-%d')
                        day = current_date.strftime('%A')
                        f.publish(client, f"{pdl}/{mode}/year-{current_year}/{key}", str(current_value))
                        if f"{mode}_{key.replace('-', '_')}" in ha_discovery[pdl]:
                            # CALC VARIATION
                            if key in lastData:
                                if current_value != 0:
                                    variation = (lastData[key]["value"] - current_value) / current_value * 100
                                    variation = int(variation)
                                    if variation > 0:
                                        variation = f"+{variation}"
                                else:
                                    variation = 999
                                if current_year == 1:
                                    queue = "diff"
                                else:
                                    queue = f"history_year_{current_year - 1}_diff"
                                if not f"variation_year_{current_year}" in \
                                       ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                    ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][queue] = str(
                                        variation)
                            # SET HISTORY ATTRIBUTES
                            if not f"history_year_{current_year}" in \
                                   ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
                                    f"history_year_{current_year}"] = str(current_value)
                            if not f"history_year_{current_year}_kw" in \
                                   ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
                                    f"history_year_{current_year}_kw"] = round(int(current_value) / 1000, 2)
                            if not f"history_year_{current_year}_day" in \
                                   ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
                                    f"history_year_{current_year}_day"] = day.capitalize()
                            if not f"history_year_{current_year}_date" in \
                                   ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
                                    f"history_year_{current_year}_date"] = value["date"]

                        if "current_value" in locals():
                            if base_price != 0:
                                if isinstance(current_value, int):
                                    roundValue = round(int(current_value) / 1000 * base_price, 2)
                                    f.publish(client, f"{pdl}/{mode}_price/year-{current_year}/{key}", roundValue)
                                    if not f"{mode}_{key.replace('-', '_')}" in ha_discovery[pdl].keys():
                                        ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"] = {
                                            "attributes": {}
                                        }
                                    if not f"price_year_{current_year}" in ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'].keys():
                                        ha_discovery[pdl][f"{mode}_{key.replace('-', '_')}"]['attributes'][
                                            f"price_year_{current_year}"] = str(roundValue)
                    else:
                        f.publish(client, f"{pdl}/{mode}/year-{current_year}/{key}", str(value))

        dateEnded = dateBegin
        dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
        dateBegin = dateEndedDelta + relativedelta(years=-1)
        if dateBegin < max_days_date:
            dateBegin = max_days_date
        dateBegin = dateBegin.strftime('%Y-%m-%d')
        current_year = current_year + 1
    return ha_discovery


def dailyBeetwen(headers, cur, con, url, pdl, mode, dateBegin, dateEnded, last_activation_date):
    response = {}

    lastYears = datetime.strptime(dateEnded, '%Y-%m-%d')
    lastYears = lastYears + relativedelta(years=-1)
    if lastYears < last_activation_date:
        dateBegin = last_activation_date
        dateBegin = dateBegin.strftime('%Y-%m-%d')

    response['dateBegin'] = dateBegin
    response['dateEnded'] = dateEnded

    data = {
        "type": f"daily_{mode}",
        "usage_point_id": str(pdl),
        "start": str(dateBegin),
        "end": str(dateEnded),
    }

    try:
        new_date = []
        current_data = checkHistoryDaily(cur, mode, pdl, dateBegin, dateEnded)
        mesures = {}
        if current_data['missing_data'] == False:
            f.log(f"All data loading beetween {dateBegin} / {dateEnded}")
            f.log(f" => Load data from cache")
            for date, data in current_data['date'].items():
                mesures[date] = data['value']
        else:
            f.log(f"Data is missing between {dateBegin} / {dateEnded}")
            f.log(f" => Load data from API")
            daily = f.apiRequest(cur, con, pdl, type="POST", url=f"{url}", headers=headers, data=json.dumps(data))
            if not "error_code" in daily:
                meter_reading = daily['meter_reading']
                f.log("Import data :")
                for interval_reading in meter_reading["interval_reading"]:
                    date = interval_reading['date']
                    value = interval_reading['value']
                    cur.execute(
                        f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{interval_reading['date']}','{interval_reading['value']}','0')")
                    new_date.append(interval_reading['date'])
                    mesures[date] = value
                f.splitLog(new_date)

                not_found_data = []
                for date, date_data in current_data['date'].items():
                    if not date in new_date:
                        not_found_data.append(date)
                        current_date = datetime.strptime(date, '%Y-%m-%d').date()
                        current_day = datetime.today().date()
                        if date_data['fail'] == 0 and date_data['value'] == 0:
                            if current_day == current_date:
                                fail = 0
                            else:
                                fail = 1
                            cur.execute(f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{date}','0','{fail}')")
                            # cur.execute(f"INSERT OR REPLACE INTO {mode}_daily VALUES ('{pdl}','{date}','0','1')")
                        else:
                            if current_day != current_date:
                                fail = 0
                            else:
                                fail = date_data['fail']
                            cur.execute(f"UPDATE {mode}_daily SET fail = {fail + 1} WHERE pdl = '{pdl}' and date = '{date}'")
                            # cur.execute(f"UPDATE {mode}_daily SET fail = {date_data['fail'] + 1} WHERE pdl = '{pdl}' and date = '{date}'")


                if not_found_data != []:
                    f.log("Data not found :")
                    f.splitLog(not_found_data)

            elif daily['error_code'] == 2:
                f.log(f"Fetch data error detected beetween {dateBegin} / {dateEnded}")
                f.log(f" => Load data from cache")
                for date, data in current_data['date'].items():
                    mesures[date] = data['value']

        list_date = list(reversed(sorted(mesures.keys())))

        dateEnded = datetime.strptime(dateEnded, '%Y-%m-%d')
        dateWeek = dateEnded + relativedelta(days=-7)
        dateMonths = dateEnded + relativedelta(months=-1)
        dateYears = dateEnded + relativedelta(years=-1)
        j1 = dateEnded + relativedelta(days=-1)
        j1 = j1.replace(hour=0, minute=0, second=0, microsecond=0)
        j2 = dateEnded + relativedelta(days=-2)
        j2 = j2.replace(hour=0, minute=0, second=0, microsecond=0)
        j3 = dateEnded + relativedelta(days=-3)
        j3 = j3.replace(hour=0, minute=0, second=0, microsecond=0)
        j4 = dateEnded + relativedelta(days=-4)
        j4 = j4.replace(hour=0, minute=0, second=0, microsecond=0)
        j5 = dateEnded + relativedelta(days=-5)
        j5 = j5.replace(hour=0, minute=0, second=0, microsecond=0)
        j6 = dateEnded + relativedelta(days=-6)
        j6 = j6.replace(hour=0, minute=0, second=0, microsecond=0)
        j7 = dateEnded + relativedelta(days=-7)
        j7 = j7.replace(hour=0, minute=0, second=0)

        energyWeek = 0
        energyMonths = 0
        energyYears = 0

        for date in list_date:
            value = int(mesures[date])
            current_date = datetime.strptime(date, '%Y-%m-%d')
            day = current_date.strftime('%A')

            # WEEK DAYS
            if current_date == j1:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j2:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j3:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j4:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j5:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j6:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            if current_date == j7:
                response[f"{day}"] = {
                    "value": value,
                    "date": date
                }
            # LAST WEEK
            if current_date >= dateWeek:
                energyWeek = int(energyWeek) + int(value)
            # LAST MONTH
            if current_date >= dateMonths:
                energyMonths = int(energyMonths) + int(value)
            # LAST YEARS
            if current_date >= dateYears:
                energyYears = int(energyYears) + int(value)

        response['this_week'] = {
            "value": energyWeek,
            "date": date
        }
        response['this_month'] = {
            "value": energyMonths,
            "date": date
        }
        response['this_year'] = {
            "value": energyYears,
            "date": date
        }
    except Exception as e:
        f.log("=====> ERROR : Exception <======")
        f.log(e)
        for error_key, error_msg in daily.items():
            response[error_key] = error_msg
            f.log(f"==> {error_key} => {error_msg}")

    return response


def checkHistoryDaily(cur, mode, pdl, dateBegin, dateEnded):
    dateToday = datetime.utcnow()
    dateToday = dateToday.strftime('%Y-%m-%d')
    dateBegin = datetime.strptime(dateBegin, '%Y-%m-%d')
    dateEnded = datetime.strptime(dateEnded, '%Y-%m-%d')
    delta = dateEnded - dateBegin
    result = {
        "missing_data": False,
        "date": {},
        "count": 0
    }
    for i in range(delta.days + 1):
        checkDate = dateBegin + timedelta(days=i)
        checkDate = checkDate.strftime('%Y-%m-%d')
        # f.log(f"Not including check vs. today: {checkDate} vs {dateToday}")
        if checkDate == dateToday :
            f.log(f"Not today: return")
            return result
        query = f"SELECT * FROM {mode}_daily WHERE pdl = '{pdl}' AND date = '{checkDate}'"
        cur.execute(query)
        query_result = cur.fetchone()
        if query_result is None:
            result["date"][checkDate] = {
                "status": False,
                "fail": 0,
                "value": 0
            }
            result["missing_data"] = True
            result["count"] = result["count"] + 1
        elif query_result[3] >= main.fail_count:
            result["date"][checkDate] = {
                "status": True,
                "fail": query_result[3],
                "value": query_result[2]
            }
        elif query_result[2] == 0:
            result["date"][checkDate] = {
                "status": False,
                "fail": query_result[3],
                "value": query_result[2]
            }
            result["missing_data"] = True
            result["count"] = result["count"] + 1
        else:
            result["date"][checkDate] = {
                "status": True,
                "fail": 0,
                "value": query_result[2]
            }
    return result
