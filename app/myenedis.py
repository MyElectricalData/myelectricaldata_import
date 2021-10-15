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

def myEnedis(cur, con, client,last_activation_date=datetime.now(pytz.timezone('Europe/Paris')), offpeak_hours=None):
    pdl = main.pdl

    def chop_to_n_decimals(x, n):
        # This "rounds towards 0".  The decimal module
        # offers many other rounding modes - see the docs.
        import decimal
        d = decimal.Decimal(repr(x))
        targetdigit = decimal.Decimal("1e%d" % -n)
        chopped = d.quantize(targetdigit, decimal.ROUND_DOWN)
        return float(chopped)

    price = {
        "BASE": main.consumption_price_base,
        "HC": main.consumption_price_hc,
        "HP": main.consumption_price_hp
    }

    ha_autodiscovery_prefix= main.ha_autodiscovery_prefix

    ha_discovery = {
        pdl: {}
    }

    name = f"enedisgateway_{pdl}"
    config = {
        "name": name,
        "stat_t": f"{ha_autodiscovery_prefix}/sensor/{name}/state",
        "json_attr_t": f"{ha_autodiscovery_prefix}/sensor/{name}/attributes",
        "unit_of_measurement": "kWh",
    }

    f.publish(client, f"sensor/{name}/config", json.dumps(config), ha_autodiscovery_prefix)

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
    while found == False:
        yesterday_datetime = today - relativedelta(days=1+delta)
        yesterday = yesterday_datetime.strftime('%Y-%m-%d')
        query = f"SELECT * FROM consumption_daily WHERE date='{yesterday}';"
        cur.execute(query)
        query_result = cur.fetchone()
        attributes['yesterdayDate'] = yesterday
        if query_result[2] != 0 and query_result != None:
            attributes['yesterday'] = query_result[2]
            found = True
        else:
            attributes['yesterday'] = -1
            delta =+ 1
    state = attributes['yesterday']

    today = datetime.now(timezone)
    yesterday_last_year_datetime = today - relativedelta(years=1, days=1)
    yesterday_last_year = yesterday_last_year_datetime.strftime('%Y-%m-%d')
    attributes["yesterdayLastYearDate"] = yesterday_last_year
    query = f"SELECT * FROM consumption_daily WHERE date='{yesterday_last_year}';"
    cur.execute(query)
    query_result = cur.fetchone()

    if query_result != None and query_result[2] != 0:
        attributes['yesterdayLastYear'] = query_result[2]
    else:
        attributes['yesterdayLastYear'] = -1
    yesterdayLastYear = attributes['yesterdayLastYear']

    # CURRENT WEEK
    today = datetime.now(timezone)
    last_week_datetime = today - relativedelta(days=8)
    last_week = last_week_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_week}' AND '{yesterday}' ORDER BY DATE DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    attributes['last_week'] = 0
    attributes['daily'] = []
    attributes['current_week'] = 0
    id = 1
    current_week = 0
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
            attributes['daily'].append(-1)
            attributes[f'day_{id}'] = -1
            attributes['daily'].append(str(chop_to_n_decimals(value / 1000, 2)))
        else:
            attributes[f'day_{id}'] = str(chop_to_n_decimals(value / 1000, 2))
            attributes['daily'].append(str(chop_to_n_decimals(value / 1000, 2)))
        id += 1
    current_week = attributes['current_week']

    today = datetime.now(timezone)
    last_week_last_year_datetime = today - relativedelta(years=1, days=nbDayWeek)
    last_week_last_year = last_week_last_year_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_week_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    attributes['current_week_last_year'] = 0
    for val in query_result:
        date = val[1]
        value = val[2]
        attributes['current_week_last_year'] += value / 1000
    current_week_last_year = attributes['current_week_last_year']
    attributes['current_week_last_year'] = str(chop_to_n_decimals(current_week_last_year, 2))

    # CURRENT MONTH
    today = datetime.now(timezone)
    last_month_datetime = today - relativedelta(months=1)
    last_month = last_month_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_month}' AND '{yesterday}' ORDER BY DATE DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    attributes['last_month'] = 0
    attributes['current_month'] = 0
    nbDayMonth = 0
    for val in query_result:
        date = val[1]
        value = val[2]
        currentMonthNumber = today.strftime("%m")
        monthNumber = datetime.strptime(date, '%Y-%m-%d').strftime('%m')
        attributes['last_month'] += value / 1000
        if monthNumber == currentMonthNumber:
            attributes['current_month'] += value / 1000
            nbDayMonth += 1
    current_month = attributes['current_month']
    attributes['current_month'] = str(chop_to_n_decimals(current_month, 2))
    last_month = attributes['last_month']

    today = datetime.now(timezone)
    last_month_last_year_datetime = today - relativedelta(years=1, days=nbDayMonth)
    last_month_last_year = last_month_last_year_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_month_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
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
    attributes['current_month_last_year'] = str(chop_to_n_decimals(current_month_last_year, 2))

    # CURRENT MONTH
    today = datetime.now(timezone)
    last_month_last_year_datetime = today - relativedelta(years=1, months=1)
    last_month_last_year = last_month_last_year_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_month_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    attributes['last_month_last_year'] = 0
    for val in query_result:
        date = val[1]
        value = val[2]
        attributes['last_month_last_year'] += value / 1000
    last_month_last_year = attributes['last_month_last_year']
    attributes['last_month_last_year'] = str(chop_to_n_decimals(last_month_last_year, 2))

    # CURRENT YEARS
    today = datetime.now(timezone)
    last_year_datetime = today - relativedelta(years=1)
    last_year = last_year_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_year}' AND '{yesterday}' ORDER BY DATE DESC;"
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
    attributes['current_year'] = str(chop_to_n_decimals(attributes['current_year'], 2))
    today = datetime.now(timezone)
    last_year_last_year_datetime = today - relativedelta(years=1, days=nbDayYear)
    last_year_last_year = last_year_last_year_datetime.strftime('%Y-%m-%d')
    query = f"SELECT * FROM consumption_daily WHERE date BETWEEN '{last_year_last_year}' AND '{yesterday_last_year}' ORDER BY DATE DESC;"
    cur.execute(query)
    query_result = cur.fetchall()
    attributes['current_year_last_year'] = 0
    for val in query_result:
        date = val[1]
        value = val[2]
        attributes['current_year_last_year'] += value / 1000
    attributes['current_year_last_year'] = str(chop_to_n_decimals(attributes['current_year_last_year'], 2))

    # WEEKLY
    attributes[f'dailyweek'] = []
    attributes['dailyweek_cost'] = [0, 0, 0, 0, 0, 0, 0]
    for measure_type in ["HP", "HC"]:
        today = datetime.now(timezone)
        attributes[f'dailyweek_cost{measure_type}'] = []
        attributes[f'dailyweek_{measure_type}'] = []
        for day in [1, 2, 3, 4, 5, 6, 7]:
            date = today - relativedelta(days=day)
            dateBegin = date.replace(hour=0, minute=30, second=0).strftime('%Y-%m-%d %H:%M:%S')
            dateEnd = date.replace(hour=23, minute=59, second=59).strftime('%Y-%m-%d %H:%M:%S')
            attributes[f'dailyweek'].append(date.strftime('%Y-%m-%d'))
            query = f"SELECT * FROM consumption_detail WHERE date BETWEEN '{dateBegin}' AND '{dateEnd}' AND measure_type = '{measure_type}' ORDER BY DATE DESC;"
            cur.execute(query)
            query_result = cur.fetchall()
            attributes[f'day_{day}_{measure_type}'] = int(0)
            if query_result == []:
                attributes[f'day_{day}_{measure_type}'] = '-1'
                attributes[f'dailyweek_cost{measure_type}'].append(-1)
                attributes[f'dailyweek_{measure_type}'].append(-1)
                attributes["dailyweek_cost"][day-1] = -1
            else:
                value_wh_total = 0
                dailyweek_cost = 0
                for val in query_result:
                    date = val[1]
                    interval = val[3]
                    value_w = val[2]
                    value_wh = value_w * interval / 60
                    value_kwh = value_wh / 1000

                    attributes[f'day_{day}_{measure_type}'] += int(value_w)
                    value_wh_total += value_kwh
                    dailyweek_cost += float(value_wh / 1000 * price[f"{measure_type}"])

                attributes[f'dailyweek_{measure_type}'].append(str(chop_to_n_decimals(value_wh_total, 2)))
                attributes[f'dailyweek_cost{measure_type}'].append(str(chop_to_n_decimals(dailyweek_cost, 2)))
                attributes["dailyweek_cost"][day-1] += chop_to_n_decimals(dailyweek_cost, 2)
                if day == 1:
                    attributes["daily_cost"] = attributes["dailyweek_cost"][day-1]
                    attributes[f"yesterday_{measure_type}_cost"] = str(chop_to_n_decimals(dailyweek_cost, 3))
                    attributes[f"yesterday_{measure_type}"] = str(chop_to_n_decimals(value_wh_total, 3))

    convert = []
    for tmp in attributes["dailyweek_cost"]:
        convert.append(str(tmp))
    attributes["dailyweek_cost"] = convert

    peak_offpeak_percent = {
        'HP': 0,
        'HC': 0
    }
    query = f"SELECT * FROM consumption_detail WHERE pdl = '{pdl}' AND date BETWEEN '{last_year}' AND '{yesterday}' ORDER BY DATE DESC;"
    print(query)
    cur.execute(query)
    query_result = cur.fetchall()
    pprint(query_result)
    for val in query_result:
        value = val[3]
        measure_type = val[4]
        peak_offpeak_percent[measure_type] += value

    pprint(peak_offpeak_percent)
    attributes['peak_offpeak_percent'] = chop_to_n_decimals(abs(100 * (peak_offpeak_percent['HC'] - peak_offpeak_percent['HP']) / peak_offpeak_percent['HP']), 2)

    attributes['monthly_evolution'] = chop_to_n_decimals(100 * (last_month - last_month_last_year) / last_month_last_year, 2)
    attributes['monthly_evolution'] = chop_to_n_decimals(100 * (current_week - current_week_last_year) / current_week_last_year, 2)
    attributes['current_month_evolution'] = chop_to_n_decimals(100 * (current_month - current_month_last_year) / current_month_last_year, 2)
    attributes['yesterday_evolution'] = chop_to_n_decimals(100 * (state - yesterdayLastYear) / yesterdayLastYear, 2)

    attributes[f'dailyweek'] = sorted(list(set(attributes[f'dailyweek'])), reverse=True)
    attributes[f'friendly_name'] = f"EnedisGateway.{pdl}"
    attributes[f'errorLastCall'] = f""
    attributes[f'errorLastCallInterne'] = f""
    attributes[f'current_week_number'] = int(datetime.now(timezone).strftime("%V"))

    query = f"SELECT * FROM config WHERE key = '{pdl}_offpeak_hours'"
    cur.execute(query)
    query_result = cur.fetchone()
    attributes[f'offpeak_hours_enedis'] = query_result[1]

    offpeak_hours_enedis = query_result[1]
    offpeak_hours_enedis = offpeak_hours_enedis[offpeak_hours_enedis.find("(") + 1:offpeak_hours_enedis.find(")")].split(';')
    offpeak_hours = []
    for hours in offpeak_hours_enedis:
        plage = hours.split("-")
        if plage[0] > plage[1]:
            current = [str(plage[0]), str("00h00")]
            offpeak_hours.append(current)
            current = [str("00h00"), str(plage[1])]
            offpeak_hours.append(current)
        else:
            current = [str(plage[0]), str(plage[1])]
            offpeak_hours.append(current)

    attributes[f'offpeak_hours'] = offpeak_hours

    query = f"SELECT * FROM config WHERE key = '{pdl}_subscribed_power'"
    cur.execute(query)
    query_result = cur.fetchone()
    attributes[f'subscribed_power'] = query_result[1]

    f.publish(client, f"sensor/{name}/state", str(state), ha_autodiscovery_prefix)
    f.publish(client, f"sensor/{name}/attributes", json.dumps(attributes), ha_autodiscovery_prefix)

    quit()

    return ha_discovery

# typeCompteur: consommation
# horaireMinCall: 1041
# yesterdayConsumptionMaxPower: 9200
# halfhourly: []
# peak_hours: '40.304'
# yesterday_production: 0


# attribution: ''
# version: 1.3.1.14
# versionGit: 1.3.1.14
# versionUpdateAvailable: false
# nbCall: 12
# typeCompteur: consommation
# numPDL: '01226049119129'
# horaireMinCall: 1041
# activationDate: '2018-08-31'
# lastUpdate: '2021-10-14T22:31:32.484523'
# timeLastCall: '2021-10-14T22:32:19.680487'
# yesterday: 56055
# last_week: 289631
# yesterdayDate: '2021-10-13'
# yesterdayLastYear: 39768
# yesterdayLastYearDate: '2021-10-13'
# yesterdayConsumptionMaxPower: 9200
# day_1_HP: 40304
# day_2_HP: 30949
# day_3_HP: 31955
# day_4_HP: 41390
# day_5_HP: 30133
# day_6_HP: 36046
# day_7_HP: 35161
# day_1_HC: 15751
# day_2_HC: 8329
# day_3_HC: 5438
# day_4_HC: 6689
# day_5_HC: 6936
# day_6_HC: 6091
# day_7_HC: 6464
# dailyweek_cost:
#   - '8.61'
#   - '6.14'
#   - '5.95'
#   - '7.66'
#   - '5.83'
#   - '6.70'
#   - '6.60'
# dailyweek_costHC:
#   - '1.96'
#   - '1.04'
#   - '0.68'
#   - '0.83'
#   - '0.86'
#   - '0.76'
#   - '0.80'
# dailyweek_HC:
#   - '15.751'
#   - '8.329'
#   - '5.438'
#   - '6.689'
#   - '6.936'
#   - '6.091'
#   - '6.464'
# dailyweek:
#   - '2021-10-13'
#   - '2021-10-12'
#   - '2021-10-11'
#   - '2021-10-10'
#   - '2021-10-09'
#   - '2021-10-08'
#   - '2021-10-07'
# dailyweek_costHP:
#   - '6.65'
#   - '5.10'
#   - '5.27'
#   - '6.83'
#   - '4.97'
#   - '5.94'
#   - '5.80'
# dailyweek_HP:
#   - '40.304'
#   - '30.949'
#   - '31.955'
#   - '41.390'
#   - '30.133'
#   - '36.046'
#   - '35.161'
# day_1: '56.05'
# day_2: '39.28'
# day_3: '37.39'
# day_4: '48.08'
# day_5: '37.07'
# day_6: '42.14'
# day_7: '41.62'
# daily:
#   - '56.05'
#   - '39.28'
#   - '37.39'
#   - '48.08'
#   - '37.07'
#   - '42.14'
#   - '41.62'
# halfhourly: []
# offpeak_hours:
#   - - '22:38'
#     - '23:59'
#   - - '00:00'
#     - '06:38'
# peak_hours: '40.304'
# peak_offpeak_percent: '71.90'
# yesterday_HC_cost: '1.959'
# yesterday_HP_cost: '6.647'
# daily_cost: '8.61'
# yesterday_HC: '15.751'
# yesterday_HP: '40.304'
# current_week: '132.726'
# current_week_number: 41
# current_week_last_year: '113.791'
# last_month: '1036.036'
# last_month_last_year: '921.418'
# current_month: '526.046'
# current_month_last_year: '480.054'
# last_year: '18702.059'
# current_year: '15394.750'
# errorLastCall: ''
# errorLastCallInterne: ''
# monthly_evolution: '12.439'
# current_week_evolution: '16.640'
# current_month_evolution: '9.581'
# yesterday_evolution: '40.955'
# subscribed_power: 12 kVA
# offpeak_hours_enedis: HC (22H38-6H38)
# yesterday_production: 0
# unit_of_measurement: kWh
# friendly_name: myEnedis.01226049119129

