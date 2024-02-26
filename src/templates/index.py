import markdown
from jinja2 import Template

from dependencies import APPLICATION_PATH
from templates.loading import Loading
from templates.models.configuration import Configuration
from templates.models.menu import Menu
from templates.models.sidemenu import SideMenu
from templates.models.usage_point_select import UsagePointSelect


class Index:
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self.application_path = APPLICATION_PATH
        self.usage_point_select = UsagePointSelect(self.config, self.db, choice=True)
        self.side_menu = SideMenu()
        self.menu = Menu(
            {
                "add_account": {
                    "title": "Ajouter un point de livraison",
                    "icon": "add_circle_outline",
                }
            }
        )
        self.configuration_div = Configuration(self.db, "Ajout d'un point de livraison", display_usage_point_id=True)

    def display(self):
        # if DB.lock_status():
        #     return Loading().display()
        # else:
        with open(f"{self.application_path}/templates/md/index.md") as file_:
            homepage_template = Template(file_.read())
        body = homepage_template.render()
        body = markdown.markdown(body, extensions=["fenced_code", "codehilite"])

        with open(f"{self.application_path}/templates/html/index.html") as file_:
            index_template = Template(file_.read())
        html = index_template.render(
            select_usage_points=self.usage_point_select.html(),
            head=open(f"{self.application_path}/templates/html/head.html").read(),
            body=body,
            side_menu=self.side_menu.html(),
            javascript=(
                self.configuration_div.javascript()
                + self.side_menu.javascript()
                + self.usage_point_select.javascript()
                + open(f"{self.application_path}/templates/js/notif.js").read()
                + open(f"{self.application_path}/templates/js/loading.js").read()
                + open(f"{self.application_path}/templates/js/gateway_status.js").read()
            ),
            configuration=self.configuration_div.html().strip(),
            menu=self.menu.html(),
        )
        return html
