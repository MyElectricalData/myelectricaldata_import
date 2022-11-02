import json
from importlib import import_module
from pprint import pprint

from dateutil.relativedelta import *

main = import_module("main")
f = import_module("function")


def haAutodiscovery(client, config, type="Sensor", pdl=None, name=None, value=None, attributes=None, unit_of_meas=None,
                    device_class=None,
                    state_class=None):
    name = name.replace("-", "_")

    ha_config = {
        "name": f"enedisgateway_{pdl}_{name}",
        "uniq_id": f"enedisgateway.{pdl}_{name}",
        "stat_t": f"{config['home_assistant']['discovery_prefix']}/{type}/enedisgateway/{pdl}_{name}/state",
        "json_attr_t": f"{config['home_assistant']['discovery_prefix']}/{type}/enedisgateway/{pdl}_{name}/attributes",
        "device": {
            "identifiers": [f"linky_{pdl}"],
            "name": f"Linky {pdl}",
            "model": "Linky",
            "manufacturer": "Enedis"
        }
    }
    if unit_of_meas is not None:
        ha_config['unit_of_meas'] = str(unit_of_meas)
    if device_class is not None:
        ha_config['device_class'] = str(device_class)
    if state_class is not None:
        ha_config['state_class'] = str(state_class)

    f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/config", json.dumps(ha_config), config['home_assistant']['discovery_prefix'])
    if attributes is not None:
        f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/attributes", json.dumps(attributes),
                  config['home_assistant']['discovery_prefix'])
    f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/state", str(value), config['home_assistant']['discovery_prefix'])
