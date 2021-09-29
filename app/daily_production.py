import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *

from importlib import import_module
main = import_module("main")
f = import_module("function")

def dailyProduction(cur, client, last_activation_date):
    my_date = datetime.now()
    pdl = main.pdl
    production_base = main.production_base

    ha_discovery = {
        pdl: {}
    }

    # Check activation data
    last_activation_date = last_activation_date.split("+")[0]
    last_activation_date = datetime.strptime(last_activation_date, '%Y-%m-%d')

    lastYears = datetime.now() + relativedelta(years=-1)
    dateBegin = lastYears.strftime('%Y-%m-%d')
    dateEnded = my_date.strftime('%Y-%m-%d')

    data = dailyProductionBeetwen(cur, pdl, dateBegin, dateEnded, last_activation_date)
    for key, value in data.items():
        f.publish(client, f"{pdl}/production/current_year/{key}", str(value))
        if key != "dateBegin" and key != "dateEnded":
            ha_discovery[pdl].update({
                f"production_{key.replace('-','_')}": {
                    "value": str(value),
                    "unit_of_meas": "W",
                    "device_class": "energy",
                    "state_class": "total_increasing",
                    "attributes": {}
                }
            })
        if production_base != 0:
            if isinstance(value, int):
                roundValue = round(int(value) / 1000 * production_base, 2)
                f.publish(client, f"{pdl}/production_price/current_year/{key}", roundValue)
                if key != "dateBegin" and key != "dateEnded":
                    if not f"price" in ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'].keys():
                        ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'][f"price"] = str(roundValue)
        lastData = data

    current_year = 1
    while current_year <= main.years:
        if main.years >= current_year:
            f.log(f"Year => {current_year}")
            dateEnded = dateBegin
            dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
            # dateEnded = dateEndedDelta + relativedelta(days=-1)
            # dateEnded = dateEnded.strftime('%Y-%m-%d')
            dateBegin = dateEndedDelta + relativedelta(years=-1)
            dateBegin = dateBegin.strftime('%Y-%m-%d')
            data = dailyProductionBeetwen(cur, pdl, dateBegin, dateEnded, last_activation_date)
            if "error_code" in data:
                f.publish(client, f"{pdl}/production/year-{current_year}/error", str(1))
                for key, value in data.items():
                    f.publish(client, f"{pdl}/production/year-{current_year}/errorMsg/{key}", str(value))
            else:
                f.publish(client, f"{pdl}/production/year-{current_year}/error", str(0))
                for key, value in data.items():
                    f.publish(client, f"{pdl}/production/year-{current_year}/{key}", str(value))
                    if key != "dateBegin" and key != "dateEnded":
                        if f"production_{key.replace('-', '_')}" in ha_discovery[pdl]:
                            # CALC VARIATION
                            if key in lastData:
                                variation = (lastData[key] - value) / value * 100
                                if not f"variation_year_{current_year}" in ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'].keys():
                                    ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'][f"variation_year_{current_year}"] = str(round(variation, 2))
                            # SET HISTORY ATTRIBUTES
                            if not f"history_year_{current_year}" in ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'][f"history_year_{current_year}"] = str(value)
                    if production_base != 0:
                        if isinstance(value, int):
                            roundValue = round(int(value) / 1000 * production_base, 2)
                            f.publish(client, f"{pdl}/production_price/year-{current_year}/{key}", roundValue)
                            # if f"price_production_{key.replace('-', '_')}" in ha_discovery[pdl]:
                            if not f"price_year_{current_year}" in ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'].keys():
                                ha_discovery[pdl][f"production_{key.replace('-', '_')}"]['attributes'][f"price_year_{current_year}"] = str(roundValue)
            current_year = current_year + 1
    return ha_discovery

def checkHistoryProductionDaily(cur, dateBegin, dateEnded):
    pdl = main.pdl
    dateBegin = datetime.strptime(dateBegin, '%Y-%m-%d')
    dateEnded = datetime.strptime(dateEnded, '%Y-%m-%d')
    delta = dateEnded - dateBegin
    result = {
        "status": True,
        "date": [],
        "count": 0
    }
    for i in range(delta.days + 1):
        checkDate = dateBegin + timedelta(days=i)
        checkDate = checkDate.strftime('%Y-%m-%d')
        query = f"SELECT * FROM production_daily WHERE pdl = '{main.pdl}' AND date = '{checkDate}'"
        cur.execute(query)
        if cur.fetchone() is None:
            main.api_no_result.append(checkDate)
            result["date"].append(checkDate)
            result["status"] = False
            result["count"] = result["count"] + 1
    return result

def dailyProductionBeetwen(cur, pdl, dateBegin, dateEnded, last_activation_date):
    response = {}

    lastYears = datetime.strptime(dateEnded, '%Y-%m-%d')
    lastYears = lastYears + relativedelta(years=-1)
    if lastYears < last_activation_date:
        dateBegin = last_activation_date
        dateBegin = dateBegin.strftime('%Y-%m-%d')

    response['dateBegin'] = dateBegin
    response['dateEnded'] = dateEnded

    data = {
        "type": "daily_production",
        "usage_point_id": str(pdl),
        "start": str(dateBegin),
        "end": str(dateEnded),
    }

    try:
        new_date = []
        current_data = checkHistoryProductionDaily(cur, dateBegin, dateEnded)
        if current_data['status'] == True:
            f.log(f"All data loading beetween {dateBegin} / {dateEnded}")
            f.log(f" => Skip API Call")
        else:
            f.log(f"Data is missing between {dateBegin} / {dateEnded}")

            daily_production = requests.request("POST", url=f"{main.url}", headers=main.headers, data=json.dumps(data)).json()
            meter_reading = daily_production['meter_reading']
            mesures = {}
            f.log("Import data :")
            log_import = []
            for interval_reading in meter_reading["interval_reading"]:
                date = interval_reading['date']
                value = interval_reading['value']
                cur.execute(f"INSERT OR REPLACE INTO production_daily VALUES ('{pdl}','{interval_reading['date']}','{interval_reading['value']}')")
                new_date.append(interval_reading['date'])
                mesures[date] = value
            list_date = list(reversed(sorted(mesures.keys())))

            f.splitLog(new_date)

            not_found_data = []
            for current_date in current_data['date']:
                if not current_date in new_date:
                    not_found_data.append(current_date)

            if not_found_data != []:
                f.log("Data not found :")
                f.splitLog(not_found_data)

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

                # WEEK DAYS
                if current_date == j1:
                    response['j-1'] = value
                if current_date == j2:
                    response['j-2'] = value
                if current_date == j3:
                    response['j-3'] = value
                if current_date == j4:
                    response['j-4'] = value
                if current_date == j5:
                    response['j-5'] = value
                if current_date == j6:
                    response['j-6'] = value
                if current_date == j7:
                    response['j-7'] = value
                # LAST WEEK
                if current_date >= dateWeek:
                    energyWeek = int(energyWeek) + int(value)
                # LAST MONTH
                if current_date >= dateMonths:
                    energyMonths = int(energyMonths) + int(value)
                # LAST YEARS
                if current_date >= dateYears:
                    energyYears = int(energyYears) + int(value)

            response['thisWeek'] = energyWeek
            response['thisMonth'] = energyMonths
            response['thisYear'] = energyYears
    except:
        for error_key, error_msg in daily_production.items():
            response[error_key] = error_msg

    return response