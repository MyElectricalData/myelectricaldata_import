import time

from dateutil.relativedelta import relativedelta

from config import *
from dependencies import *
from models.config import CONFIG, get_version
from models.cache import Cache
from models.mqtt import Mqtt
from models.influxdb import InfluxDB
from models.myelectricaldata import MyElectricalData

logo(get_version())

CONFIG.display()
CONFIG.check()

CACHE = Cache()
if CONFIG.get("wipe_cache"):
    CACHE.purge_cache()
    CONFIG.set("wipe_cache", False)
    logWarn()

MQTT_CONFIG = CONFIG.mqtt_config()
if MQTT_CONFIG and "enable" in MQTT_CONFIG and MQTT_CONFIG["enable"]:
    MQTT = Mqtt(
        hostname=MQTT_CONFIG["hostname"],
        port=MQTT_CONFIG["port"],
        username=MQTT_CONFIG["username"],
        password=MQTT_CONFIG["password"],
        client_id=MQTT_CONFIG["client_id"],
        prefix=MQTT_CONFIG["prefix"],
        retain=MQTT_CONFIG["retain"],
        qos=MQTT_CONFIG["qos"]
    )

INFLUXDB_CONFIG = CONFIG.influxdb_config()
if INFLUXDB_CONFIG and "enable" in INFLUXDB_CONFIG and INFLUXDB_CONFIG["enable"]:
    INFLUXDB = InfluxDB(
        hostname=INFLUXDB_CONFIG["hostname"],
        port=INFLUXDB_CONFIG["port"],
        token=INFLUXDB_CONFIG["token"],
        org=INFLUXDB_CONFIG["org"],
        bucket=INFLUXDB_CONFIG["bucket"]
    )
    if CONFIG.get("wipe_influxdb"):
        INFLUXDB.purge_influxdb()
        CONFIG = CONFIG.set("wipe_influxdb", False)
        logWarn()

CYCLE = CONFIG.get('cycle')
if CYCLE < cycle_minimun:
    warning("Le cycle minimun est de 3600s")
    CYCLE = cycle_minimun
    CONFIG.set("cycle", cycle_minimun)



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


if __name__ == '__main__':

    # while True:
    print(CONFIG.get('myelectricaldata'))
    for usage_point_id, config in CONFIG.get('myelectricaldata').items():

        myelectricaldata = MyElectricalData(
            cache=CACHE,
            url=url,
            usage_point_id=usage_point_id,
            config=config
        )

        logSep()
        log("Récupération du contrat :")
        myelectricaldata.contract()


    # logSep()
    # date = datetime.datetime.now() + relativedelta(seconds=CYCLE)
    # log(f"Prochain import : {date}")
    # time.sleep(CYCLE)
