import json
from dateutil.relativedelta import *

from importlib import import_module

main = import_module("main")
f = import_module("function")


def haAutodiscovery(client, type="Sensor", pdl=None, name=None, value=None, attributes=None, unit_of_meas=None,
                    device_class=None,
                    state_class=None):
    name = name.replace("-", "_")
    config = {
        "name": f"enedisgateway_{pdl}_{name}",
        "uniq_id": f"enedisgateway.{pdl}_{name}",
        "stat_t": f"{main.config['home_assistant']['discovery_prefix']}/{type}/enedisgateway/{pdl}_{name}/state",
        "json_attr_t": f"{main.config['home_assistant']['discovery_prefix']}/{type}/enedisgateway/{pdl}_{name}/attributes",
        "device": {
            "identifiers": [f"linky_{pdl}"],
            "name": f"Linky {pdl}",
            "model": "Linky",
            "manufacturer": "Enedis"
        }
    }
    if unit_of_meas is not None:
        config['unit_of_meas'] = str(unit_of_meas)
    if device_class is not None:
        config['device_class'] = str(device_class)
    if state_class is not None:
        config['state_class'] = str(state_class)

    f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/config", json.dumps(config), main.config['home_assistant']['discovery_prefix'])
    if attributes is not None:
        f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/attributes", json.dumps(attributes),
                  main.config['home_assistant']['discovery_prefix'])
    f.publish(client, f"{type}/enedisgateway/{pdl}_{name}/state", str(value), main.config['home_assistant']['discovery_prefix'])
