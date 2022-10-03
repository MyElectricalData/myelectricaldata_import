from config import *
from dependencies import *
from models.config import config
from models.cache import Cache, wipe_cache

logo(VERSION)
config.display()

if config.get("wipe_cache"):
    wipe_cache()

cache = Cache()

#
# def run(pdl, pdl_config):
#     f.logLine()
#     f.title(pdl)
#
#     global offpeak_hours
#
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': pdl_config['token'],
#         'call-service': "enedisgateway2mqtt",
#         'version': VERSION
#     }
#
#     f.logLine()
#     f.log("Get contract :")
#     contract = cont.getContract(headers, client, cur, con, pdl, pdl_config)
#     offpeak_hours = []
#     f.log(contract, "debug")
#     if "error_code" in contract:
#         f.publish(client, f"error", str(1))
#         for key, data in contract["detail"].items():
#             f.publish(client, f"errorMsg/{key}", str(data))
#         f.log("-- Stop import --")
#     else:
#         f.publish(client, f"error", str(0))
#
#         for pdl, contract_data in contract.items():
#             for key, data in contract_data.items():
#                 if key == "last_activation_date":
#                     last_activation_date = data
#                 if key == "offpeak_hours":
#                     offpeak_hours = data
#                 if "home_assistant" in config and "discovery" in config['home_assistant'] and config['home_assistant'][
#                     'discovery'] == True:
#                     ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=key, value=data)
#
#         f.logLine()
#         f.log("Get Addresses :")
#         addresse = addr.getAddresses(headers, client, con, cur, pdl, pdl_config)
#         if "error_code" in addresse:
#             f.publish(client, f"addresses/error", str(1))
#             for key, data in addresse["detail"].items():
#                 f.publish(client, f"addresses/errorMsg/{key}", str(data))
#         else:
#             f.publish(client, f"addresses/error", str(0))
#
#         if pdl_config['consumption'] == True:
#             f.logLine()
#             f.log("Get Consumption :")
#             ha_discovery_consumption = day.getDaily(headers, cur, con, client, pdl, pdl_config, "consumption",
#                                                     last_activation_date)
#             f.logLine1()
#             f.log("                        SUCCESS : Consumption daily imported")
#             f.logLine1()
#             if config['home_assistant']['discovery'] == True:
#                 f.logLine()
#                 f.log("Home Assistant auto-discovery (Consumption) :")
#                 for pdl, data in ha_discovery_consumption.items():
#                     for name, sensor_data in data.items():
#                         if "attributes" in sensor_data:
#                             attributes = sensor_data['attributes']
#                         else:
#                             attributes = None
#                         if "unit_of_meas" in sensor_data:
#                             unit_of_meas = sensor_data['unit_of_meas']
#                         else:
#                             unit_of_meas = None
#                         if "device_class" in sensor_data:
#                             device_class = sensor_data['device_class']
#                         else:
#                             device_class = None
#                         if "state_class" in sensor_data:
#                             state_class = sensor_data['state_class']
#                         else:
#                             state_class = None
#                         if "value" in sensor_data:
#                             ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                                value=sensor_data['value'],
#                                                attributes=attributes, unit_of_meas=unit_of_meas,
#                                                device_class=device_class, state_class=state_class)
#             f.log(" => HA Sensor updated")
#         # f.logLine()
#
#         if pdl_config['consumption_detail']:
#             f.log("Get Consumption Detail:")
#             ha_discovery_consumption = detail.getDetail(headers, cur, con, client, pdl, pdl_config, "consumption",
#                                                         last_activation_date, offpeak_hours=offpeak_hours)
#             f.logLine1()
#             f.log("                   SUCCESS : Consumption detail imported")
#             f.logLine1()
#             if config['home_assistant']['discovery'] == True:
#                 f.logLine()
#                 f.log("Home Assistant auto-discovery (Consumption Detail) :")
#                 for pdl, data in ha_discovery_consumption.items():
#                     for name, sensor_data in data.items():
#                         if "attributes" in sensor_data:
#                             attributes = sensor_data['attributes']
#                         else:
#                             attributes = None
#                         if "unit_of_meas" in sensor_data:
#                             unit_of_meas = sensor_data['unit_of_meas']
#                         else:
#                             unit_of_meas = None
#                         if "device_class" in sensor_data:
#                             device_class = sensor_data['device_class']
#                         else:
#                             device_class = None
#                         if "state_class" in sensor_data:
#                             state_class = sensor_data['state_class']
#                         else:
#                             state_class = None
#                         if "value" in sensor_data:
#                             ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                                value=sensor_data['value'],
#                                                attributes=attributes, unit_of_meas=unit_of_meas,
#                                                device_class=device_class, state_class=state_class)
#                 f.log(" => HA Sensor updated")
#         # f.logLine()
#
#         if pdl_config['production'] == True:
#             f.logLine()
#             f.log("Get production :")
#             ha_discovery_production = day.getDaily(headers, cur, con, client, pdl, pdl_config, "production",
#                                                    last_activation_date)
#             f.logLine1()
#             f.log("             SUCCESS : Production daily imported")
#             f.logLine1()
#             if config['home_assistant']['discovery'] == True:
#                 f.logLine()
#                 f.log("Home Assistant auto-discovery (Production) :")
#                 for pdl, data in ha_discovery_production.items():
#                     for name, sensor_data in data.items():
#                         if "attributes" in sensor_data:
#                             attributes = sensor_data['attributes']
#                         else:
#                             attributes = None
#                         if "unit_of_meas" in sensor_data:
#                             unit_of_meas = sensor_data['unit_of_meas']
#                         else:
#                             unit_of_meas = None
#                         if "device_class" in sensor_data:
#                             device_class = sensor_data['device_class']
#                         else:
#                             device_class = None
#                         if "state_class" in sensor_data:
#                             state_class = sensor_data['state_class']
#                         else:
#                             state_class = None
#                         ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                            value=sensor_data['value'],
#                                            attributes=attributes, unit_of_meas=unit_of_meas,
#                                            device_class=device_class, state_class=state_class)
#                 f.log(" => HA Sensor updated")
#
#         if pdl_config['production_detail'] == True:
#             f.logLine()
#             f.log("Get production Detail:")
#             ha_discovery_consumption = detail.getDetail(headers, cur, con, client, pdl, pdl_config, "production",
#                                                         last_activation_date)
#             f.logLine1()
#             f.log("              SUCCESS : Production detail imported")
#             f.logLine1()
#             if config['home_assistant']['discovery'] == True:
#                 f.logLine()
#                 f.log("Home Assistant auto-discovery (Production Detail) :")
#                 for pdl, data in ha_discovery_consumption.items():
#                     for name, sensor_data in data.items():
#                         if "attributes" in sensor_data:
#                             attributes = sensor_data['attributes']
#                         else:
#                             attributes = None
#                         if "unit_of_meas" in sensor_data:
#                             unit_of_meas = sensor_data['unit_of_meas']
#                         else:
#                             unit_of_meas = None
#                         if "device_class" in sensor_data:
#                             device_class = sensor_data['device_class']
#                         else:
#                             device_class = None
#                         if "state_class" in sensor_data:
#                             state_class = sensor_data['state_class']
#                         else:
#                             state_class = None
#                         if "value" in sensor_data:
#                             ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                                value=sensor_data['value'],
#                                                attributes=attributes, unit_of_meas=unit_of_meas,
#                                                device_class=device_class, state_class=state_class)
#                 f.log(" => HA Sensor updated")
#
#         if "influxdb" in config and config["influxdb"] != {}:
#             f.logLine()
#             f.log("Push data in influxdb")
#             influx.influxdb_insert(cur, con, pdl, pdl_config, influxdb, influxdb_api)
#             f.log(" => Data exported")
#
#         if "home_assistant" in config and "card_myenedis" in config['home_assistant'] and config['home_assistant'][
#             'card_myenedis'] == True:
#             f.logLine()
#             f.log("Generate Sensor for myEnedis card")
#             my_enedis_data = myenedis.myEnedis(cur, con, client, pdl, pdl_config, last_activation_date,
#                                                offpeak_hours=offpeak_hours)
#             for pdl, data in my_enedis_data.items():
#                 for name, sensor_data in data.items():
#                     if "attributes" in sensor_data:
#                         attributes = sensor_data['attributes']
#                     else:
#                         attributes = None
#                     if "unit_of_meas" in sensor_data:
#                         unit_of_meas = sensor_data['unit_of_meas']
#                     else:
#                         unit_of_meas = None
#                     if "device_class" in sensor_data:
#                         device_class = sensor_data['device_class']
#                     else:
#                         device_class = None
#                     if "state_class" in sensor_data:
#                         state_class = sensor_data['state_class']
#                     else:
#                         state_class = None
#                     if "value" in sensor_data:
#                         ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                            value=sensor_data['value'],
#                                            attributes=attributes, unit_of_meas=unit_of_meas,
#                                            device_class=device_class, state_class=state_class)
#             f.log(" => Sensor generated")
#
#         if "home_assistant" in config and "hourly" in config['home_assistant'] and config['home_assistant'][
#             'hourly'] == True:
#             f.logLine()
#             f.log("Generate Hourly Sensor")
#             hourly_data = hourly.Hourly(cur, con, client, pdl, pdl_config, last_activation_date,
#                                         offpeak_hours=offpeak_hours)
#             for pdl, data in my_enedis_data.items():
#                 for name, sensor_data in data.items():
#                     if "attributes" in sensor_data:
#                         attributes = sensor_data['attributes']
#                     else:
#                         attributes = None
#                     if "unit_of_meas" in sensor_data:
#                         unit_of_meas = sensor_data['unit_of_meas']
#                     else:
#                         unit_of_meas = None
#                     if "device_class" in sensor_data:
#                         device_class = sensor_data['device_class']
#                     else:
#                         device_class = None
#                     if "state_class" in sensor_data:
#                         state_class = sensor_data['state_class']
#                     else:
#                         state_class = None
#                     if "value" in sensor_data:
#                         ha.haAutodiscovery(config=config, client=client, type="sensor", pdl=pdl, name=name,
#                                            value=sensor_data['value'],
#                                            attributes=attributes, unit_of_meas=unit_of_meas,
#                                            device_class=device_class, state_class=state_class)
#             f.log(" => Sensor generated")
#
#         query = f"SELECT * FROM consumption_daily WHERE pdl == '{pdl}' AND fail > {fail_count} ORDER BY date"
#         rows = con.execute(query)
#         if rows.fetchone() is not None:
#             f.logLine()
#             f.log(f"Consumption data not found on enedis (after {fail_count} retry) :")
#             # pprint(rows.fetchall())
#             # pprint(rows)
#             for row in rows:
#                 f.log(f"{row[0]} => {row[1]}")
#     con.commit()
#
#     f.logLine()
#     f.log("IMPORT FINISH")
#     f.logLine()
#
#
# if __name__ == '__main__':
#
#     if lost_params != []:
#         f.log(f'Some mandatory parameters are missing :', "ERROR")
#         for param in lost_params:
#             f.log(f'- {param}', "ERROR")
#         f.log("", "ERROR")
#         f.log("You can get list of parameters here :", "ERROR")
#         f.log(f" => https://github.com/m4dm4rtig4n/enedisgateway2mqtt#configuration-file", "ERROR")
#         f.log("-- Stop application --", "CRITICAL")
#
#     f.logLine()
#     f.logo(VERSION)
#     if "mqtt" in config:
#         f.log("MQTT")
#         for id, value in config['mqtt'].items():
#             if id == "password":
#                 value = "** hidden **"
#             f.log(f" - {id} : {value}")
#     else:
#         f.log("MQTT Configuration missing !", "CRITICAL")
#
#     if "home_assistant" in config:
#         f.logLine()
#         f.log("Home Assistant")
#         for id, value in config['home_assistant'].items():
#             f.log(f" - {id} : {value}")
#
#     if "influxdb" in config:
#         f.logLine()
#         f.log("InfluxDB")
#         for id, value in config['influxdb'].items():
#             if id == "token":
#                 value = "** hidden **"
#             f.log(f" - {id} : {value}")
#
#     if "enedis_gateway" in config:
#         f.logLine()
#         f.log("Enedis Gateway")
#         for pdl, data in config['enedis_gateway'].items():
#             f.log(f" - {pdl}")
#             for id, value in data.items():
#                 if id == "token":
#                     value = "** hidden **"
#                 f.log(f"     {id} : {value}")
#     else:
#         f.log("Enedis Gateway Configuration missing !", "CRITICAL")
#     f.logLine()
#
#     # SQLlite
#     f.log("Check database/cache")
#
#     if not os.path.exists('/data'):
#         os.mkdir('/data')
#
#
#
#     # MQTT
#     f.logLine()
#     client = f.connect_mqtt()
#     client.loop_start()
#
#     # INFLUXDB
#     if "influxdb" in config and config["influxdb"] != {}:
#         f.logLine()
#         f.log("InfluxDB connect :")
#
#         date_utils.date_helper = DateHelper(timezone=tzlocal())
#         if "scheme" not in config['influxdb']:
#             scheme = "http"
#         else:
#             scheme = config['influxdb']['scheme']
#         influxdb = influxdb_client.InfluxDBClient(
#             url=f"{scheme}://{config['influxdb']['host']}:{config['influxdb']['port']}",
#             token=config['influxdb']['token'],
#             org=config['influxdb']['org'],
#             timeout="600000"
#         )
#         health = influxdb.health()
#         if health.status == "pass":
#             f.log(" => Connection success")
#         else:
#             f.log(" => Connection failed", "CRITICAL")
#
#         influxdb_api = influxdb.write_api(write_options=ASYNCHRONOUS)
#
#     if "wipe_influxdb" in config and config["wipe_influxdb"] == True:
#         f.log(f"Reset InfluxDB data")
#         delete_api = influxdb.delete_api()
#         start = "1970-01-01T00:00:00Z"
#         stop = datetime.utcnow()
#         delete_api.delete(start, stop, '_measurement="enedisgateway_daily"', config['influxdb']['bucket'],
#                           org=config['influxdb']['org'])
#         start = datetime.utcnow() - relativedelta(years=2)
#         delete_api.delete(start, stop, '_measurement="enedisgateway_detail"', config['influxdb']['bucket'],
#                           org=config['influxdb']['org'])
#         f.log(f" => Data reset")
#         config["wipe_influxdb"] = False
#
#     while True:
#
#         con = sqlite3.connect('/data/enedisgateway.db', timeout=10)
#         cur = con.cursor()
#
#         for pdl, pdl_config in config['enedis_gateway'].items():
#             run(pdl, pdl_config)
#
#         con.close()
#
#         with open("/data/config.yaml", 'r+') as f:
#             text = f.read()
#             text = re.sub('wipe_cache:.*', 'wipe_cache: false', text)
#             text = re.sub('wipe_influxdb:.*', 'wipe_influxdb: false', text)
#             text = re.sub('    refresh_contract:.*', '    refresh_contract: false', text)
#             text = re.sub('    refresh_addresses:.*', '    refresh_addresses: false', text)
#             f.seek(0)
#             f.write(text)
#             f.truncate()
#
#         time.sleep(config['cycle'])
