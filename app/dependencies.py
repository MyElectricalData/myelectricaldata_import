import logging
import os
import sys

from jinja2 import Template

from config import *

def debug(message):
    logWarn()
    if type(message) is list:
        for msg in message:
            logging.debug(f" {msg}")
    else:
        logging.debug(f" {message}")
    logWarn()

def log(message):
    if type(message) is list:
        for msg in message:
            logging.info(f" {msg}")
    else:
        logging.info(f" {message}")


def logTitle(message):
    logSep()
    logging.info(f" {message.upper()}")
    logSep()


def logDebug(message):
    if type(message) is list:
        for msg in message:
            logging.debug(f" {msg}")
    else:
        logging.debug(f" {message}")


def logWarning(message):
    if type(message) is list:
        for msg in message:
            logging.warning(f" {msg}")
    else:
        logging.warning(f" {message}")


def logError(message):
    logging.error("═════════════════════════════════•°• :ERREUR: •°•══════════════════════════════════")
    logging.error("")
    if type(message) is list:
        for msg in message:
            logging.error(f" {msg}")
    else:
        logging.error(f" {message}")
    logging.error("")
    logging.error("═══════════════════════════════════════════════════════════════════════════════════")


def logCritical(message):
    if type(message) is list:
        for msg in message:
            logging.critical(f" {msg}")
    else:
        logging.critical(f" {message}")
    sys.exit()


def logSep():
    logging.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ ❖ ◦ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def logWarn():
    logging.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ▲ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")


def logo(version):
    logSep()
    logging.info("#  __  __       ______ _           _        _           _ _____        _          #")
    logging.info("# |  \/  |     |  ____| |         | |      (_)         | |  __ \      | |         #")
    logging.info("# | \  / |_   _| |__  | | ___  ___| |_ _ __ _  ___ __ _| | |  | | __ _| |_ __ _   #")
    logging.info("# | |\/| | | | |  __| | |/ _ \/ __| __| '__| |/ __/ _` | | |  | |/ _` | __/ _` |  #")
    logging.info("# | |  | | |_| | |____| |  __/ (__| |_| |  | | (_| (_| | | |__| | (_| | || (_| |  #")
    logging.info("# |_|  |_|\__, |______|_|\___|\___|\__|_|  |_|\___\__,_|_|_____/ \__,_|\__\__,_|  #")
    logging.info("#          __/ |                                                                  #")
    logging.info("#         |___/                                                                   #")
    logSep()
    logging.info(f"                            VERSION : {version}")


if os.environ.get("APPLICATION_PATH") is None:
    APPLICATION_PATH = "/app"
else:
    APPLICATION_PATH = os.environ.get('APPLICATION_PATH')


def html_return(body, url="/import/0"):
    links = ["Forcer l'importation"]
    footer = ""
    for i, comment in enumerate(links):
        footer += f"""
            <div id="bouton_enedis" style="">
                <a style="text-decoration: none" href="{url}"><div class="btn">{comment}</div></a>
            </div>
        """

    with open(f'{APPLICATION_PATH}/html/footer.html') as file_:
        footer_template = Template(file_.read())
    footer = footer_template.render(footer=footer)

    with open(f'{APPLICATION_PATH}/html/index.html') as file_:
        index_template = Template(file_.read())

    html = index_template.render(
        body=body,
        fullscreen=True,
        footer=footer,
        homepage_link="/",
        footer_height=80,
        concent_url=f'{URL}',
        swagger_url=f"{URL}/docs/",
        redoc_url=f"{URL}/redoc/",
        faq_url=f"{URL}/faq/",
        code_url=f"{URL}/error_code/",
        doc_url=f"{URL}/documentation/",
    )
    return html


paypal_footer = """
<div style="text-align: center" id="paypal" class="paypal_link">
    <form action="https://www.paypal.com/donate" method="post" target="_top" style="height: 30px;" id="paypal_form">
        <input type="hidden" name="business" value="FY25JLXDYLXAJ" />
        <input type="hidden" name="no_recurring" value="0" />
        <input type="hidden" name="currency_code" value="EUR" />
        <input type="image" id="paypal_img"
               src="/static/paypal.png"
               border="0"
               name="submit"
               title="PayPal - The safer, easier way to pay online!"
               alt="Bouton Faites un don avec PayPal"/>
        <img alt="" border="0" src="https://www.paypal.com/fr_FR/i/scr/pixel.gif" width="1" height="1" />
    </form>
    Le service est gratuit, mais si tu souhaites soutenir le projet (serveur & domaine).
</div>
"""

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
