import __main__ as app
import datetime
import json

import markdown
from dependencies import daterange
from jinja2 import Template
from models.config import get_version

from config import URL


class Html:

    def __init__(self, usage_point_id=None):
        self.cache = app.CACHE
        self.application_path = app.APPLICATION_PATH
        self.usage_point_id = usage_point_id
        if self.usage_point_id is not None:
            self.config = self.cache.get_config(self.usage_point_id)
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': self.config['token'],
            'call-service': "myelectricaldata",
            'version': get_version()
        }
        self.list_usage_points_id = ""

    def select_usage_points_id(self, selected_usage_point=None, choice=False):
        self.list_usage_points_id = '<select name="usages_points_id" id="select_usage_point_id" class="right">'
        if choice:
            self.list_usage_points_id += '<option value="none">--- Choix du point de livraison ---</option>'
        for pdl in self.cache.get_usage_points_id():
            usage_point = pdl[0]
            address_data = self.cache.get_addresse(usage_point_id=usage_point)
            if address_data is not None:
                address_data = json.loads(address_data)
                street = address_data['usage_point']['usage_point_addresses']['street']
                postal_code = address_data['usage_point']['usage_point_addresses']['postal_code']
                city = address_data['usage_point']['usage_point_addresses']['city']
                country = address_data['usage_point']['usage_point_addresses']['country']
                text = f"{usage_point} - {street}, {postal_code} {city} {country}"
            else:
                text = usage_point
            select = ""
            if selected_usage_point == usage_point:
                select = "selected"
            self.list_usage_points_id += f'<option value="{usage_point}" {select}>{text}</option>'
        self.list_usage_points_id += '</select>'

    def html_return(self, body, usage_point_id=0):
        import_button = f"""
        <div>
            <div id="bouton_enedis">
                <input type="text" id="usage_point_id" value="{usage_point_id}" style="display: none">
                <a style="text-decoration: none">
                    <div class="btn">Lancez la récupération</div>
                </a>
            </div>
        </div>'
        """
        with open(f'{self.application_path}/html/index.html') as file_:
            index_template = Template(file_.read())

        html = index_template.render(
            body=body,
            fullscreen=True,
            import_button=import_button,
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

    def page_index(self):
        usage_points_id = self.cache.get_usage_points_id()
        usage_points_id_data = ""
        if usage_points_id:
            self.select_usage_points_id(choice=True)
        with open(f'{self.application_path}/html/homepage.md') as file_:
            homepage_template = Template(file_.read())
        data = homepage_template.render(
            usage_points_id=usage_points_id_data,
        )
        data = markdown.markdown(data, extensions=['fenced_code', 'codehilite'])
        data = f"""
        <h3 style="line-height: 45px; font-size: 25px;">Choix du point de livraison {self.list_usage_points_id}</h3>
        <div style="padding-right:50px; font-family: 'Inter UI',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';" id="accueil"> 
        {data}            
        </div>
        """
        return self.html_return(body=data)

    def page_usage_point_id(self):
        config = self.cache.get_config(self.usage_point_id)
        contract = self.cache.get_contract(self.usage_point_id)
        contract_data = {}
        if contract is not None:
            _tmp = json.loads(contract)
            contract_data = {
                "usage_point_status": _tmp['usage_point']['usage_point_status'],
                "meter_type": _tmp['usage_point']['meter_type'],
                "segment": _tmp['contracts']['segment'],
                "subscribed_power": _tmp['contracts']['subscribed_power'],
                "last_activation_date": _tmp['contracts']['last_activation_date'],
                "distribution_tariff": _tmp['contracts']['distribution_tariff'],
                "offpeak_hours": _tmp['contracts']['offpeak_hours'],
                "contract_status": _tmp['contracts']['contract_status'],
                "last_distribution_tariff_change_date": _tmp['contracts']['last_distribution_tariff_change_date'],
            }
        address = self.cache.get_addresse(self.usage_point_id)
        address_data = {}
        if address is not None:
            _tmp = json.loads(address)
            address_data = {
                "street": _tmp['usage_point']['usage_point_addresses']['street'],
                "postal_code": _tmp['usage_point']['usage_point_addresses']['postal_code'],
                "city": _tmp['usage_point']['usage_point_addresses']['city'],
                "country": _tmp['usage_point']['usage_point_addresses']['country'],
            }

        with open(f'{self.application_path}/html/usage_point_id.md') as file_:
            homepage_template = Template(file_.read())

        if config["consumption"]:
            daily_consumption_data = self.generate_datatable(
                title="Consommation",
                daily_data=self.cache.get_consumption_daily_all(self.usage_point_id),
                cache_last_date=self.cache.get_consumption_daily_last_date(self.usage_point_id)
            )
            recap_consumption = self.recap(title="Consommation", data=daily_consumption_data['recap'])
            daily_consumption_data = daily_consumption_data["datatable"]

        if config["production"]:
            daily_production_data = self.generate_datatable(
                title="Production",
                daily_data=self.cache.get_production_daily_all(self.usage_point_id),
                cache_last_date=self.cache.get_production_daily_last_date(self.usage_point_id)
            )
            recap_production = self.recap(title="Production", data=daily_production_data['recap'])
            daily_production_data = daily_production_data["datatable"]

        data = homepage_template.render(
            contract_data=contract_data,
            address_data=address_data,
        )
        self.select_usage_points_id()
        data = markdown.markdown(data, extensions=['fenced_code', 'codehilite'])
        data = f"""
        <h3 style="line-height: 45px; font-size: 25px;">Choix du point de livraison {self.list_usage_points_id}</h3>
        <div style="padding-right:50px; font-family: 'Inter UI',-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif,'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol';" id="accueil"> 
        {data}
        <h1>Récapitulatif</h1>"""
        if config["consumption"]:
            data += recap_consumption
        if config["production"]:
            data += recap_production
        data += "<h1>Mes données journalières</h1>"
        if config["consumption"]:
            data += daily_consumption_data
        if config["production"]:
            data += daily_production_data
        data += "</div>"

        return self.html_return(body=data, usage_point_id=self.usage_point_id)

    def generate_datatable(self, title, daily_data, cache_last_date):
        tag = title.lower()
        result = f"""
        <h2>{title}</h2>
        <table id="dataTable{title}" class="display">
            <thead>
                <tr>
                    <th class="title">Date</th>
                    <th class="title">{title} (W)</th>
                    <th class="title">{title} (kW)</th>
                    <th class="title">En&nbsp;cache</th>
                    <th class="title">Cache</th>
                    <th class="title">Liste noire</th>
                </tr>
            </thead>
            <tbody>
        """

        date_format = '%Y-%m-%d'
        all_data = {}
        recap = {}
        for data in daily_data:
            all_data[data[1]] = {
                "value": data[2],
                "blacklist": data[3]
            }
        start_date = cache_last_date
        end_date = datetime.datetime.now()
        if start_date:
            start_date = datetime.datetime.strptime(start_date, date_format)
            for single_date in daterange(start_date, end_date):
                year = single_date.strftime("%Y")
                month = single_date.strftime("%m")
                if year not in recap:
                    recap[year] = {
                        "value": 0,
                        "month": {"01": 0, "02": 0, "03": 0, "04": 0, "05": 0, "06": 0, "07": 0,
                                  "08": 0, "09": 0,
                                  "10": 0, "11": 0,
                                  "12": 0,
                                  }
                    }
                date_text = single_date.strftime("%Y-%m-%d")
                conso_w = "0"
                conso_kw = "0"
                cache_state = f'<div id="{tag}_icon_{date_text}" class="icon_failed">0</div>'
                reset = f"""
                <input type="button" id="{tag}_import_{date_text}" name="import_{self.usage_point_id}_{date_text}" class="datatable_button datatable_button_import"   value="Importer">
                <input type="button" id="{tag}_reset_{date_text}"  name="reset_{self.usage_point_id}_{date_text}"  class="datatable_button"  value="Vider" style="display: none">
                """

                if date_text in all_data:
                    value = all_data[date_text]["value"]
                    blacklist_state = all_data[date_text]["blacklist"]
                    recap[year]["value"] = recap[year]["value"] + value
                    recap[year]['month'][month] = recap[year]['month'][month] + value
                    conso_w = f"{value}"
                    conso_kw = f"{value / 1000}"
                    cache_state = f'<div id="{tag}_icon_{date_text}" class="icon_success">1</div>'
                    reset = f"""
                    <input type="button" id="{tag}_import_{date_text}" name="import_{self.usage_point_id}_{date_text}" class="datatable_button datatable_button_import" value="Importer" style="display: none">
                    <input type="button" id="{tag}_reset_{date_text}"  name="reset_{self.usage_point_id}_{date_text}"  class="datatable_button" value="Vider">
                    """
                    display_blacklist = ''
                    display_whitelist = ''
                    if blacklist_state == 1:
                        display_blacklist = 'style="display: none"'
                    else:
                        display_whitelist = 'style="display: none"'
                    blacklist = f"""
                    <input type="button" class="datatable_button datatable_blacklist datatable_button_disable" id="{tag}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}" value="Blacklist" {display_blacklist}>
                    <input type="button" class="datatable_button datatable_whitelist" id="{tag}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}" value="Whitelist" {display_whitelist}>
                    """
                else:
                    blacklist = f"""
                       <input type="button" class="datatable_button datatable_blacklist" id="{tag}_blacklist_{date_text}" name="blacklist_{self.usage_point_id}_{date_text}"  value="Blacklist">
                       <input type="button" class="datatable_button datatable_whitelist" id="{tag}_whitelist_{date_text}" name="whitelist_{self.usage_point_id}_{date_text}"  value="Whitelist" style="display: none">
                    """

                result += f"""
                <tr>
                    <td><b>{date_text}</b></td>
                    <td id="{tag}_conso_w_{date_text}">{conso_w} W</td>
                    <td id="{tag}_conso_kw_{date_text}">{conso_kw} kW</td>
                    <td>{cache_state}</td>
                    <td class="loading_bg">{reset}</td>
                    <td class="loading_bg">{blacklist}</td>
                </tr>"""
        result += "</tbody></table>"
        return {
            "recap": recap,
            "datatable": result
        }

    def recap(self, title, data):
        result = f"""<h2>{title}</h2>"""
        current_years = int(datetime.datetime.now().strftime("%Y"))
        current_month = int(datetime.datetime.now().strftime("%m"))
        linear_years = {}
        mount_count = 0
        for linear_year, linear_data in reversed(sorted(data.items())):
            for linear_month, linear_value in reversed(sorted(linear_data["month"].items())):
                if linear_value != 0:
                    key = f"{current_month}/{current_years} => {current_month}/{current_years - 1}"
                    if key not in linear_years:
                        linear_years[key] = 0
                    linear_years[key] = linear_years[key] + linear_value
                    mount_count = mount_count + 1
                    if mount_count >= 12:
                        current_years = current_years - 1
                        mount_count = 0
        result += '<table class="table_recap"><tr>'
        result += '<th class="table_recap_header">Annuel</th>'
        for year, data in reversed(sorted(data.items())):
            result += f"""
        <td class="table_recap_data">                    
            <div class='recap_years_title'>{year}</div>
            <div class='recap_years_value'>{round(data['value'] / 1000)} kWh</div>
        </td>    
        """
        result += "</tr><tr>"
        result += '<th class="table_recap_header">Annuel linéaire</th>'
        current_years = int(datetime.datetime.now().strftime("%Y"))
        for year, data in linear_years.items():
            data_last_years_class = ""
            data_last_years = "---"
            key = f"{current_month}/{current_years - 1} => {current_month}/{current_years - 2}"
            if str(key) in linear_years:
                data_last_years = linear_years[str(key)]
                data_last_years = 100 - (round((data_last_years / data) * 100))
                current_years = current_years - 1
                if data_last_years >= 0:
                    if data_last_years == 0:
                        data_last_years_class = "blue"
                    else:
                        data_last_years_class = "red"
                        data_last_years = f"+{data_last_years}"
                else:
                    data_last_years_class = "green"
            result += f"""
        <td class="table_recap_data">                    
            <div class='recap_years_title'>{year}</div>
            <div class='recap_years_value'>{round(data / 1000)} kWh</div>
            <div class='recap_years_value {data_last_years_class}'><b>{data_last_years}%</b></div>
        </td>    
        """
        result += "</tr></table>"
        return result
