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

locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
timezone = pytz.timezone('Europe/Paris')

def myEnedis(cur, con, client, pdl, pdl_config, last_activation_date=datetime.now(pytz.timezone('Europe/Paris')), offpeak_hours=None):
    def forceRound(x, n):
        import decimal
        d = decimal.Decimal(repr(x))
        targetdigit = decimal.Decimal("1e%d" % -n)
        chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
        return float(chopped)

    price = {
        "BASE": pdl_config['consumption_price_base'],
        "HC": pdl_config['consumption_price_hc'],
        "HP": pdl_config['consumption_price_hp']
    }

    ha_autodiscovery_prefix= main.config['home_assistant']['discovery_prefix']

    ha_discovery = {
        pdl: {}
    }

    path = f"enedisgateway/{pdl}"
    config = {
        "name": f"enedisgateway_{pdl}",
        "uniq_id": f"enedisgateway.{pdl}",
        "stat_t": f"{ha_autodiscovery_prefix}/sensor/{path}/state",
        "json_attr_t": f"{ha_autodiscovery_prefix}/sensor/{path}/attributes",
        "unit_of_measurement": "kWh",
        "device": {
            "identifiers": [ f"linky_{pdl}" ],
            "name": f"Linky {pdl}",
            "model": "Linky",
            "manufacturer": "Enedis"
        },
    }

    f.publish(client, f"sensor/{path}/config", json.dumps(config), ha_autodiscovery_prefix)

    today = datetime.now(timezone)
    attributes = {
        "numPDL": pdl,
        "activationDate": last_activation_date.split("+")[0],
        "lastUpdate": today.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "timeLastCall": today.strftime('%Y-%m-%dT%H:%M:%SZ'),
    }

    today = datetime.now(timezone)
    found = False
    delta = 0
    deltaMax = 7
    notFound = False
    while found == False and notFound == False:
        yesterday_datetime = today - relativedelta(days=1+delta)
        yesterday = yesterday_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date='{yesterday}';"
        cur.execute(query)
        query_result = cur.fetchone()
        attributes['yesterdayDate'] = yesterday
        if query_result != None:
            attributes['yesterday'] = query_result[2] / 1000
            found = True
        else:
            attributes['yesterday'] = -1
            delta += 1
            if delta >= deltaMax:
                notFound = True

    if notFound == True:
        f.log(" => No data found (skip HA MyEnedis Sensor)")
    else:
        state = attributes['yesterday']

        today = datetime.now(timezone)
        yesterday_last_year_datetime = today - relativedelta(years=1, days=1+delta)
        yesterday_last_year = yesterday_last_year_datetime.strftime('%Y-%m-%d')
        attributes["yesterdayLastYearDate"] = yesterday_last_year
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date='{yesterday_last_year}';"
        cur.execute(query)
        query_result = cur.fetchone()
        if query_result != None:
            attributes['yesterdayLastYear'] = query_result[2] / 1000
        else:
            attributes['yesterdayLastYear'] = -1
        yesterdayLastYear = attributes['yesterdayLastYear']

        # CURRENT WEEK
        today = datetime.now(timezone)
        last_week_datetime = today - relativedelta(days=7+delta)
        last_week = last_week_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_week}' AND '{yesterday}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['last_week'] = 0
        attributes['daily'] = []
        attributes['current_week'] = 0
        id = 1
        nbDayWeek = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            currentWeekNumber = today.strftime("%V")
            weekNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%V')
            attributes['last_week'] += value
            if weekNumber == currentWeekNumber:
                attributes['current_week'] += value / 1000
                nbDayWeek += 1
            if id <= delta:
                attributes['daily'].append(0)
                # attributes['daily'].append(str(forceRound(value / 1000, 2)))
                attributes[f'day_{id}'] = -1
            else:
                attributes[f'day_{id}'] = str(forceRound(value / 1000, 2))
                attributes['daily'].append(str(forceRound(value / 1000, 2)))
            id += 1

        current_week = attributes['current_week']
        if attributes['current_week'] == 0:
            attributes['current_week'] = -1

        today = datetime.now(timezone)
        last_week_last_year_datetime = today - relativedelta(years=1, days=nbDayWeek)
        last_week_last_year = last_week_last_year_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_week_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['current_week_last_year'] = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            attributes['current_week_last_year'] += value / 1000

        current_week_last_year = attributes['current_week_last_year']
        if attributes['current_week_last_year'] == 0:
            attributes['current_week_last_year'] = 0
        else:
            attributes['current_week_last_year'] = str(forceRound(attributes['current_week_last_year'], 2))

	# LAST DETAIL 
        query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' AND date = (select max(date) from consumption_detail);"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['last_detail'] = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            attributes['last_detail'] += value / 1000

        last_detail = attributes['last_detail']
        if attributes['last_detail'] == 0:
            attributes['last_detail'] = 0
        else:
            attributes['last_detail'] = str(forceRound(attributes['last_detail'], 4))

        # CURRENT MONTH
        today = datetime.now(timezone)
        last_month_datetime = today - relativedelta(months=1)
        last_month = last_month_datetime.strftime('%Y-%m')
        lastMonthNumber = last_month_datetime.strftime('%m')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_month}-01' AND '{yesterday}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['last_month'] = 0
        attributes['current_month'] = 0
        nbDayMonth = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            currentMonthNumber = today.strftime("%m")
            lastMonthNumber = last_month_datetime.strftime('%m')
            monthNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%m')
            if monthNumber == lastMonthNumber:
            	attributes['last_month'] += value / 1000
            if monthNumber == currentMonthNumber:
                attributes['current_month'] += value / 1000
                nbDayMonth += 1

        last_month = attributes['last_month']
        if attributes['last_month'] == 0:
            attributes['last_month'] = 0
        else:
            attributes['last_month'] = str(forceRound(attributes['last_month'], 2))

        current_month = attributes['current_month']
        if attributes['current_month'] == 0:
            attributes['current_month'] = 0
        else:
            attributes['current_month'] = str(forceRound(attributes['current_month'], 2))

        today = datetime.now(timezone)
        last_month_last_year_datetime = today - relativedelta(years=1, days=nbDayMonth)
        last_month_last_year = last_month_last_year_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_month_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['current_month_last_year'] = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            currentYearNumber = today.strftime("%m")
            YearNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%m')
            if YearNumber == currentYearNumber:
                attributes['current_month_last_year'] += value / 1000

        current_month_last_year = attributes['current_month_last_year']
        if attributes['current_month_last_year'] == 0:
            attributes['current_month_last_year'] = 0
        else:
            attributes['current_month_last_year'] = str(forceRound(attributes['current_month_last_year'], 2))

        # CURRENT MONTH
        today = datetime.now(timezone)
        last_month_last_year_datetime = today - relativedelta(years=1, months=1)
        last_month_last_year = last_month_last_year_datetime.strftime('%Y-%m')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_month_last_year}-01' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['last_month_last_year'] = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            lastYearLastMonthNumber = last_month_last_year_datetime.strftime('%m')
            monthNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%m')
            if monthNumber == lastMonthNumber:
                attributes['last_month_last_year'] += value / 1000

        last_month_last_year = attributes['last_month_last_year']
        if attributes['last_month_last_year'] == 0:
            attributes['last_month_last_year'] = 0
        else:
            attributes['last_month_last_year'] = str(forceRound(attributes['last_month_last_year'], 2))

        # CURRENT YEARS
        today = datetime.now(timezone)
        last_year_datetime = today - relativedelta(years=1)
        last_year = last_year_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_year}' AND '{yesterday}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['last_year'] = 0
        attributes['current_year'] = 0
        nbDayYear = 1
        for val in query_result:
            date = val[1]
            value = val[2]
            currentYearNumber = today.strftime("%Y")
            yearNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%Y')
            attributes['last_year'] += val[2] / 1000
            if yearNumber == currentYearNumber:
                attributes['current_year'] += value / 1000
                nbDayYear += 1

        current_year = attributes['current_year']
        if attributes['current_year'] == 0:
            attributes['current_year'] = 0
        else:
            attributes['current_year'] = str(forceRound(attributes['current_year'], 2))

        today = datetime.now(timezone)
        last_year_last_year_datetime = today - relativedelta(years=1, days=nbDayYear)
        last_year_last_year = last_year_last_year_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{last_year_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        attributes['current_year_last_year'] = 0
        for val in query_result:
            date = val[1]
            value = val[2]
            attributes['current_year_last_year'] += value / 1000

        current_year_last_year = attributes['current_year_last_year']
        if attributes['current_year_last_year'] == 0:
            attributes['current_year_last_year'] = 0
        else:
            attributes['current_year_last_year'] = str(forceRound(attributes['current_year_last_year'], 2))


        # WEEKLY
        attributes[f'dailyweek'] = []
        attributes['dailyweek_cost'] = [0, 0, 0, 0, 0, 0, 0]
        for measure_type in ["HP", "HC", "BASE"]:
            today = datetime.now(timezone)
            if measure_type != "BASE":
                attributes[f'dailyweek_cost{measure_type}'] = []
                attributes[f'dailyweek_{measure_type}'] = []
            for day in [1, 2, 3, 4, 5, 6, 7]:
                date = today - relativedelta(days=day)
                dateBegin = date.replace(hour=0, minute=30, second=0).strftime('%Y-%m-%d %H:%M:%S')
                dateEnd = date.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
                attributes[f'dailyweek'].append(date.strftime('%Y-%m-%d'))
                query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' AND date BETWEEN '{dateBegin}' AND '{dateEnd}' AND measure_type = '{measure_type}' ORDER BY DATE DESC;"
                cur.execute(query)
                query_result = cur.fetchall()
                if measure_type != "BASE":
                    attributes[f'day_{day}_{measure_type}'] = int(0)
                if not query_result:
                    if measure_type != "BASE":
                        attributes[f'day_{day}_{measure_type}'] = 0
                        attributes[f'dailyweek_cost{measure_type}'].append(0)
                        attributes[f'dailyweek_{measure_type}'].append(0)
                        attributes["dailyweek_cost"][day-1] = 0
                else:
                    value_wh_total = 0
                    dailyweek_cost = 0
                    for val in query_result:
                        date = val[1]
                        value_w = val[2]
                        interval = val[3]
                        plan = val[4]
                        value_wh = value_w * interval / 60
                        value_kwh = value_wh / 1000
                        if plan != "BASE":
                            attributes[f'day_{day}_{plan}'] += int(value_w)
                        value_wh_total += value_kwh
                        if pdl_config['plan'] == "BASE" or plan == "BASE":
                            dailyweek_cost += float(value_wh / 1000 * price[f"BASE"])
                        else:
                            dailyweek_cost += float(value_wh / 1000 * price[f"{plan}"])

                    attributes["dailyweek_cost"][day-1] += forceRound(dailyweek_cost, 2)

                    if plan != "BASE":
                        attributes[f'dailyweek_{plan}'].append(str(forceRound(value_wh_total, 2)))
                        attributes[f'dailyweek_cost{plan}'].append(str(forceRound(dailyweek_cost, 2)))

                    if day == 1:
                        attributes["daily_cost"] = attributes["dailyweek_cost"][day-1]
                        if plan != "BASE":
                            attributes[f"yesterday_{plan}_cost"] = str(forceRound(dailyweek_cost, 3))
                            attributes[f"yesterday_{plan}"] = str(forceRound(value_wh_total, 3))

        # IF DAILY COST EMPTY IN DETAIL, try in daily if in plan base
        if attributes['dailyweek_cost'] == [0, 0, 0, 0, 0, 0, 0] and pdl_config['plan'] == "BASE":
            today = datetime.now(timezone)
            for day in [1, 2, 3, 4, 5, 6, 7]:
                date = today - relativedelta(days=day)
                dateBegin = date.strftime('%Y-%m-%d')
                dateEnd = date.strftime('%Y-%m-%d')
                query = f"SELECT * FROM consumption_daily WHERE pdl = '{pdl}' AND date BETWEEN '{dateBegin}' AND '{dateEnd}' ORDER BY DATE DESC;"
                cur.execute(query)
                query_result = cur.fetchall()
                if not query_result:
                    attributes["dailyweek_cost"][day-1] = 0
                else:
                    for val in query_result:
                        date = val[1]
                        value_w = val[2]
                        value_wh = value_w
                        value_kwh = value_wh / 1000
                        dailyweek_cost = float(value_kwh * price[f"BASE"])
                        attributes["dailyweek_cost"][day - 1] += forceRound(dailyweek_cost, 2)

        convert = []
        for tmp in attributes["dailyweek_cost"]:
            convert.append(str(tmp))
        attributes["dailyweek_cost"] = convert
        peak_offpeak_percent = {
            'HP': 0,
            'HC': 0,
            'BASE': 0
        }
        query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' AND date BETWEEN '{last_year}' AND '{yesterday}' ORDER BY DATE DESC;"
        cur.execute(query)
        query_result = cur.fetchall()
        for val in query_result:
            value = val[2]
            interval = val[3]
            measure_type = val[4]
            peak_offpeak_percent[measure_type] += value

        if measure_type != "BASE":
            attributes['peak_offpeak_percent'] = forceRound(abs(100 * (peak_offpeak_percent['HC'] - peak_offpeak_percent['HP']) / peak_offpeak_percent['HP']), 2)
        else:
            attributes['peak_offpeak_percent'] = 0

        def variation(val1, val2):
            # print(f"100 * ({val1} - {val2}) / {val2}")
            result = 100 * (val1 - val2) / val2
            return result

        if last_month != 0 and last_month != 0 and last_month_last_year != 0 and last_month_last_year != 0:
            attributes['monthly_evolution'] = forceRound(variation(last_month, last_month_last_year), 2)
        else:
            attributes['monthly_evolution'] = 0

        if current_week != 0 and current_week != 0 and current_week_last_year != 0 and current_week_last_year != 0:
            attributes['current_week_evolution'] = forceRound(variation(current_week, current_week_last_year), 2)
        else:
            attributes['current_week_evolution'] = 0

        if current_month != 0 and current_month != 0 and current_month_last_year != 0 and current_month_last_year != 0:
            attributes['current_month_evolution'] = forceRound(variation(current_month, current_month_last_year), 2)
        else:
            attributes['current_month_evolution'] = 0

        if state != 0 and state != 0 and yesterdayLastYear != 0 and yesterdayLastYear != 0:
            attributes['yesterday_evolution'] = forceRound(variation(state, yesterdayLastYear), 2)
        else:
            attributes['yesterday_evolution'] = 0

        attributes[f'dailyweek'] = sorted(list(set(attributes[f'dailyweek'])), reverse=True)
        attributes[f'friendly_name'] = f"EnedisGateway.{pdl}"
        attributes[f'errorLastCall'] = f""
        attributes[f'errorLastCallInterne'] = f""
        attributes[f'current_week_number'] = int(datetime.now(timezone).strftime("%V"))

        if offpeak_hours != []:
            peak = ""
            id = 0
            for offpeak in offpeak_hours:
                peak += offpeak.upper()
                id += 1
                if id < len(offpeak_hours):
                    peak += ";"
            attributes[f'offpeak_hours_enedis'] = f"HC ({peak})"
            offpeak_hours_enedis = attributes[f'offpeak_hours_enedis']
            offpeak_hours_enedis = offpeak_hours_enedis[offpeak_hours_enedis.find("(") + 1:offpeak_hours_enedis.find(")")].split(';')
            offpeak_hours = []
            for hours in offpeak_hours_enedis:
                plage = hours.split("-")
                today = datetime.now(timezone)
                dateBegin = today.replace(hour=int(plage[0].split("H")[0]), minute=int(plage[0].split("H")[1]), second=0)
                dateEnd = today.replace(hour=int(plage[1].split("H")[0]), minute=int(plage[1].split("H")[1]), second=0)
                if dateBegin > dateEnd:
                    current = [str(plage[0]), str("00H00")]
                    offpeak_hours.append(current)
                    current = [str("00H00"), str(plage[1])]
                    offpeak_hours.append(current)
                else:
                    current = [str(plage[0]), str(plage[1])]
                    offpeak_hours.append(current)
            attributes[f'offpeak_hours'] = offpeak_hours
        else:
            attributes[f'offpeak_hours_enedis'] = 0
            attributes[f'offpeak_hours'] = 0

        query = f"SELECT * FROM config WHERE key = '{pdl}_subscribed_power'"
        cur.execute(query)
        query_result = cur.fetchone()
        attributes[f'subscribed_power'] = query_result[1]

        f.publish(client, f"sensor/{path}/state", str(state), ha_autodiscovery_prefix)
        f.publish(client, f"sensor/{path}/attributes", json.dumps(attributes), ha_autodiscovery_prefix)

        if not "debug" in main.config:
            debug = False
        else:
            debug = main.config["debug"]
        if debug == True:
            pprint(attributes)

    return ha_discovery

# typeCompteur: consommation
# horaireMinCall: 1041
# yesterdayConsumptionMaxPower: 9200
# halfhourly: []
# peak_hours: '40.304'
# yesterday_production: 0
