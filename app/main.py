import sys

from flask import Flask, request, send_file
from flask_apscheduler import APScheduler

from config import cycle_minimun
from dependencies import *
from models.config import Config, get_version
from models.jobs import Job
from models.ajax import Ajax
from models.database import Database
from models.influxdb import InfluxDB
from models.log import Log
from models.mqtt import Mqtt
from templates.index import Index
from templates.usage_point_id import UsagePointId

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

DB = Database()
DB.unlock()

LOG.title("Loading configuration...")
for usage_point_id, data in CONFIG.list_usage_point().items():
    LOG.log(f"{usage_point_id}")
    DB.set_usage_point(usage_point_id, data)
    LOG.log("  => Success")

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
    MQTT.connect()

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
        CONFIG.set("wipe_influxdb", False)
        LOG.separator_warning()
        time.sleep(1)

CYCLE = CONFIG.get('cycle')
if CYCLE < cycle_minimun:
    logging.warning("Le cycle minimun est de 3600s")
    CYCLE = cycle_minimun
    CONFIG.set("cycle", cycle_minimun)


class FetchAllDataScheduler(object):
    JOBS = [
        {
            # "id": f"fetch_data_boot",
            # "func": Job().job_import_data
        # }, {
            "id": f"fetch_data",
            "func": Job().job_import_data,
            "trigger": "interval",
            "seconds": CYCLE,
        }
    ]
    SCHEDULER_API_ENABLED = True


logging.basicConfig(format='%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s')

if __name__ == '__main__':
    APP = Flask(__name__)
    APP.config.from_object(FetchAllDataScheduler())
    scheduler = APScheduler()
    scheduler.init_app(APP)
    scheduler.start()


    # ------------------------------------------------------------------------------------------------------------------
    # HTML RETURN
    # ------------------------------------------------------------------------------------------------------------------
    @APP.route("/status")
    @APP.route("/status/")
    @APP.route("/ping")
    @APP.route("/ping/")
    def status():
        return "ok"


    @APP.route("/favicon.ico")
    def favicon():
        return send_file("static/favicon.ico", mimetype='image/gif')


    @APP.route("/", methods=['GET'])
    def main():
        return Index().display()


    @APP.route('/usage_point_id/<usage_point_id>', methods=['GET'])
    @APP.route('/usage_point_id/<usage_point_id>/', methods=['GET'])
    def usage_point_id(usage_point_id):
        return UsagePointId(usage_point_id).display()


    # ------------------------------------------------------------------------------------------------------------------
    # BACKGROUND HTML TASK (AJAX)
    # ------------------------------------------------------------------------------------------------------------------

    @APP.route("/lock_status", methods=['GET'])
    @APP.route("/lock_status/", methods=['GET'])
    def lock():
        return str(DB.lock_status())

    @APP.route("/gateway_status", methods=['GET'])
    @APP.route("/gateway_status/", methods=['GET'])
    def gateway_status():
        return Ajax().gateway_status()


    @APP.route("/configuration/<usage_point_id>", methods=['POST'])
    @APP.route("/configuration/<usage_point_id>/", methods=['POST'])
    def configuration(usage_point_id):
        return Ajax(usage_point_id).configuration(request.form)


    @APP.route("/new_account", methods=['POST'])
    @APP.route("/new_account/", methods=['POST'])
    def new_account():
        return Ajax().new_account(request.form)


    @APP.route("/account_status/<usage_point_id>", methods=['GET'])
    @APP.route("/account_status/<usage_point_id>/", methods=['GET'])
    def account_status(usage_point_id):
        return Ajax(usage_point_id).account_status()


    @APP.route("/import/<usage_point_id>", methods=['GET'])
    @APP.route("/import/<usage_point_id>/", methods=['GET'])
    def import_all_data(usage_point_id):
        return Ajax(usage_point_id).import_data()

    @APP.route("/import/<usage_point_id>/<target>", methods=['GET'])
    @APP.route("/import/<usage_point_id>/<target>", methods=['GET'])
    def import_data(usage_point_id, target):
        return Ajax(usage_point_id).import_data(target)


    @APP.route("/reset/<usage_point_id>", methods=['GET'])
    @APP.route("/reset/<usage_point_id>/", methods=['GET'])
    def reset_all_data(usage_point_id):
        return Ajax(usage_point_id).reset_all_data()


    @APP.route("/usage_point_id/<usage_point_id>/<target>/reset/<date>", methods=['GET'])
    @APP.route("/usage_point_id/<usage_point_id>/<target>/reset/<date>/", methods=['GET'])
    def reset_data(usage_point_id, target, date):
        return Ajax(usage_point_id).reset_data(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/blacklist/<date>", methods=['GET'])
    @APP.route("/usage_point_id/<usage_point_id>/<target>/blacklist/<date>/", methods=['GET'])
    def blacklist_data(usage_point_id, target, date):
        return Ajax(usage_point_id).blacklist(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/whitelist/<date>", methods=['GET'])
    @APP.route("/usage_point_id/<usage_point_id>/<target>/whitelist/<date>/", methods=['GET'])
    def whitelist_data(usage_point_id, target, date):
        return Ajax(usage_point_id).whitelist(target, date)


    @APP.route("/usage_point_id/<usage_point_id>/<target>/import/<date>", methods=['GET'])
    @APP.route("/usage_point_id/<usage_point_id>/<target>/import/<date>/", methods=['GET'])
    def fetch_data(usage_point_id, target, date):
        return Ajax(usage_point_id).fetch(target, date)


    APP.run(host="0.0.0.0", port=5000, debug=False, use_reloader=True)
