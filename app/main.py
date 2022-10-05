import time
import json

from config import *
from dependencies import *
from models.config import CONFIG, get_version
from models.cache import Cache
from models.mqtt import Mqtt
from models.influxdb import InfluxDB
from models.query_address import Address
from models.query_contract import Contract
from models.query_consumption_daily import ConsumptionDaily

logo(get_version())

CONFIG.display()
CONFIG.check()

if CONFIG.get("wipe_cache"):
    CACHE.purge_cache()
    CONFIG.set("wipe_cache", False)
    logWarn()

MQTT_CONFIG = CONFIG.mqtt_config()
MQTT_ENABLE = False
MQTT = None
if MQTT_CONFIG and "enable" in MQTT_CONFIG and MQTT_CONFIG["enable"]:
    MQTT_ENABLE = True
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
INFLUXB_ENABLE = False
INFLUXDB = None
if INFLUXDB_CONFIG and "enable" in INFLUXDB_CONFIG and INFLUXDB_CONFIG["enable"]:
    INFLUXB_ENABLE = True
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

if __name__ == '__main__':

    # while True:
    for usage_point_id, config in CONFIG.get('myelectricaldata').items():
        ha_discovery = {usage_point_id: {}}

        result = {}

        headers = {
            'Content-Type': 'application/json',
            'Authorization': config['token'],
            'call-service': "myelectricaldata",
            'version': get_version()
        }

        logSep()
        log("Récupération du contrat :")
        result["contract"] = Contract(
            headers=headers,
            usage_point_id=usage_point_id,
            config=config
        ).get()

        activation_date = False
        if result.get('contract', {}).get('contracts', {}).get('last_activation_date', {}):
            activation_date = result["contract"]["contracts"]["last_activation_date"]

        offpeak_hours = False
        if result.get('contract', {}).get('contracts', {}).get('offpeak_hours', {}):
            offpeak_hours = result["contract"]["contracts"]["offpeak_hours"]

        logSep()
        log("Récupération de coordonnée :")
        result["addresses"] = Address(
            headers=headers,
            usage_point_id=usage_point_id,
            config=config
        ).get()

        if config["consumption"]:
            logSep()
            log("Récupération de la consommation journalière :")
            result["consumption_daily"] = ConsumptionDaily(
                headers=headers,
                usage_point_id=usage_point_id,
                config=config,
                activation_date=activation_date,
                offpeak_hours=offpeak_hours
            ).get()

        # if config["consumption_detail"]:
        #     logSep()
        #     log("Récupération de la consommation détaillé :")
        #     result["consumption_detail"] = ConsumptionDetail(
        #         usage_point_id=usage_point_id,
        #         config=config
        #     ).get()
        #
        # if config["production"]:
        #     logSep()
        #     log("Récupération de la production journalière :")
        #     result["production_daily"] = ProductionDaily(
        #         usage_point_id=usage_point_id,
        #         config=config
        #     ).get()
        #
        # if config["production_detail"]:
        #     logSep()
        #     log("Récupération de la production détaillé :")
        #     result["production_detail"] = ProductionDetail(
        #         usage_point_id=usage_point_id,
        #         config=config
        #     ).get()

        print(json.dumps(result, sort_keys=True, indent=4))

        # if "error" in contract:
        #     error(contract["description"])
        #     ha_discovery = {"error_code": True, "detail": {"message": contract["description"]}}
        #     if MQTT_ENABLE:
        #         for key, msg in contract.items():
        #             MQTT.publish(topic=f"{usage_point_id}/contract/{key}", msg=str(msg))
        # else:
        #     if MQTT_ENABLE:
        #         MQTT.publish(topic=f"{usage_point_id}/contract/error", msg=str(0))
        #         for key, msg in contract.items():
        #             MQTT.publish(topic=f"{usage_point_id}/contract/{key}", msg=str(msg))

        # if "error_code" in contract:
        #     f.log(contract["description"])
        #     ha_discovery = {"error_code": True, "detail": {"message": contract["description"]}}
        #     f.publish(client, f"{pdl}/contract/error", str(1))
        #     for key, value in contract.items():
        #         f.publish(client, f"{pdl}/contract/errorMsg/{key}", str(value))
        # else:
        #     f.publish(client, f"{pdl}/contract/error", str(0))
        #     if "customer" in contract:
        #         customer = contract["customer"]
        #         f.publish(client, f"{pdl}/customer_id", str(customer["customer_id"]))
        #         for usage_points in customer["usage_points"]:
        #             for usage_point_key, usage_point_data in usage_points["usage_point"].items():
        #                 f.publish(client, f"{pdl}/contract/{usage_point_key}", str(usage_point_data))
        #
        #             for contracts_key, contracts_data in usage_points["contracts"].items():
        #                 f.publish(client, f"{pdl}/contract/{contracts_key}", str(contracts_data))
        #
        #                 if contracts_key == "last_distribution_tariff_change_date":
        #                     f.publish(client, f"{pdl}/last_distribution_tariff_change_date", str(contracts_data))
        #                     ha_discovery[pdl]["last_distribution_tariff_change_date"] = str(contracts_data)
        #
        #                 if contracts_key == "last_activation_date":
        #                     f.publish(client, f"{pdl}/last_activation_date", str(contracts_data))
        #                     ha_discovery[pdl]["last_activation_date"] = str(contracts_data)
        #
        #                 if contracts_key == "subscribed_power":
        #                     f.publish(client, f"{pdl}/subscribed_power", str(contracts_data.split()[0]))
        #                     ha_discovery[pdl]["subscribed_power"] = str(contracts_data.split()[0])
        #                     config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
        #                     cur.execute(config_query, [f"{pdl}_subscribed_power", f"{str(contracts_data)}"])
        #                     con.commit()
        #
        #                 offpeak_hours = []
        #                 if pdl_config["offpeak_hours"] != None:
        #                     offpeak_hours = pdl_config["offpeak_hours"].split(";")
        #                 else:
        #                     if contracts_key == "offpeak_hours":
        #                         offpeak_hours = contracts_data[
        #                                         contracts_data.find("(") + 1: contracts_data.find(")")
        #                                         ].split(";")
        #
        #                 if offpeak_hours != [] and offpeak_hours != [""]:
        #                     ha_discovery[pdl]["offpeak_hours"] = offpeak_hours
        #                     index = 0
        #                     for oh in offpeak_hours:
        #                         f.publish(client, f"{pdl}/offpeak_hours/{index}/start", str(oh.split("-")[0]))
        #                         f.publish(client, f"{pdl}/offpeak_hours/{index}/stop", str(oh.split("-")[1]))
        #                         index += 1
        #                     f.publish(client, f"{pdl}/offpeak_hours", str(offpeak_hours))
        #                     offpeak_hours_store = ""
        #                     offpeak_hours_len = len(offpeak_hours)
        #                     i = 1
        #                     for hours in offpeak_hours:
        #                         offpeak_hours_store += f"{hours}"
        #                         if i < offpeak_hours_len:
        #                             offpeak_hours_store += ";"
        #                         i += 1
        #
        #                     # config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
        #                     # cur.execute(config_query, [f"{pdl}_offpeak_hours", f"HC ({str(offpeak_hours_store)})"])
        #                     # con.commit()
        #
        #     else:
        #         ha_discovery = {"error_code": True, "detail": {"message": contract}}
        # return ha_discovery

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

    # logSep()
    # date = datetime.datetime.now() + relativedelta(seconds=CYCLE)
    # log(f"Prochain import : {date}")
    # time.sleep(CYCLE)
