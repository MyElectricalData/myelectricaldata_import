import ast
import json
import logging
from datetime import datetime, timedelta

import markdown
from jinja2 import Template
from mergedeep import Strategy, merge

from dependencies import APPLICATION_PATH, get_version
from init import CONFIG, DB
from models.stat import Stat
from templates.models.configuration import Configuration
from templates.models.menu import Menu
from templates.models.sidemenu import SideMenu
from templates.models.usage_point_select import UsagePointSelect


class UsagePoint:
    def __init__(self, usage_point_id):
        # if not DB.lock_status():
        self.config = CONFIG
        self.db = DB
        self.db.refresh_object()
        self.application_path = APPLICATION_PATH
        self.usage_point_id = usage_point_id
        self.current_years = int(datetime.now().strftime("%Y"))
        self.max_history = 4
        self.max_history_chart = 6
        if self.usage_point_id is not None:
            self.usage_point_config = self.db.get_usage_point(self.usage_point_id)
            if hasattr(self.usage_point_config, "token"):
                self.headers = {
                    "Content-Type": "application/json",
                    "Authorization": self.usage_point_config.token,
                    "call-service": "myelectricaldata",
                    "version": get_version(),
                }
            else:
                self.headers = None
        self.usage_point_select = UsagePointSelect(self.config, self.db, usage_point_id)
        self.side_menu = SideMenu()
        menu = {}
        menu = merge(
            {
                "import_data": {
                    "title": "Importer les données depuis Enedis",
                    "icon": "file_download",
                    "css": "background-color: var(--sde-bg-color);",
                    "loading_page": "loading_import",
                    "ajax": {"method": "GET", "url": f"/import/{self.usage_point_id}"},
                }
            },
            menu,
            strategy=Strategy.ADDITIVE,
        )
        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
            menu = merge(
                {
                    "import_daily": {
                        "title": "Importer la consommation journalière",
                        "icon": "electric_bolt",
                        "css": "background-color: var(--text-color);",
                        "loading_page": "loading_import",
                        "ajax": {
                            "method": "GET",
                            "url": f"/import/{self.usage_point_id}/consumption",
                        },
                    }
                },
                menu,
                strategy=Strategy.ADDITIVE,
            )
        if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
            menu = merge(
                {
                    "import_detail": {
                        "title": "Importer la consommation détaillée",
                        "icon": "electric_bolt",
                        "css": "background-color: #f39c12;",
                        "loading_page": "loading_import",
                        "ajax": {
                            "method": "GET",
                            "url": f"/import/{self.usage_point_id}/consumption_detail",
                        },
                    }
                },
                menu,
                strategy=Strategy.ADDITIVE,
            )
        if hasattr(self.usage_point_config, "consumption_max_power") and self.usage_point_config.consumption_max_power:
            menu = merge(
                {
                    "import_daily_max_power": {
                        "title": "Importer la puissance maximum journalière.",
                        "icon": "offline_bolt",
                        "css": "background-color: #e74c3c;",
                        "loading_page": "loading_import",
                        "ajax": {
                            "method": "GET",
                            "url": f"/import/{self.usage_point_id}/consumption_max_power",
                        },
                    }
                },
                menu,
                strategy=Strategy.ADDITIVE,
            )
        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
            menu = merge(
                {
                    "import_production_daily": {
                        "title": "Importer la production journalière",
                        "icon": "solar_power",
                        "css": "background-color: #F1C40F;",
                        "loading_page": "loading_import",
                        "ajax": {
                            "method": "GET",
                            "url": f"/import/{self.usage_point_id}/production",
                        },
                    }
                },
                menu,
                strategy=Strategy.ADDITIVE,
            )
        if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
            menu = merge(
                {
                    "import_production_detail": {
                        "title": "Importer la production détaillée",
                        "icon": "solar_power",
                        "css": "background-color: #f39c12;",
                        "loading_page": "loading_import",
                        "ajax": {
                            "method": "GET",
                            "url": f"/import/{self.usage_point_id}/production_detail",
                        },
                    }
                },
                menu,
                strategy=Strategy.ADDITIVE,
            )
        menu = merge(
            {
                "delete_data": {
                    "title": "Supprimer le cache local",
                    "icon": "delete",
                    "css": "background-color: var(--text-warning);",
                    "loading_page": "loading",
                    "ajax": {"method": "GET", "url": f"/delete/{self.usage_point_id}"},
                },
                "delete_data_gateway": {
                    "title": "Supprimer le cache de la passerelle",
                    "icon": "delete_forever",
                    "css": "background-color: var(--text-warning);",
                    "loading_page": "loading_import",
                    "ajax": {
                        "method": "GET",
                        "url": f"/reset_gateway/{self.usage_point_id}",
                    },
                },
                "config_data": {
                    "title": "Configuration",
                    "css": "background-color: var(--success-bg);",
                    "icon": "settings_applications",
                },
            },
            menu,
            strategy=Strategy.ADDITIVE,
        )
        self.menu = Menu(menu)
        self.configuration_div = Configuration(
            self.db,
            f"Modification du point de livraison {self.usage_point_id}",
            self.usage_point_id,
        )
        self.contract = self.db.get_contract(self.usage_point_id)
        self.address = self.db.get_addresse(self.usage_point_id)
        self.javascript = ""
        self.recap_consumption_data = {}
        self.recap_consumption_price = {}
        self.recap_consumption_max_power = {}
        self.recap_production_data = {}
        self.recap_production_price = {}
        self.recap_hc_hp = "Pas de données."

    def display(self):
        # if self.db.lock_status():
        #     return Loading().display()
        # else:
        if self.headers is None:
            self.javascript = "window.location.href = '/';"
            with open(f"{self.application_path}/templates/html/usage_point_id.html") as file_:
                index_template = Template(file_.read())
            html = index_template.render(
                select_usage_points=self.usage_point_select.html(),
                javascript_loader=open(f"{self.application_path}/templates/html/head.html").read(),
                side_menu=self.side_menu.html(),
                javascript=self.javascript,
                # configuration=self.configuration_div.html().strip(),
                menu=self.menu.html(),
                css=self.menu.css(),
            )
            return html
        else:
            address = self.get_address()
            if address is None:
                address = "Inconnue"
            if hasattr(self.usage_point_config, "name"):
                title = f"{self.usage_point_id} - {self.usage_point_config.name}"
            else:
                title = address

            with open(f"{self.application_path}/templates/md/usage_point_id.md") as file_:
                homepage_template = Template(file_.read())
            body = homepage_template.render(
                title=title,
                address=address,
                contract_data=self.contract_data(),
                address_data=address,
            )
            body = markdown.markdown(body, extensions=["fenced_code", "codehilite"])
            body += self.offpeak_hours_table()

            # TEMPO
            tempo_config = None
            if self.usage_point_config.plan == "Tempo":
                tempo_config = self.db.get_tempo_config("price")
                body += "<h1>Tempo</h1>"
                today = datetime.combine(datetime.now(), datetime.min.time())
                tomorow = datetime.combine(datetime.now() + timedelta(days=1), datetime.min.time())
                tempo = self.db.get_tempo_range(today, tomorow, "asc")
                if tempo_config:
                    body += f"""
                    <table style="width:100%" class="table_recap">
                        <tr>
                            <td style="width:50%; text-align: center">Aujourd'hui <br> {today.strftime("%d-%m-%Y")}</td>
                            <td style="width:50%; text-align: center">Demain <br> {tomorow.strftime("%d-%m-%Y")}</td>
                        </tr>
                        <tr>"""
                    tempo_template = {
                        "?": {
                            "color": "background-color: #000000",
                            "text_color": "color: #FFFFFF",
                            "text": "En attente...",
                        },
                        "RED": {
                            "color": "background-color: #E74C3C",
                            "text_color": "color: #ECF0F1",
                            "text": f"""Rouge<br>
                            06h00 -> 22h00 = {tempo_config['red_hp']}€ / kWh<br>
                            22h00 -> 06h00 = {tempo_config['red_hc']}€ / kWh<br>
                            """,
                        },
                        "WHITE": {
                            "color": "background-color: #ECF0F1",
                            "text_color": "color: #34495E",
                            "text": f"""Blanc<br>
                            06h00 -> 22h00 = {tempo_config['white_hp']}€ / kWh<br>
                            22h00 -> 06h00 = {tempo_config['white_hc']}€ / kWh
                            """,
                        },
                        "BLUE": {
                            "color": "background-color: #3498DB",
                            "text_color": "color: #ECF0F1",
                            "text": f"""Bleu<br>
                            06h00 -> 22h00 = {tempo_config['blue_hp']}€ / kWh<br>
                            22h00 -> 06h00 = {tempo_config['blue_hc']}€ / kWh
                            """,
                        },
                    }
                    if len(tempo) > 0:
                        color = tempo[0].color
                    else:
                        color = "?"
                    body += f"""<td style="width:50%; text-align: center; {tempo_template[color]["color"]};{tempo_template[color]["text_color"]}">{tempo_template[color]["text"]}</td>"""
                    if len(tempo) > 1:
                        color = tempo[1].color
                    else:
                        color = "?"
                    body += f"""<td style="width:50%; text-align: center; {tempo_template[color]["color"]};{tempo_template[color]["text_color"]}">{tempo_template[color]["text"]}</td>"""
                    body += """</tr>
                    </table>
                    """

            body += "<h1>Récapitulatif</h1>"
            # RECAP CONSUMPTION
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                self.generate_data("consumption")
                self.consumption()
                # recap_consumption = self.recap(data=self.recap_consumption_data)
                recap_consumption = self.recapv2()
                body += "<h2>Consommation</h2>"
                body += str(recap_consumption)
                body += '<div id="chart_daily_consumption"></div>'

            # RATIO HP/HC
            if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
                self.generate_chart_hc_hp()
                body += "<h2>Ratio HC/HP</h2>"
                body += "<table class='table_hchp'><tr>"
                body += str(self.recap_hc_hp)
                body += "</tr></table>"

            # TARIFICATION
            body += "<h2>Comparatif abonnements</h2>"
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                datatable = str(self.get_price("consumption"))
                if datatable:
                    lien_tempo = "https://particulier.edf.fr/fr/accueil/gestion-contrat/options/tempo/details.html"
                    body += (
                        "Ce tableau à pour but de vous aider à choisir le forfait le plus adapté à votre mode "
                        "de consommation.<br><br>"
                    )
                    body += datatable
                    if tempo_config and "enable" in tempo_config and tempo_config["enable"]:
                        body += (
                            "<br>Le forfait Tempo (uniquement disponible chez EDF) est soumis à une "
                            "tarification à 6 niveaux avec un prix du kWh très élévé 22j dans l'années. "
                            "Généralement lorsque le réseau électrique est tendu ou les jours les plus froids "
                            f"de l'années. Tout est expliqué <a href='{lien_tempo}'>ici</a>.<br>"
                        )
                    body += (
                        "<br><code>Les prix indiqué sont approximatif et ne tiennent pas compte du prix de "
                        "l'abonnement mensuel.</code>"
                    )
                else:
                    body += "Pas de données."

            # RECAP PRODUCTION
            if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                self.generate_data("production")
                self.production()
                recap_production = self.recap(data=self.recap_production_data)
                body += "<h2>Production</h2>"
                body += str(recap_production)
                body += '<div id="chart_daily_production"></div>'

            # RECAP CONSUMPTION VS PRODUCTION
            if (
                hasattr(self.usage_point_config, "consumption")
                and self.usage_point_config.consumption
                and hasattr(self.usage_point_config, "production")
                and self.usage_point_config.production
            ):
                body += "<h2>Consommation VS Production</h2>"
                for year, data in self.recap_consumption_data.items():
                    if data["value"] != 0:
                        # body += f'<div><h3>{year}</h3></div>'
                        # body += f'<div>{self.consumption_vs_production(year)}</div>'
                        self.consumption_vs_production(year)
                        body += f'<div id="chart_daily_production_compare_{year}"></div>'

            body += "<h1>Mes données</h1>"
            # CONSUMPTION DATATABLE
            if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
                body += "<h2>Consommation</h2>"
                body += "<h3>Journalière</h2>"
                body += """
                <table id="dataTableConsommation" class="display">
                    <thead>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Consommation (Wh)</th>
                            <th class="title">Consommation (kWh)</th>
                            <th class="title">HC (kWh)</th>
                            <th class="title">HP (kWh)</th>
                            <th class="title">Tempo</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Consommation (Wh)</th>
                            <th class="title">Consommation (kWh)</th>
                            <th class="title">HC (kWh)</th>
                            <th class="title">HP (kWh)</th>
                            <th class="title">Tempo</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </tfoot>
                </table>
                """
            if hasattr(self.usage_point_config, "consumption_detail") and self.usage_point_config.consumption_detail:
                body += "<h3>Horaires</h2>"
                body += "<ul><li>Quand vous videz le cache d'une tranche horaire, vous supprimez la totalité du cache de la journée.</li></ul>"
                body += """
                <table id="dataTableConsommationDetail" class="display">
                    <thead>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Horaire</th>
                            <th class="title">Consommation (Wh)</th>
                            <th class="title">Consommation (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Horaire</th>
                            <th class="title">Consommation (Wh)</th>
                            <th class="title">Consommation (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </tfoot>
                </table>
                """
            # MAX POWER DATATABLE
            if (
                hasattr(self.usage_point_config, "consumption_max_power")
                and self.usage_point_config.consumption_max_power
            ):
                body += "<h2>Puissance Maximale</h2>"
                if hasattr(self.contract, "subscribed_power") and self.contract.subscribed_power is not None:
                    max_power = self.contract.subscribed_power.split(" ")[0]
                else:
                    max_power = 0
                body += f"Votre abonnement : <b>{max_power}kVA</b>"
                body += f"<input style='display: none' type='text' value='{max_power}' id='consumption_max_power'>"
                body += """
                <table style='border: none;'>
                    <tr>
                        <td style='width: 30px; background-color: #FFB600'>&nbsp;</td>
                        <td style='border: none'>Seuil des 90% de l'abonnement atteint.</td>
                    </tr>
                    <tr>
                        <td style='width: 30px; background-color: #FF0000'>&nbsp;</td>
                        <td style='border: none'>Dépassement de l'abonnement maximal.</td>
                    </tr>
                    <tr>
                        <td style='border: none'></td>
                        <td style='border: none'>ATTENTION, Un dépassement d'abonnement ne veut pas forcement dire 
                        qu'il est nécessaire de basculer sur un abonnement supérieur.
                        Le compteur Linky vous autorise à dépasser un certain seuil pendant un certain temps afin
                        d'absorber un pic de consommation anormal sans pour autant disjoncter.                        
                        </td>
                    </tr>
                    <tr>
                        <td style='border: none'></td>
                        <td style='border: none'><a href="https://www.enedis.fr/media/2035/download">Lien vers la documentation officielle d’Enedis.</a> (cf. chapitre 7)</td>
                    </tr>
                </table>"""
                body += """
                <table id="dataTablePuissance" class="display">
                    <thead>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Événement</th>
                            <th class="title">Puissance (VA)</th>
                            <th class="title">Puissance (kVA)</th>
                            <th class="title">Ampère (A)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Événement</th>
                            <th class="title">Puissance (VA)</th>
                            <th class="title">Puissance (kVA)</th>
                            <th class="title">Ampère (A)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </tfoot>
                </table>
                """

            # PRODUCTION DATATABLE
            if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
                body += "<h2>Production</h2>"
                body += "<h3>Journalière</h2>"
                body += """
                <table id="dataTableProduction" class="display">
                    <thead>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Production (Wh)</th>
                            <th class="title">Production (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Production (Wh)</th>
                            <th class="title">Production (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </tfoot>
                </table>
                """
            if hasattr(self.usage_point_config, "production_detail") and self.usage_point_config.production_detail:
                body += "<h3>Horaires</h2>"
                body += "<ul><li>Quand vous videz le cache d'une tranche horaire, vous supprimez la totalité du cache de la journée.</li></ul>"
                body += """
                <table id="dataTableProductionDetail" class="display">
                    <thead>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Horaire</th>
                            <th class="title">Production (Wh)</th>
                            <th class="title">Production (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </thead>
                    <tfoot>
                        <tr>
                            <th class="title">Date</th>
                            <th class="title">Horaire</th>
                            <th class="title">Production (Wh)</th>
                            <th class="title">Production (kWh)</th>
                            <th class="title">Échec</th>
                            <th class="title">En&nbsp;cache</th>
                            <th class="title">Cache</th>
                            <th class="title">Liste noire</th>
                        </tr>
                    </tfoot>
                </table>
                """

            with open(f"{self.application_path}/templates/html/usage_point_id.html") as file_:
                index_template = Template(file_.read())
            html = index_template.render(
                select_usage_points=self.usage_point_select.html(),
                javascript_loader=open(f"{self.application_path}/templates/html/head.html").read(),
                body=body,
                side_menu=self.side_menu.html(),
                javascript=(
                    self.configuration_div.javascript()
                    + self.side_menu.javascript()
                    + self.usage_point_select.javascript()
                    + self.menu.javascript()
                    + open(f"{self.application_path}/templates/js/loading.js").read()
                    + open(f"{self.application_path}/templates/js/notif.js").read()
                    + open(f"{self.application_path}/templates/js/gateway_status.js").read()
                    + open(f"{self.application_path}/templates/js/datatable.js").read()
                    + open(f"{self.application_path}/templates/js/loading.js").read()
                    + self.javascript
                ),
                configuration=self.configuration_div.html().strip(),
                menu=self.menu.html(),
                css=self.menu.css(),
            )
            return html

    def contract_data(self):
        contract_data = {}
        if self.contract is not None:
            last_activation_date = self.contract.last_activation_date
            if hasattr(self.usage_point_config, "activation_date_daily") and hasattr(
                self.usage_point_config, "activation_date_detail"
            ):
                last_activation_date = (
                    f"<b style='text-decoration-line: line-through;'>{last_activation_date}</b><br>"
                    f"Date d'activation journalière : {self.usage_point_config.activation_date_daily} <br>"
                    f"Date d'activation détaillé : {self.usage_point_config.activation_date_detail} "
                )
            contract_data = {
                "usage_point_status": self.contract.usage_point_status,
                "meter_type": self.contract.meter_type,
                "segment": self.contract.segment,
                "subscribed_power": self.contract.subscribed_power,
                "last_activation_date": last_activation_date,
                "distribution_tariff": self.contract.distribution_tariff,
                "contract_status": self.contract.contract_status,
                "last_distribution_tariff_change_date": self.contract.last_distribution_tariff_change_date,
            }
        return contract_data

    def offpeak_hours_table(self):
        def split(data):
            result = ""
            if data is not None:
                for idx, coh in enumerate(data.split(";")):
                    result += f"{coh}"
                    if idx + 1 < len(data.split(";")):
                        result += "<br>"
            return result

        offpeak_hours = """
        <table class='table_offpeak_hours'>
            <tr>
                <th>Lundi</th>
                <th>Mardi</th>
                <th>Mercredi</th>
                <th>Jeudi</th>
                <th>Vendredi</th>
                <th>Samedi</th>
                <th>Dimanche</th>
            </tr>
            <tr>"""
        day = 0
        while day <= 6:
            week_day = f"offpeak_hours_{day}"
            if (
                hasattr(self.contract, week_day)
                and getattr(self.contract, week_day) != ""
                and hasattr(self.usage_point_config, week_day)
                and getattr(self.usage_point_config, week_day) != ""
            ):
                contract_offpeak_hours = split(getattr(self.contract, week_day))
                config_offpeak_hours = split(getattr(self.usage_point_config, week_day))
                if getattr(self.usage_point_config, week_day) != getattr(self.contract, week_day):
                    offpeak_hours += f"<td><i style='text-decoration:line-through;'>{contract_offpeak_hours}</i><br>{config_offpeak_hours}</td>"
                else:
                    offpeak_hours += f"<td>{contract_offpeak_hours}</td>"
            else:
                offpeak_hours += f"<td>Pas de données.</td>"
            day = day + 1
        offpeak_hours += "</tr></table>"
        return offpeak_hours

    def get_address(self):
        if self.address is not None:
            return f"{self.address.street}, " f"{self.address.postal_code} " f"{self.address.city}"
        else:
            return None

    def consumption(self):
        if hasattr(self.usage_point_config, "consumption") and self.usage_point_config.consumption:
            if self.recap_consumption_data:
                self.javascript += """
                google.charts.load("current", {packages:["corechart"]});
                google.charts.setOnLoadCallback(drawChartConsumption);
                function drawChartConsumption() {
                    var data = google.visualization.arrayToDataTable([
                """
                format_table = {}
                years_array = ""
                max_history = self.current_years - self.max_history_chart
                for years, data in self.recap_consumption_data.items():
                    if years > str(max_history):
                        years_array += f"'{years}', "
                        for month in range(1, 13):
                            month_2digit = "{:02d}".format(month)
                            if month not in format_table:
                                format_table[month] = []
                            if month_2digit in data["month"]:
                                format_table[month].append(data["month"][month_2digit])
                            else:
                                format_table[month].append(0)
                self.javascript += f"['Month', {years_array}],"
                for month, val in format_table.items():
                    table_value = ""
                    for idx, c in enumerate(val):
                        table_value += str(c / 1000)
                        if idx + 1 < len(val):
                            table_value += ", "
                    self.javascript += f"['{month}', {table_value}],"
                self.javascript += """]);
                            var options = {
                              title : '',
                              vAxis: {title: 'Consommation (kWh)'},
                              hAxis: {title: 'Mois'},
                              seriesType: 'bars',
                              series: {5: {type: 'line'}}
                            };

                            var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_consumption'));
                            chart.draw(data, options);
                        }
                            """

    def production(self):
        if hasattr(self.usage_point_config, "production") and self.usage_point_config.production:
            if self.recap_production_data:
                self.javascript += """
                google.charts.load("current", {packages:["corechart"]});
                google.charts.setOnLoadCallback(drawChartProduction);
                function drawChartProduction() {
                    var data = google.visualization.arrayToDataTable([
                """
                format_table = {}
                years_array = ""
                max_history = self.current_years - self.max_history_chart
                for years, data in self.recap_production_data.items():
                    if years > str(max_history):
                        years_array += f"'{years}', "
                        for month in range(1, 13):
                            month_2digit = "{:02d}".format(month)
                            if month not in format_table:
                                format_table[month] = []
                            if month_2digit in data["month"]:
                                format_table[month].append(data["month"][month_2digit])
                            else:
                                format_table[month].append(0)
                self.javascript += f"['Month', {years_array}],"
                for month, val in format_table.items():
                    table_value = ""
                    for idx, c in enumerate(val):
                        table_value += str(c / 1000)
                        if idx + 1 < len(val):
                            table_value += ", "
                    self.javascript += f"['{month}', {table_value}],"
                self.javascript += """]);
                                var options = {
                                  vAxis: {title: 'Production (kWh)'},
                                  hAxis: {title: 'Mois'},
                                  seriesType: 'bars',
                                  series: {5: {type: 'line'}}
                                };

                                var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_production'));
                                chart.draw(data, options);
                            }
                            """

    def consumption_vs_production(self, year):
        if self.recap_production_data != {} and self.usage_point_config.production != {}:
            # For a given year, we want to return the union of all months where
            # energy was either consumed or produced.
            # e.g. if there was [consumption C1, no production] in Jan,
            #      and [no consumption, production P2] in Feb
            #      we will return: [Jan, C1, 0], [Feb, 0, P2]
            compare_comsuption_production = {}
            consumption_months = []
            if year in self.recap_consumption_data:
                consumption_months = self.recap_consumption_data[year].get("month", {}).keys()

            production_months = []
            if year in self.recap_production_data:
                production_months = self.recap_production_data[year].get("month", {}).keys()

            all_months = set(consumption_months) | set(production_months)

            for month in all_months:
                consumption = self.recap_consumption_data[year]["month"][month] if month in consumption_months else 0
                production = self.recap_production_data[year]["month"][month] if month in production_months else 0
                compare_comsuption_production[month] = [float(consumption) / 1000, float(production) / 1000]
            self.javascript += (
                """            
            google.charts.load("current", {packages:["corechart"]});
            google.charts.setOnLoadCallback(drawChartProductionVsConsumption"""
                + year
                + """);
            function drawChartProductionVsConsumption"""
                + year
                + """() {
                var data = google.visualization.arrayToDataTable([
                ['Mois', 'Consommation', 'Production'],
            """
            )
            for month, data in compare_comsuption_production.items():
                table_value = ""
                for idx, value in enumerate(data):
                    if value == "":
                        value = 0
                    table_value += f"{value}"
                    if idx + 1 < len(data):
                        table_value += ", "
                self.javascript += f"['{month}', {table_value}],"
            self.javascript += (
                """
                ])
                data.sort([{column: 0}]);
                var options = {
                  title : '"""
                + year
                + """',
                  vAxis: {title: 'Consommation (kWh)'},
                  hAxis: {title: 'Mois'},
                  seriesType: 'bars',
                  series: {5: {type: 'line'}}
                };

                var chart = new google.visualization.ComboChart(document.getElementById('chart_daily_production_compare_"""
                + year
                + """'));
                chart.draw(data, options);
            }
            """
            )
        else:
            return "Pas de données."

    def generate_chart_hc_hp(self):
        price_consumption = self.db.get_stat(self.usage_point_id, "price_consumption")
        if price_consumption and hasattr(price_consumption[0], "value"):
            recap = ast.literal_eval(price_consumption[0].value)
            for year, data in sorted(recap.items(), reverse=True):
                if self.recap_hc_hp == "Pas de données.":
                    self.recap_hc_hp = ""
                self.recap_hc_hp += (
                    f'<td class="table_hp_hc_recap" style="width: {100 / len(recap)}%" id="piChart{year}"></td>'
                )
                self.javascript += "google.charts.load('current', {'packages':['corechart']});"
                self.javascript += f"google.charts.setOnLoadCallback(piChart{year});"
                self.javascript += f"function piChart{year}() " + "{"
                self.javascript += "   var data = google.visualization.arrayToDataTable([['Type', 'Valeur'],"
                self.javascript += f"['HC',     {data['HC']['Wh']}],"
                self.javascript += f"['HP',     {data['HP']['Wh']}],"
                # self.javascript += f"['BASE',     {data['BASE']['Wh']}],"
                self.javascript += (
                    """
                    ]);

                    var options = {
                        title: '"""
                    + year
                    + """',
                    };"""
                )
                self.javascript += (
                    f"var chart = new google.visualization.PieChart(document.getElementById('piChart{year}'));"
                )
                self.javascript += """chart.draw(data, options);
                }"""
        else:
            logging.error("Pas de données.")

    def generate_data(self, measurement_direction):
        data = self.db.get_daily_all(self.usage_point_id, measurement_direction)
        result = {}
        for item in data:
            year = item.date.strftime("%Y")
            month = item.date.strftime("%m")
            if year not in result:
                result[year] = {"value": 0, "month": {}}
            if month not in result[year]["month"]:
                result[year]["month"][month] = 0
            result[year]["value"] = result[year]["value"] + item.value
            result[year]["month"][month] = result[year]["month"][month] + item.value
        if measurement_direction == "consumption":
            self.recap_consumption_data = result
        else:
            self.recap_production_data = result

    def get_price(self, measurement_direction):
        def generate_price_compare(data):
            evolution_1 = round(data["price_2"] - data["price_1"], 2)
            evolution_2 = round(data["price_3"] - data["price_1"], 2)
            color_1 = "green"
            color_2 = "green"
            if data["price_1"] < data["price_2"]:
                color_1 = "red"
                evolution_1 = f"+{evolution_1}"
            if data["price_3"] and data["price_1"] < data["price_3"]:
                color_2 = "red"
                evolution_2 = f"+{evolution_2}"
            text_color = "var(--text-color);"
            if color_1 == "red" and color_2 == "red":
                text_color = "rgb(16, 150, 24);"
            return (
                f"<td>"
                f"<div style='float: left; width: 50%; padding-top: 14px;'><b style='font-size: 18px; color: {text_color}'>{data['price_1']} €</b></div>"
                f"<div style='float: right; width: 50%'><span style='color: {color_1}; font-size: 12px'>{data['lib_1']} : {evolution_1}€</span><br>"
                f"<span style='color: {color_2}; font-size: 12px'>{data['lib_2']} : {evolution_2}€</span></div>"
                f"</td>"
            )

        data = self.db.get_stat(self.usage_point_id, f"price_{measurement_direction}")
        html = ""
        if len(data) > 0:
            data = data[0]
            html = """
            <table style='width: 100%; text-align: center' class='table_recap'>

                <tr class='table_recap_header'>
                    <td>Années</td>
                    <td>Base</td>
                    <td>HP/HC</td>
            """
            tempo_config = self.config.tempo_config()
            html += "<td>Tempo</td>"
            html += "</tr>"
            if data:
                data_value = json.loads(data.value)
                for years, value in data_value.items():
                    price_base = round(value["BASE"]["euro"], 2)
                    price_hchp = round(value["HC"]["euro"] + value["HP"]["euro"], 2)
                    tempo_config = self.config.tempo_config()
                    price_tempo = None
                    value_tempo = 0
                    for color, tempo in value["TEMPO"].items():
                        value_tempo = value_tempo + tempo["euro"]
                    price_tempo = round(value_tempo, 2)
                    html += "<tr>"
                    html += f"<td class='table_recap_header'>{years}</td>"
                    html += generate_price_compare(
                        {
                            "price_1": price_base,
                            "price_2": price_hchp,
                            "price_3": price_tempo,
                            "lib_1": "HC/HP",
                            "lib_2": "Tempo",
                        }
                    )
                    html += generate_price_compare(
                        {
                            "price_1": price_hchp,
                            "price_2": price_base,
                            "price_3": price_tempo,
                            "lib_1": "Base",
                            "lib_2": "Tempo",
                        }
                    )
                    html += generate_price_compare(
                        {
                            "price_1": price_tempo,
                            "price_2": price_base,
                            "price_3": price_hchp,
                            "lib_1": "Base",
                            "lib_2": "HC/HP",
                        }
                    )

            html += "</table>"
        return html

    def recap(self, data):
        if data:
            current_years = int(datetime.now().strftime("%Y"))
            current_month = datetime.now().strftime("%m")
            max_history = current_years - self.max_history
            linear_years = {}
            mount_count = 0
            first_occurance = False
            for linear_year, linear_data in reversed(sorted(data.items())):
                for linear_month, linear_value in reversed(sorted(linear_data["month"].items())):
                    key = f"{current_month}/{current_years} => {current_month}/{current_years - 1}"
                    if not first_occurance and linear_value != 0:
                        first_occurance = True
                    if first_occurance:
                        if key not in linear_years:
                            linear_years[key] = 0
                        linear_years[key] = linear_years[key] + linear_value
                        mount_count = mount_count + 1
                        if mount_count >= 12:
                            current_years = current_years - 1
                            mount_count = 0
            body = '<table class="table_recap"><tr>'
            body += '<th class="table_recap_header">Annuel</th>'
            current_years = int(datetime.now().strftime("%Y"))
            for year, data in reversed(sorted(data.items())):
                if int(year) > max_history:
                    body += f"""
                <td class="table_recap_data">                    
                    <div class='recap_years_title'>{year}</div>
                    <div class='recap_years_value'>{round(data['value'] / 1000)} kWh</div>
                </td>    
                """
                    current_years = current_years - 1
            body += "</tr>"
            body += "<tr>"
            body += '<th class="table_recap_header">Annuel linéaire</th>'
            current_years = int(datetime.now().strftime("%Y"))
            for year, data in linear_years.items():
                if current_years > max_history:
                    data_last_years_class = ""
                    data_last_years = 0
                    key = f"{current_month}/{current_years - 1} => {current_month}/{current_years - 2}"
                    if str(key) in linear_years:
                        data_last_years = linear_years[str(key)]
                        if data_last_years != 0:
                            data_last_years = round((100 * int(data)) / int(data_last_years) - 100, 2)
                        current_years = current_years - 1
                        if data_last_years >= 0:
                            if data_last_years == 0:
                                data_last_years_class = "blue"
                            else:
                                data_last_years_class = "red"
                                data_last_years = f"+{data_last_years}"
                        else:
                            data_last_years_class = "green"
                    body += f"""
                <td class="table_recap_data">                    
                    <div class='recap_years_title'>{year}</div>
                    <div class='recap_years_value'>{round(data / 1000)} kWh</div>
                    <div class='recap_years_value {data_last_years_class}'><b>{data_last_years}%</b></div>
                </td>                
                """
            body += "</tr>"
            body += "</table>"
        else:
            body = "Pas de données."
        return body

    def recapv2(self, measurement_direction="consumption"):
        idx = 0
        finish = False
        output_data = {"years": {}, "linear": {}}
        body_year = ""
        body_linear = ""
        while not finish:
            linear_data = Stat(self.usage_point_id, measurement_direction).get_year_linear(idx)
            idx += 1
            if linear_data["value"] == 0:
                finish = True
            else:
                year = linear_data["end"].split("-")[0]
                year_data = Stat(self.usage_point_id, measurement_direction).get_year(int(year))
                output_data["years"][year] = year_data["value"]
                output_data["linear"][year] = {
                    "begin": linear_data["begin"],
                    "end": linear_data["end"],
                    "value": linear_data["value"],
                }

        for year, value in output_data["years"].items():
            body_year += f"""
            <td class="table_recap_data">
                <div class='recap_years_title'>{year}</div>
                <div class='recap_years_value'>{round(value / 1000)} kWh</div>
            </td>
            """
        for year, data in output_data["linear"].items():
            last_year = str(int(year) - 1)
            data_last_years = 0
            if last_year in output_data["linear"]:
                data_last_years = round(
                    (100 * int(data["value"])) / int(output_data["linear"][last_year]["value"]) - 100,
                    2,
                )
            if data_last_years >= 0:
                if data_last_years == 0:
                    data_last_years_class = "blue"
                else:
                    data_last_years_class = "red"
                    data_last_years = f"+{data_last_years}"
            else:
                data_last_years_class = "green"
            body_linear += f"""
            <td class="table_recap_data">
                <div class='recap_years_title'>{data["begin"]} => {data["end"]}</div>
                <div class='recap_years_value'>{round(data["value"] / 1000)} kWh</div>
                <div class='recap_years_value {data_last_years_class}'><b>{data_last_years}%</b></div>
            </td>
            """
        body = '<table class="table_recap"><tr>'
        body += '<th class="table_recap_header">Annuel</th>'
        body += body_year
        body += "</tr>"
        body += "<tr>"
        body += '<th class="table_recap_header">Annuel linéaire</th>'
        body += body_linear
        body += "</tr>"
        body += "</table>"
        return body
