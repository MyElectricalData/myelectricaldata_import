import json
import threading
import time

from flask import Flask

from config import cycle_minimun
from dependencies import *
from models.ajax import Ajax
from models.cache import Cache
from models.config import Config, get_version
from models.html import Html
from models.influxdb import InfluxDB
from models.log import Log
from models.mqtt import Mqtt

LOG = Log()

if "APPLICATION_PATH_DATA" in os.environ:
    APPLICATION_PATH_DATA = os.getenv("APPLICATION_PATH_DATA")
else:
    APPLICATION_PATH_DATA = "/data"
CONFIG = Config(
    path=APPLICATION_PATH_DATA
)
CONFIG.load()

LOG.logo(get_version())

CONFIG.display()
CONFIG.check()

CACHE = Cache()
CACHE.unlock()

if CONFIG.get("wipe_cache"):
    CACHE.purge_cache()
    CONFIG.set("wipe_cache", False)
    LOG.warning()

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
        LOG.separator_warning()

CYCLE = CONFIG.get('cycle')
if CYCLE < cycle_minimun:
    logging.warning("Le cycle minimun est de 3600s")
    CYCLE = cycle_minimun
    CONFIG.set("cycle", cycle_minimun)

if __name__ == '__main__':

    APP = Flask(__name__,
                static_url_path='/static',
                static_folder='html/static', )
    threading.Thread(target=lambda: APP.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)).start()

    # ------------------------------------------------------------------------------------------------------------------
    # HTML RETURN
    # ------------------------------------------------------------------------------------------------------------------

    @APP.route("/status")
    @APP.route("/status/")
    @APP.route("/ping")
    @APP.route("/ping/")
    def status():
        return "ok"


    @APP.route("/")
    def main():
        return Html().page_index()


    @APP.route('/usage_point_id/<usage_point_id>', methods=['GET'])
    @APP.route('/usage_point_id/<usage_point_id>/', methods=['GET'])
    def usage_point_id(usage_point_id):
        return Html(usage_point_id).page_usage_point_id()

    # ------------------------------------------------------------------------------------------------------------------
    # BACKGROUND HTML TASK (AJAX)
    # ------------------------------------------------------------------------------------------------------------------

    @APP.route("/import/<usage_point_id>")
    @APP.route("/import/<usage_point_id>/")
    def import_data(usage_point_id):
        return Ajax(usage_point_id).import_data()


    @APP.route("/usage_point_id/<usage_point_id>/<target>/reset/<date>")
    @APP.route("/usage_point_id/<usage_point_id>/<target>/reset/<date>/")
    def reset_data(usage_point_id, target, date):
        return Ajax(usage_point_id).reset_data(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/blacklist/<date>")
    @APP.route("/usage_point_id/<usage_point_id>/<target>/blacklist/<date>/")
    def blacklist_data(usage_point_id, target, date):
        return Ajax(usage_point_id).blacklist(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/whitelist/<date>")
    @APP.route("/usage_point_id/<usage_point_id>/<target>/whitelist/<date>/")
    def whitelist_data(usage_point_id, target, date):
        return Ajax(usage_point_id).reset_data(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/import/<date>")
    @APP.route("/usage_point_id/<usage_point_id>/<target>/import/<date>/")
    def fetch_data(usage_point_id, target, date):
        return Ajax(usage_point_id).fetch(target, date)


    while True:
        get_data()
        time.sleep(CYCLE)
