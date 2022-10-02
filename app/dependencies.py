from models.log import *


# import requests
# from paho.mqtt import client as mqtt_client
# from datetime import datetime
# import json
# from pprint import pprint

# def connect_mqtt():
#     log("MQTT Connect")
#     try:
#         client = mqtt_client.Client(main.config["mqtt"]["client_id"])
#         if main.config["mqtt"]["username"] != "" and main.config["mqtt"]["password"] != "":
#             client.username_pw_set(main.config["mqtt"]["username"], main.config["mqtt"]["password"])
#         client.connect(main.config["mqtt"]["host"], main.config["mqtt"]["port"])
#         log(" => Connected to MQTT Broker!")
#         return client
#     except Exception as e:
#         print(e)
#         log(f"Failed to connect to MQTT Broker")
#         log(f" => Check your MQTT Configuration", "CRITICAL")
#
#
# def publish(client, topic, msg, prefix=None):
#     if prefix == None:
#         prefix = main.config["mqtt"]['prefix']
#     msg_count = 0
#     result = client.publish(f'{prefix}/{topic}', str(msg), qos=main.config["mqtt"]["qos"],
#                             retain=main.config["mqtt"]["retain"])
#     status = result[0]
#     if status == 0:
#         log(f" MQTT Send : {prefix}/{topic} => {msg}", "debug")
#     else:
#         log(f" - Failed to send message to topic {prefix}/{topic}")
#     msg_count += 1
#
#
# def subscribe(client, topic, prefix=None):
#     if prefix == None:
#         prefix = main.config["mqtt"]['prefix']
#
#     def on_message(client, userdata, msg):
#         print(f" MQTT Received : `{prefix}/{topic}` => `{msg.payload.decode()}`")
#
#     sub_topic = f"{prefix}/{topic}"
#     client.subscribe(client, sub_topic)
#     client.on_message = on_message


def logo(version):
    logSep()
    log("__  __       ______ _           _        _           _ _____        _")
    log("|  \/  |     |  ____| |         | |      (_)         | |  __ \      | |")
    log("| \  / |_   _| |__  | | ___  ___| |_ _ __ _  ___ __ _| | |  | | __ _| |_ __ _")
    log("| |\/| | | | |  __| | |/ _ \/ __| __| '__| |/ __/ _` | | |  | |/ _` | __/ _` |")
    log("| |  | | |_| | |____| |  __/ (__| |_| |  | | (_| (_| | | |__| | (_| | || (_| |")
    log("|_|  |_|\__, |______|_|\___|\___|\__|_|  |_|\___\__,_|_|_____/ \__,_|\__\__,_|")
    log("         __/ |")
    log("        |___/")
    logSep()
    log(f"                           VERSION : {version}")
    logSep()




# def is_json(myjson):
#     try:
#         json.loads(myjson)
#     except ValueError as e:
#         return False
#     return True
#
#
# def splitLog(msg):
#     format_log = ""
#     i = 1
#     nb_col = 12
#     msg_length = len(msg)
#     cur_length = 1
#     for log_msg in msg:
#         format_log += f" | {log_msg}"
#         if i == nb_col:
#             i = 1
#             format_log += f" |"
#             log(format_log)
#             format_log = ""
#         elif cur_length == msg_length:
#             format_log += f" |"
#             log(format_log)
#         else:
#             i = i + 1
#         cur_length = cur_length + 1
#
#
# def apiRequest(cur, con, pdl, type="POST", url=None, headers=None, data=None):
#     config_query = f"SELECT * FROM config WHERE key = 'config'"
#     cur.execute(config_query)
#     query_result = cur.fetchall()
#     query_result = json.loads(query_result[0][1])
#     if not f"call_nb_{pdl}" in query_result:
#         query_result[f"call_nb_{pdl}"] = 0
#
#     log(f"call_number : {query_result[f'call_nb_{pdl}']} (max : {query_result['max_call']})", "DEBUG")
#     if query_result["day"] == datetime.now().strftime('%Y-%m-%d'):
#         if query_result[f"call_nb_{pdl}"] > query_result["max_call"]:
#             return {
#                 "error_code": 2,
#                 "description": f"API Call number per day is reached ({query_result['max_call']}), please wait until tomorrow to load the rest of data"
#             }
#         else:
#             query_result[f"call_nb_{pdl}"] = int(query_result[f"call_nb_{pdl}"]) + 1
#             query_result["day"] = datetime.now().strftime('%Y-%m-%d')
#     else:
#         query_result[f"call_nb_{pdl}"] = 0
#         query_result["day"] = datetime.now().strftime('%Y-%m-%d')
#
#     query = f"UPDATE config SET key = 'config', value = '{json.dumps(query_result)}' WHERE key = 'config'"
#     cur.execute(query)
#     con.commit()
#
#     log(f"Call API : {url}", "DEBUG")
#     log(f"Data : {data}", "DEBUG")
#     try:
#         retour = requests.request(type, url=f"{url}", timeout=240, headers=headers, data=data)
#
#         if retour.status_code != 200:
#             retour = {
#                 "error_code": retour.status_code,
#                 "description": retour.text
#             }
#         else:
#             if is_json(str(retour.text)):
#                 retour = retour.json()
#             else:
#                 retour = {
#                     "error_code": 500,
#                     "description": "Enedis return is not json"
#                 }
#     except requests.exceptions.Timeout:
#         log(" !! Query Timeout !!")
#         retour = {
#             "error_code": "timeout",
#             "description": "Query Timeout"
#         }
#     except requests.exceptions.TooManyRedirects:
#         log(" !! Too Many Redirection !!")
#         retour = {
#             "error_code": "TooManyRedirects",
#             "description": "TooManyRedirects"
#         }
#     except requests.exceptions.RequestException as e:
#         log(" !! Critical error !!")
#         retour = {
#             "error_code": "RequestException",
#             "description": "RequestException",
#             "exception": e
#         }
#
#     if "debug" in main.config and main.config["debug"] == True:
#         log(f"API Return :", "ERROR")
#         log(retour, "ERROR")
#
#     return retour
