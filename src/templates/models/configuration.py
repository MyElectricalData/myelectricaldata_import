import datetime

from jinja2 import Template
from mergedeep import Strategy, merge

from dependencies import APPLICATION_PATH, str2bool


class Configuration:
    def __init__(self, db, title="", usage_point_id=0, display_usage_point_id=False):
        self.db = db
        self.application_path = APPLICATION_PATH
        self.title = title
        self.usage_point_id = usage_point_id
        self.display_usage_point_id = display_usage_point_id
        self.config = {
            "Global": {
                "name": {
                    "title": "Alias",
                    "help": "Alias du point de livraison pour vous permettre de le retrouver "
                    "plus facilement quand vous en avez plusieurs.",
                    "type": "",
                    "default": "",
                },
                "enable": {
                    "title": "Actif ?",
                    "help": "Active ou non le lancement du job de récupération des données tous X secondes<br/>"
                    'L\'intervalle de récupération est définie par le "cycle" dans le config.yaml',
                    "type": True,
                    "default": True,
                },
                "token": {
                    "title": "Token",
                    "help": "Votre token généré sur <a href='https://myelectricaldata.fr/'>MyElectricalData</a>.",
                    "type": "",
                    "default": "",
                },
                "cache": {
                    "title": "Cache",
                    "help": "L'activation du cache sur <a href='https://myelectricaldata.fr/'>MyElectricalData</a> "
                    "va vous permettre de réduire fortement les temps de réponse lors de la récupération des "
                    "données chez Enedis et également pallier au soucis d'indisponibilité de leur API (Si les "
                    "données ont déjà été récupérées au moins une fois dans les 30 derniers jours).",
                    "type": True,
                    "default": True,
                },
                "plan": {
                    "title": "Type de plan",
                    "help": "Permet de définir la méthode de calcul dans l'estimation du coût.",
                    "type": ["BASE", "HC/HP", "Tempo"],
                    "default": "HC/HP",
                },
                "refresh_addresse": {
                    "title": "Rafraichir vos coordonnées",
                    "help": "Permet de forcer le rafraichissement de vos coordonnées postales.",
                    "type": True,
                    "default": False,
                },
                "refresh_contract": {
                    "title": "Rafraichir votre contrat",
                    "help": "Permet de forcer le rafraichissement des informations liées à votre contrat.",
                    "type": True,
                    "default": False,
                },
            },
            "Consommation": {
                "consumption": {
                    "title": "Consommation journalière",
                    "help": "Active/Désactive la récupération de la consommation journalière.",
                    "type": True,
                    "default": True,
                },
                "consumption_max_power": {
                    "title": "Puissance maximale journalière",
                    "help": "Active/Désactive la récupération de la puissance maximal journalière.",
                    "type": True,
                    "default": True,
                },
                "consumption_max_date": {
                    "title": "Date max journalière",
                    "help": "Permet de définir la date de fin de récupération des données en mode journalier.  "
                    "<br><br>Si aucune valeur n'est définie ce sera la date 'last_activation_date' remontée "
                    "par les API d'Enedis."
                    "<br><br><b>ATTENTION, si cette valeur n'est pas correctement définie vous risquez de ne pas "
                    "récupérer la totalité de vos données ou encore d'avoir un dépassement du quota</b>",
                    "type": datetime.datetime.now(),
                    "default": "",
                },
                "consumption_detail": {
                    "title": "Consommation détaillée",
                    "help": "Active/Désactive la récupération de la consommation détaillée.<br><br></b>ATTENTION</b>, pour "
                    "fonctionner il vous faut activer le relevé de consommation horaire sur le site d'Enedis"
                    "Plus d'informations sont disponibles <a href='https://www.myelectricaldata.fr/faq'>ici</a>",
                    "type": True,
                    "default": True,
                },
                "consumption_detail_max_date": {
                    "title": "Date max détaillée",
                    "help": "Permet de définir la date de fin de récupération des données en mode détaillé.  "
                    "<br><br>Si aucune valeur n'est définie ce sera la date 'last_activation_date' remontée "
                    "par les API d'Enedis."
                    "<br><br><b>ATTENTION, si cette valeur n'est pas correctement définie vous risquez de ne pas "
                    "récupérer la totalité de vos données ou encore d'avoir un dépassement du quota</b>",
                    "type": datetime.datetime.now(),
                    "default": "",
                },
                "consumption_price_hc": {
                    "title": "Prix TTC HC",
                    "help": 'Permet de définir le prix du kWh en heures "creuse" pour l\'estimation du coût.',
                    "type": 0.1,
                    "default": 0.175,
                },
                "consumption_price_hp": {
                    "title": "Prix TTC HP",
                    "help": 'Permet de définir le prix du kWh en heures "pleines" pour l\'estimation du coût.',
                    "type": 0.1,
                    "default": 0.175,
                },
                "consumption_price_base": {
                    "title": "Prix TTC BASE",
                    "help": 'Permet de définir le prix du kWh en heures "classique" pour l\'estimation du coût.',
                    "type": 0.1,
                    "default": 0.175,
                },
            },
            "Heures creuses / pleines": {
                "title": {
                    "title": "Permet de calculer le ratio HC/HP.<br>"
                    "Si vous changez les plages horaires, il est nécessaire de vider le cache.<br>"
                    "<i>Format : 22h30-06h30;11h30-14h30</i>",
                    "help": "Permet de forcer les horaires HC/HP si elles ne sont pas remontées via l'API.<br>"
                    "Si vous êtes en contrat BASE, il peut être intéressant de saisir vos HC/HP afin "
                    "d'avoir une estimation du coût si vous étiez en contrat HC/HP.<br><br>"
                    "<b>Si vous changez les plages horaires, il est nécessaire de vider le cache.</b><br><br>"
                    "<b>Si vous avez plusieurs plages, il vous suffit des les séparer par des points "
                    "virgules (;)</b>",
                    "type": None,
                    "default": None,
                },
                "offpeak_hours_0": {"title": "Lundi", "type": "", "default": ""},
                "offpeak_hours_1": {"title": "Mardi", "type": "", "default": ""},
                "offpeak_hours_2": {"title": "Mercredi", "type": "", "default": ""},
                "offpeak_hours_3": {"title": "Jeudi", "type": "", "default": ""},
                "offpeak_hours_4": {"title": "Vendredi", "type": "", "default": ""},
                "offpeak_hours_5": {"title": "Samedi", "type": "", "default": ""},
                "offpeak_hours_6": {"title": "Dimanche", "type": "", "default": ""},
            },
            "Production": {
                "production": {
                    "title": "Production journalière",
                    "help": "Active/Désactive la récupération de la production journalière via vos panneaux solaires.",
                    "type": True,
                    "default": False,
                },
                "production_max_date": {
                    "title": "Date max journalière",
                    "help": "Permet de définir la date de fin de récupération des données en mode journalier.  "
                    "<br><br>Si aucune valeur n'est définie ce sera la date 'last_activation_date' remontée "
                    "par les API d'Enedis."
                    "<br><br><b>ATTENTION, si cette valeur n'est pas correctement définie vous risquez de ne pas "
                    "récupérer la totalité de vos données ou encore d'avoir un dépassement de quota</b>",
                    "type": datetime.datetime.now(),
                    "default": "",
                },
                "production_detail": {
                    "title": "Production détaillée",
                    "help": "Active/Désactive la récupération de la production détaillée via vos panneaux solaires."
                    "<br><br></b>ATTENTION</b>, pour fonctionner il vous faut activer le relevé de consommation horaire"
                    "sur le site d'Enedis<br>Plus d'informations sont disponibles "
                    "<a href='https://www.myelectricaldata.fr/faq'>ici</a>",
                    "type": True,
                    "default": False,
                },
                "production_detail_max_date": {
                    "title": "Date max détaillée",
                    "help": "Permet de définir la date de fin de récupération des données en mode détaillé.  "
                    "<br><br>Si aucune valeur n'est définie ce sera la date 'last_activation_date' remontée "
                    "par les API d'Enedis."
                    "<br><br><b>ATTENTION, si cette valeur n'est pas correctement définie vous risquez de ne pas "
                    "récupérer la totalité de vos données ou encore d'avoir un dépassement de quota</b>",
                    "type": datetime.datetime.now(),
                    "default": "",
                },
                "production_price": {
                    "title": "Prix de revente TTC",
                    "help": "Permet de définir le prix du kWh en revente si vous étes en revente totale.",
                    "type": 0.1,
                    "default": 0,
                },
            },
        }
        if self.display_usage_point_id:
            self.config = merge(
                {
                    "Global": {
                        "usage_point_id": {
                            "title": "Point de livraison",
                            "help": "Votre point de livraison.<br><br>Composé uniquement de "
                            "chiffres et de 14 caractères",
                            "type": "",
                            "default": "",
                        }
                    }
                },
                self.config,
                strategy=Strategy.ADDITIVE,
            )

    def html(self):
        current_cat = ""
        if self.usage_point_id != 0:
            configuration = f"""
            <div id="configuration" title="{self.title}" style="display: none">
                <form id="formConfiguration" action="/configuration/{self.usage_point_id}" method="POST"> 
                    <table class="table_configuration">     
            """
            config = self.db.get_usage_point(self.usage_point_id)
            contract = self.db.get_contract(self.usage_point_id)
            current_cat = ""
            for cat, cat_data in self.config.items():
                for key, data in cat_data.items():
                    if current_cat != cat:
                        configuration += f'<tr><td colspan="3" style="padding-top: 10px;"><h2>{cat}</h1></td></tr>'
                        current_cat = cat
                    title = data["title"]
                    var_type = data["type"]
                    if hasattr(config, key):
                        value = getattr(config, key)
                    elif hasattr(contract, key):
                        value = getattr(contract, key)
                    else:
                        value = None
                    if var_type is None:
                        configuration += f"""
                        <tr>
                            <td class="key" colspan='2'>{title}</td>"""
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
                    elif type(var_type) == bool:
                        checked = ""
                        value = str2bool(value)
                        if value:
                            checked = "checked"
                        configuration += f"""
                        <tr>
                            <td class="key">{title}</td>
                            <td class="value"><input type="checkbox" style="height: 20px;cursor: pointer;" id="configuration_{key}" name="{key}" {checked}></td>"""
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
                    elif type(var_type) == str or type(var_type) == float:
                        configuration += f"""
                        <tr>
                            <td class="key">{title}</td>
                            <td class="value"><input type="text" id="configuration_{key}" name="{key}" value="{value}"></td>"""
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
                    elif type(var_type) == list:
                        configuration += f'<tr><td class="key">{title}</td><td class="value"><select id="configuration_{key}" name="{key}">'
                        for option in var_type:
                            selected = ""
                            if option == value:
                                selected = "selected"
                            configuration += f'<option value="{option}" {selected}>{option.upper()}</option>'
                        configuration += "</select></td>"
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
                    elif isinstance(var_type, datetime.datetime):
                        if isinstance(value, datetime.datetime):
                            date = datetime.datetime.strftime(value, "%Y-%m-%d")
                        else:
                            date = ""
                        configuration += f"""
                        <tr>
                            <td class="key">{title}</td>
                            <td class="value"><input type="text" id="configuration_{key}" name="{key}" value="{date}"></td>"""
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
        else:
            configuration = f"""
            <div id="configuration" title="{self.title}" style="display: none">
                <form id="formConfiguration" action="/new_account" method="POST"> 
                    <table class="table_configuration">     
            """
            for cat, cat_data in self.config.items():
                for key, data in cat_data.items():
                    if current_cat != cat:
                        configuration += f'<tr><td colspan="3" style="padding-top: 10px;"><h2>{cat}</h1></td></tr>'
                        current_cat = cat
                    title = data["title"]
                    var_type = data["type"]
                    if "default" in data:
                        default = data["default"]
                    if var_type is None:
                        configuration += f"""
                                <tr>
                                    <td class="key" colspan='2'>{title}</td>"""
                        if "help" in data:
                            configuration += f"""
                                    <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
                    elif type(var_type) == bool:
                        checked = ""
                        if default:
                            checked = "checked"
                        configuration += f"""
                                <tr>
                                    <td class="key">{title}</td>
                                    <td class="value"><input type="checkbox" style="height: 20px;cursor: pointer;" id="configuration_{key}" name="{key}" {checked}></td>"""
                        if "help" in data:
                            configuration += f"""
                                    <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += f"</tr>"
                    elif type(var_type) == str or type(var_type) == float:
                        configuration += f"""
                                <tr>
                                    <td class="key">{title}</td>
                                    <td class="value"><input type="text" id="configuration_{key}" name="{key}" value="{default}"></td>"""
                        if "help" in data:
                            configuration += f"""
                                    <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += f"</tr>"
                    elif type(var_type) == list:
                        configuration += f'<tr><td class="key">{title}</td><td class="value"><select id="configuration_{key}" name="{key}">'
                        selected = ""
                        for option in var_type:
                            if option == default:
                                selected = "selected"
                            configuration += f'<option value="{option}" {selected}>{option.upper()}</option>'
                        configuration += f"</select></td>"
                        if "help" in data:
                            configuration += f"""
                                    <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += f"</tr>"
                    elif isinstance(var_type, datetime.datetime):
                        configuration += f"""
                        <tr>
                            <td class="key">{title}</td>
                            <td class="value"><input type="text" id="configuration_{key}" name="{key}" value=""></td>"""
                        if "help" in data:
                            configuration += f"""
                            <td><i class="material-icons help" alt="{data["help"]}">help_outline</i></td>"""
                        configuration += "</tr>"
        configuration += "</table></form></div>"
        return configuration

    def javascript(self):
        configuration_input = ""
        for cat, cat_data in self.config.items():
            for key, data in cat_data.items():
                var_type = data["type"]
                if type(var_type) == bool:
                    configuration_input += f'{key}: $("#configuration_{key}").prop("checked"),'
                elif type(var_type) == str or type(var_type) == float:
                    configuration_input += f'{key}: $("#configuration_{key}").val(),'
                elif type(var_type) == list:
                    configuration_input += f'{key}: $("#configuration_{key}").val(),'
                elif isinstance(var_type, datetime.datetime):
                    configuration_input += f'{key}: $("#configuration_{key}").val(),'

        with open(f"{self.application_path}/templates/js/usage_point_configuration.js") as file_:
            usage_point_configuration = Template(file_.read())
        return usage_point_configuration.render(configurationInput=configuration_input)
