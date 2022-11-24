import datetime
import json
import logging
import os
import sys
import time

if os.environ.get("APPLICATION_PATH") is None:
    APPLICATION_PATH = "/app"
else:
    APPLICATION_PATH = os.environ.get('APPLICATION_PATH')

paypal_footer = """
<div style="text-align: center" id="paypal" class="paypal_link">
    <form action="https://www.paypal.com/donate" method="post" target="_top" style="height: 55px;" id="paypal_form">
        <input type="hidden" name="business" value="FY25JLXDYLXAJ" />
        <input type="hidden" name="no_recurring" value="0" />
        <input type="hidden" name="currency_code" value="EUR" />
        <input type="image" id="paypal_img"
               src="/static/img/paypal.png"
               border="0"
               name="submit"
               title="PayPal - The safer, easier way to pay online!"
               alt="Bouton Faites un don avec PayPal"/>
        <img alt="" border="0" src="https://www.paypal.com/fr_FR/i/scr/pixel.gif" width="1" height="1" />
    </form>
    Le service est gratuit, mais si tu souhaites soutenir le projet (serveur & domaine).
</div>
"""


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def str2bool(v):
    if type(v) != bool:
        return v.lower() in ("yes", "true", "t", "1")
    else:
        return v


def is_float(element):
    try:
        float(element)
        return True
    except ValueError:
        return False


def reformat_json(yaml):
    result = {}
    for key, value in yaml.items():
        if value in ["true", "false"]:
            result[key] = str2bool(value)
        elif type(value) == dict:
            result[key] = value
        elif not isinstance(value, bool) and is_float(value):
            result[key] = float(value)
        else:
            result[key] = value
    return result