import datetime
import logging
import os
import sys

import __main__ as app
from models.log import Log
from models.config import get_version
from models.query_status import Status
from models.query_contract import Contract
from models.query_address import Address
from models.query_consumption_daily import ConsumptionDaily
from models.query_consumption_detail import ConsumptionDetail
from models.query_production_daily import ProductionDaily
from models.query_production_detail import ProductionDetail


if os.environ.get("APPLICATION_PATH") is None:
    APPLICATION_PATH = "/app"
else:
    APPLICATION_PATH = os.environ.get('APPLICATION_PATH')

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


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


def get_data():
    if not app.CACHE.lock_status():
        app.CACHE.lock()
        for usage_point_id, config in app.CONFIG.get('myelectricaldata').items():
            app.CACHE.save_config(usage_point_id, config)
            app.LOG.log_usage_point_id(usage_point_id)
            result = {}

            headers = {
                'Content-Type': 'application/json',
                'Authorization': config['token'],
                'call-service': "myelectricaldata",
                'version': get_version()
            }

            app.LOG.title(f"[{usage_point_id}] Status de la passerelle :")
            result["status_gateway"] = Status(
                headers=headers,
            ).ping()

            app.LOG.title(f"[{usage_point_id}] Check account status :")
            result["status_account"] = Status(
                headers=headers,
            ).status(usage_point_id=usage_point_id)

            app.LOG.title(f"[{usage_point_id}] Récupération du contrat :")
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

            app.LOG.title(f"[{usage_point_id}] Récupération de coordonnée :")
            result["addresses"] = Address(
                headers=headers,
                usage_point_id=usage_point_id,
                config=config
            ).get()

            if config["consumption"]:
                app.LOG.title(f"[{usage_point_id}] Récupération de la consommation journalière :")
                result["consumption_daily"] = ConsumptionDaily(
                    headers=headers,
                    usage_point_id=usage_point_id,
                    config=config,
                    activation_date=activation_date,
                ).get()

            if config["consumption_detail"]:
                app.LOG.title(f"[{usage_point_id}] Récupération de la consommation détaillé :")
                result["consumption_detail"] = ConsumptionDetail(
                    headers=headers,
                    usage_point_id=usage_point_id,
                    config=config,
                    activation_date=activation_date,
                    offpeak_hours=offpeak_hours
                ).get()

            if config["production"]:
                app.LOG.title(f"[{usage_point_id}] Récupération de la production journalière :")
                result["production_daily"] = ProductionDaily(
                    headers=headers,
                    usage_point_id=usage_point_id,
                    config=config,
                    activation_date=activation_date,
                ).get()

            if config["production_detail"]:
                app.LOG.title(f"[{usage_point_id}] Récupération de la production détaillé :")
                result["production_detail"] = ProductionDetail(
                    headers=headers,
                    usage_point_id=usage_point_id,
                    config=config,
                    activation_date=activation_date,
                    offpeak_hours=offpeak_hours
                ).get()
        app.CACHE.unlock()
        app.LOG.finish()
    else:
        app.LOG.warning("Skip, import in progress!!")
