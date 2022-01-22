import requests
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import *
from pprint import pprint
import re

from importlib import import_module

main = import_module("main")
f = import_module("function")

date_format = "%Y-%m-%d %H:%M:%S"


def getDetail(headers, cur, con, client, pdl, pdl_config, mode="consumption", last_activation_date=datetime.utcnow(), measure_total=None, offpeak_hours=[]):

    max_days = pdl_config['max_detail_days']
    max_days_per_demand = 7
    max_days_date = datetime.utcnow() + relativedelta(days=-max_days)
    price_base = pdl_config['consumption_price_base']
    price_hc = pdl_config['consumption_price_hc']
    price_hp = pdl_config['consumption_price_hp']

    url = main.url

    ha_discovery = {
        pdl: {}
    }

    # Check activation data
    last_activation_date = last_activation_date.split("+")[0]
    last_activation_date = datetime.strptime(last_activation_date, '%Y-%m-%d')

    lastYears = datetime.utcnow() + relativedelta(days=-max_days_per_demand)
    dateBegin = lastYears.strftime('%Y-%m-%d')
    dateEnded = datetime.utcnow()
    dateEnded = dateEnded.strftime('%Y-%m-%d')

    data = detailBeetwen(headers, cur, con, url, pdl, pdl_config, mode, dateBegin, dateEnded, last_activation_date, max_days_per_demand, offpeak_hours)
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
        finish = False
        no_data_found = 0
        while max_days_date <= datetime.strptime(dateEnded, '%Y-%m-%d') and not "error_code" in data and finish == False:
            f.log(f"Load {dateBegin} => {dateEnded}")
            if last_activation_date > datetime.strptime(dateEnded, '%Y-%m-%d'):
                f.log(" - Skip (activation date > dateEnded)")
                finish = True
            else:
                data = detailBeetwen(headers, cur, con, url, pdl, pdl_config, mode, dateBegin, dateEnded, last_activation_date,
                                     max_days_per_demand, offpeak_hours)

                if "error_code" in data:
                    if data["error_code"] == "no_data_found":
                        no_data_found += 1
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
    base_vs_offpeak = 0

    if query_result:

        for data in query_result:
            date = data[1]
            value = data[2]
            interval = data[3]
            measure_type = data[4]

            if value != 0:

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
                result[year][month]["measure_total"] += int(value)
                result[year][month]["measure_total_wh"] += int(value_wh)

                if measure_type == "HP":
                    result[year][month]["measure_hp"] += int(value)
                    result[year][month]["measure_hp_wh"] += int(value_wh)
                    result[year][month]["measure_ration_hp"] = round(
                        100 * result[year][month]["measure_hp"] / result[year][month]["measure_total"], 2)
                if measure_type == "HC":
                    result[year][month]["measure_hc"] += int(value)
                    result[year][month]["measure_hc_wh"] += int(value_wh)
                    result[year][month]["measure_ration_hc"] = round(
                        100 * result[year][month]["measure_hc"] / result[year][month]["measure_total"], 2)

                if price_base != 0:
                    result[year][month]["measure_base_euro"] = result[year][month]["measure_total_wh"] / 1000 * price_base

                if offpeak_hours != []:
                    if price_hc != 0 and price_hp != 0:
                        result[year][month]["measure_hp_euro"] = result[year][month]["measure_hp_wh"] / 1000 * price_hp
                        result[year][month]["measure_hc_euro"] = result[year][month]["measure_hc_wh"] / 1000 * price_hc
                        result[year][month]["measure_hphc_euro"] = result[year][month]["measure_hp_euro"] + result[year][month]["measure_hc_euro"]

                    if price_base != 0 and price_hc != 0 and price_hp != 0 and measure_type != "BASE":
                        result[year][month]["base_vs_offpeak"] = 100 - (
                                100 * result[year][month]["measure_base_euro"] / (result[year][month]["measure_hphc_euro"]))

                        base_vs_offpeak += result[year][month]["base_vs_offpeak"]

                        if result[year][month]["base_vs_offpeak"] > 0:
                            result[year][month]["best_plan"] = f"BASE"
                            result[year][month]["best_plan_percent"] = f"{abs(round(result[year][month]['base_vs_offpeak'], 2))}"
                        else:
                            result[year][month]["best_plan"] = f"HC/HP"
                            result[year][month]["best_plan_percent"] = f"{abs(round(result[year][month]['base_vs_offpeak'], 2))}"

        if offpeak_hours != [] and price_base != 0 and price_hc != 0 and price_hp != 0:
            if base_vs_offpeak > 0:
                best_plan = f"BASE"
                best_plan_percent = f"{abs(round(result[year][month]['base_vs_offpeak'], 2))}"
            else:
                best_plan = f"HC/HP"
                best_plan_percent = f"{abs(round(result[year][month]['base_vs_offpeak'], 2))}"

        year = dateObject.strftime('%Y')
        month = dateObject.strftime('%m')
        if offpeak_hours != [] and offpeak_hours != "":
            for plan in ["hc", "hp"]:
                ha_discovery[pdl].update({
                    f"{mode}_detail_this_month_{plan}": {
                        "value": result[year][month][f"measure_{plan}_wh"] / 1000,
                        "unit_of_meas": "kWh",
                        "device_class": "energy",
                        "state_class": "total_increasing",
                        "attributes": {}
                    }
                })
                if f"measure_ration_{plan}" in result[year][month]:
                    ha_discovery[pdl][f"{mode}_detail_this_month_{plan}"]["attributes"]["ratio"] = result[year][month][f"measure_ration_{plan}"]
                if f"measure_{plan}" in result[year][month]:
                    ha_discovery[pdl][f"{mode}_detail_this_month_{plan}"]["attributes"]["W"] = result[year][month][f"measure_{plan}"]

                if price_hc != 0 and price_hp != 0:
                    ha_discovery[pdl][f"{mode}_detail_this_month_{plan}"]["attributes"][f"measure_{plan}_euro"] = result[year][month][f"measure_{plan}_euro"]

        ha_discovery[pdl].update({
            f"{mode}_detail_this_month_base": {
                "value": result[year][month]["measure_total_wh"]/1000,
                "unit_of_meas": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "attributes": {}
            }
        })
        ha_discovery[pdl][f"{mode}_detail_this_month_base"]["attributes"]["W"] = result[year][month][f"measure_total"]
        if price_base != 0:
            ha_discovery[pdl][f"{mode}_detail_this_month_base"]["attributes"][f"measure_base_euro"] = result[year][month][f"measure_base_euro"]

        if offpeak_hours != []:
            if price_base != 0 and price_hc != 0 and price_hp != 0:
                ha_discovery[pdl].update({
                    f"{mode}_detail_this_month_compare": {
                        "value": result[year][month][f"best_plan"],
                        "attributes": {}
                    }
                })
                ha_discovery[pdl][f"{mode}_detail_this_month_compare"]["attributes"]["best_plan_percent"] = result[year][month][f"best_plan_percent"]
                ha_discovery[pdl].update({
                    f"{mode}_detail_this_year_compare": {
                        "value": best_plan,
                        "attributes": {}
                    }
                })
                ha_discovery[pdl][f"{mode}_detail_this_year_compare"]["attributes"]["best_plan_percent"] = best_plan_percent

        for year, value in result.items():
            for month, subvalue in value.items():
                for key, subsubvalue in subvalue.items():
                    f.publish(client, f"{pdl}/{mode}/detail/{year}/{month}/{key}", str(subsubvalue))

    return ha_discovery


def detailBeetwen(headers, cur, con, url, pdl, pdl_config, mode, dateBegin, dateEnded, last_activation_date, max_days_per_demand,
                  offpeak_hours=[]):

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
        current_data = checkHistoryDetail(cur, con, pdl, mode, dateBeginLong, dateEndedLong)
        if current_data['missing_data'] == False:
            f.log(f"Week allready in cache {dateBegin} / {dateEnded}")
            f.log(f" => Load data from cache")
        else:
            f.log(f"Data is missing between {dateBegin} / {dateEnded}")
            f.log(f" => Load data from API")

            detail = f.apiRequest(cur, con, pdl, type="POST", url=f"{url}", headers=headers, data=json.dumps(data))
            if not "error_code" in detail:
                meter_reading = detail['meter_reading']
                f.log("Import data :")
                new_date = []
                for interval_reading in meter_reading["interval_reading"]:
                    date = interval_reading['date']
                    interval_length = re.findall(r'\d+', interval_reading['interval_length'])[0]
                    value = int(interval_reading['value'])
                    dateObject = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                    dateHourMinute = dateObject.strftime('%H:%M')
                    if offpeak_hours != []:
                        measure_type = "HP"
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
                    else:
                        measure_type = "BASE"
                    new_date.append(date)
                    query = f"INSERT OR REPLACE INTO {mode}_detail VALUES ('{pdl}','{date}',{value},{interval_length},'{measure_type}', 0)"
                    cur.execute(query)
                con.commit()
                f.log(f"  => Import {len(new_date)} entry")

            elif detail['error_code'] == 2:
                f.log(f"Fetch data error detected beetween {dateBegin} / {dateEnded}", "ERROR")
                f.log(f" => {detail['description']}", "ERROR")
                # cur.execute(f"UPDATE {mode}_detail SET fail = {date_data['fail'] + 1} WHERE pdl = '{pdl}' and date = '{date}'")
            else:
                f.log(f"API return error beetween {dateBegin} / {dateEnded}", "ERROR")
                f.log(f" => {detail['description']}", "ERROR")
                response["error_code"] = detail['error_code']

        con.commit()
    except Exception as e:
        f.log(f"=====> ERROR : Exception - detailBeetwen <======")
        f.log(e)
        for error_key, error_msg in detail.items():
            response[error_key] = error_msg
            f.log(f"==> {error_key} => {error_msg}", "ERROR")
    return response


def checkHistoryDetail(cur, con, pdl, mode, dateBegin, dateEnded):
    # Run different query if there is data for 'today', to avoid needless runs/connections when checking history
    if datetime.utcnow().strftime('%Y-%m-%d') == dateEnded.strftime('%Y-%m-%d'):
        #result = {
        #    "missing_data": True
        #}
        f.log(f"Run today with dateEnded: {dateEnded}")
        query = f"SELECT * FROM {mode}_detail WHERE pdl = '{pdl}' AND date = '{dateEnded}'"    
    else:
        query = f"SELECT * FROM {mode}_detail WHERE pdl = '{pdl}' AND date BETWEEN '{dateBegin}' AND '{dateEnded}' ORDER BY date"
    
    cur.execute(query)
    query_result = cur.fetchall()
    f.log(f"Q: {query}", "DEBUG")
    # if len(query_result) < 160:
    if not query_result:
        result = {
            "missing_data": True
        }
    else:
        result = {
            "missing_data": False
        }
    return result
