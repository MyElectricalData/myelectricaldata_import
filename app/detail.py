import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from pprint import pprint
import re
from scipy import integrate

from importlib import import_module

main = import_module("main")
f = import_module("function")

date_format = "%Y-%m-%d %H:%M:%S"


def getDetail(cur, con, client, mode="consumption", last_activation_date=datetime.now(), offpeak_hours=None,
              measure_total=None):
    max_days = 730
    max_days_per_demand = 7
    max_days_date = datetime.now() + relativedelta(days=-max_days)
    pdl = main.pdl
    price_base = main.consumption_price_base
    price_hc = main.consumption_price_hc
    price_hp = main.consumption_price_hp

    ha_discovery = {
        pdl: {}
    }

    # Check activation data
    last_activation_date = last_activation_date.split("+")[0]
    last_activation_date = datetime.strptime(last_activation_date, '%Y-%m-%d')

    lastYears = datetime.now() + relativedelta(days=-max_days_per_demand)
    dateBegin = lastYears.strftime('%Y-%m-%d')
    dateEnded = datetime.now()
    dateEnded = dateEnded.strftime('%Y-%m-%d')

    data = detailBeetwen(cur, con, pdl, mode, dateBegin, dateEnded, last_activation_date, max_days_per_demand,
                         offpeak_hours)
    if "error_code" in data:
        f.publish(client, f"{pdl}/{mode}/detail/error", str(1))
        for key, value in data.items():
            f.publish(client, f"{pdl}/{mode}/detail/errorMsg/{key}", str(value))
    else:
        dateEnded = dateBegin
        dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
        dateBegin = dateEndedDelta + relativedelta(weeks=-1)
        dateBegin = dateBegin.strftime('%Y-%m-%d')
        current_week = 1
        while max_days_date <= datetime.strptime(dateEnded, '%Y-%m-%d') and not "error_code" in data:
            f.log(f"Load {dateBegin} => {dateEnded}")
            if last_activation_date > datetime.strptime(dateEnded, '%Y-%m-%d'):
                f.log(" - Skip (activation date > dateEnded)")
            else:
                data = detailBeetwen(cur, con, pdl, mode, dateBegin, dateEnded, last_activation_date,
                                     max_days_per_demand, offpeak_hours)
                if "error_code" in data:
                    f.publish(client, f"{pdl}/{mode}/detail/error", str(1))
                    for key, value in data.items():
                        f.publish(client, f"{pdl}/{mode}/detail/errorMsg/{key}", str(value))
                else:
                    dateEnded = dateBegin
                    dateEndedDelta = datetime.strptime(dateEnded, '%Y-%m-%d')
                    dateBegin = dateEndedDelta + relativedelta(weeks=-1)
                    if dateBegin < max_days_date:
                        dateBegin = max_days_date
                    dateBegin = dateBegin.strftime('%Y-%m-%d')
                    current_week = current_week + 1

    query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' ORDER BY date;"
    cur.execute(query)
    query_result = cur.fetchall()

    result = {}
    # result = {
    #     "measure_hp": 0,
    #     "measure_hp_wh": 0,
    #     "measure_hc": 0,
    #     "measure_hc_wh": 0,
    #     "measure_total": 0,
    #     "measure_total_wh": 0
    # }

    for data in query_result:
        date = data[1]
        value = data[2]
        interval = data[3]
        measure_type = data[4]

        dateObject = datetime.strptime(date, date_format)
        year = dateObject.strftime('%Y')
        month = dateObject.strftime('%m')

        if not year in result:
            result[year] =  {}
        if not month in result[year]:
            result[year].update({
                month: {
                    "measure_hp": 0,
                    "measure_hp_wh": 0,
                    "measure_hc": 0,
                    "measure_hc_wh": 0,
                    "measure_total": 0,
                    "measure_total_wh": 0
                }
            })

        value_wh = value * (interval / 60)
        if measure_type == "HP":
            result[year][month]["measure_hp"] += int(value)
            result[year][month]["measure_total"] += int(value)
            result[year][month]["measure_hp_wh"] += int(value_wh)
            result[year][month]["measure_total_wh"] += int(value_wh)
        if measure_type == "HC":
            result[year][month]["measure_hc"] += int(value)
            result[year][month]["measure_total"] += int(value)
            result[year][month]["measure_hc_wh"] += int(value_wh)
            result[year][month]["measure_total_wh"] += int(value_wh)

        result[year][month]["mesure_ration_hp"] = round(100 * result[year][month]["measure_hp"] / result[year][month]["measure_total"], 2)
        result[year][month]["mesure_ration_hc"] = round(100 * result[year][month]["measure_hc"] / result[year][month]["measure_total"], 2)

        result[year][month]["measure_hp_euro"] = result[year][month]["measure_hp_wh"] / 1000 * price_hp
        result[year][month]["measure_hc_euro"] = result[year][month]["measure_hc_wh"] / 1000 * price_hc
        result[year][month]["measure_hphc_euro"] = result[year][month]["measure_hp_euro"] + result[year][month]["measure_hc_euro"]
        result[year][month]["measure_base_euro"] = result[year][month]["measure_total_wh"] / 1000 * price_base


        result[year][month]["base_vs_offpeak"] = 100 - (
                    100 * result[year][month]["measure_base_euro"] / (result[year][month]["measure_hphc_euro"]))
        if result[year][month]["base_vs_offpeak"] > 0:
            result[year][month]["best_plan"] = f"BASE"
            result[year][month]["best_plan_percent"] = f"{round(result[year][month]['base_vs_offpeak'], 2)}"
        else:
            result[year][month]["best_plan"] = f"HC/HP"
            result[year][month]["best_plan_percent"] = f"{round(result[year][month]['base_vs_offpeak'], 2)}"

    f.logLine()
    for year, value in result.items():
        for month, subvalue in value.items():
            for key, subsubvalue in subvalue.items():
                f.publish(client, f"{pdl}/{mode}/detail/{year}/{month}/{key}", str(subsubvalue))

    return ha_discovery


def detailBeetwen(cur, con, pdl, mode, dateBegin, dateEnded, last_activation_date, max_days_per_demand, offpeak_hours):
    response = {}

    def is_between(time, time_range):
        if time_range[1] < time_range[0]:
            return time >= time_range[0] or time <= time_range[1]
        return time_range[0] <= time <= time_range[1]

    lastYears = datetime.strptime(dateEnded, '%Y-%m-%d')
    lastYears = lastYears + relativedelta(days=-max_days_per_demand)
    if lastYears < last_activation_date:
        dateBegin = last_activation_date
        dateBegin = dateBegin.strftime('%Y-%m-%d')

    response['dateBegin'] = dateBegin
    response['dateEnded'] = dateEnded

    data = {
        "type": f"{mode}_load_curve",
        "usage_point_id": str(pdl),
        "start": str(dateBegin),
        "end": str(dateEnded),
    }

    try:
        new_date = []
        dateBeginLong = datetime.strptime(dateBegin, '%Y-%m-%d')
        dateEndedLong = datetime.strptime(dateEnded, '%Y-%m-%d')
        current_data = checkHistoryDetail(cur, con, mode, dateBeginLong, dateEndedLong)
        if current_data['missing_data'] == False:
            f.log(f"Week allready in cache {dateBegin} / {dateEnded}")
            f.log(f" => Load data from cache")
        else:
            f.log(f"Data is missing between {dateBegin} / {dateEnded}")
            f.log(f" => Load data from API")

            detail = f.apiRequest(cur, con, type="POST", url=f"{main.url}", headers=main.headers, data=json.dumps(data))
            meter_reading = detail['meter_reading']
            f.log("Import data :")
            new_date = []
            for interval_reading in meter_reading["interval_reading"]:
                date = interval_reading['date']
                interval_length = re.findall(r'\d+', interval_reading['interval_length'])[0]
                value = int(interval_reading['value'])
                measure_type = "HP"
                dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                dateHourMinute = dateObject.strftime('%H:%M')
                for offpeak_hour in offpeak_hours:
                    offpeak_begin = offpeak_hour.split("-")[0].replace('h', ':').replace('H', ':')
                    # FORMAT HOUR WITH 2 DIGIT
                    offpeak_begin = datetime.strptime(offpeak_begin, '%H:%M')
                    offpeak_begin = datetime.strftime(offpeak_begin, '%H:%M')
                    offpeak_stop = offpeak_hour.split("-")[1].replace('h', ':').replace('H', ':')
                    # FORMAT HOUR WITH 2 DIGIT
                    offpeak_stop = datetime.strptime(offpeak_stop, '%H:%M')
                    offpeak_stop = datetime.strftime(offpeak_stop, '%H:%M')
                    result = is_between(dateHourMinute, (offpeak_begin, offpeak_stop))
                    if result == True:
                        measure_type = "HC"
                    new_date.append(date)
                query = f"INSERT OR REPLACE INTO {mode}_detail VALUES ('{pdl}','{date}',{value},{interval_length},'{measure_type}', 0)"
                cur.execute(query)
            con.commit()
            f.log(f"  => Import {len(new_date)} entry")
        con.commit()
    except Exception as e:
        f.log(f"=====> ERROR : Exception - detailBeetwen <======")
        f.log(e)
        for error_key, error_msg in detail.items():
            response[error_key] = error_msg
            f.log(f"==> {error_key} => {error_msg}")
    return response


def checkHistoryDetail(cur, con, mode, dateBegin, dateEnded):
    pdl = main.pdl

    # FORCE THIS WEEK
    if datetime.now().strftime('%Y-%m-%d') == dateEnded.strftime('%Y-%m-%d'):
        result = {
            "missing_data": True
        }
    else:
        # CHECK CURRENT DATA
        query = f"SELECT * FROM {mode}_detail WHERE pdl = '{pdl}' AND date BETWEEN '{dateBegin}' AND '{dateEnded}' ORDER BY date"
        cur.execute(query)
        query_result = cur.fetchall()
        if len(query_result) < 160:
            result = {
                "missing_data": True
            }
        else:
            result = {
                "missing_data": False
            }
    return result
