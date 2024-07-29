"""Index HTML."""
from pathlib import Path

import markdown
from jinja2 import Template

from config.main import APP_CONFIG
from templates.models.configuration import Configuration
from templates.models.menu import Menu
from templates.models.sidemenu import SideMenu
from templates.models.usage_point_select import UsagePointSelect


class Index:
    """Index HTML."""

    def __init__(self, db):
        self.config = APP_CONFIG
        self.db = db
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
        self.configuration_div = Configuration("Ajout d'un point de livraison", display_usage_point_id=True)

    def display(self):
        """Display Index."""
        with Path(f"{APP_CONFIG.application_path}/templates/md/index.md").open(encoding="UTF-8") as file_:
            homepage_template = Template(file_.read())
        body = homepage_template.render()
        body = markdown.markdown(body, extensions=["fenced_code", "codehilite"])

        with Path(f"{APP_CONFIG.application_path}/templates/html/index.html").open(encoding="UTF-8") as file_:
            index_template = Template(file_.read())

        with Path(f"{APP_CONFIG.application_path}/templates/html/head.html").open(encoding="UTF-8") as head:
            with Path(f"{APP_CONFIG.application_path}/templates/js/notif.js").open(encoding="UTF-8") as notif:
                with Path(f"{APP_CONFIG.application_path}/templates/js/loading.js").open(encoding="UTF-8") as loading:
                    with Path(f"{APP_CONFIG.application_path}/templates/js/gateway_status.js").open(
                        encoding="UTF-8"
                    ) as gateway_status:
                        html = index_template.render(
                            select_usage_points=self.usage_point_select.html(),
                            head=head.read(),
                            body=body,
                            side_menu=self.side_menu.html(),
                            javascript=(
                                self.configuration_div.javascript()
                                + self.side_menu.javascript()
                                + self.usage_point_select.javascript()
                                + notif.read()
                                + loading.read()
                                + gateway_status.read()
                            ),
                            configuration=self.configuration_div.html().strip(),
                            menu=self.menu.html(),
                        )
        return html
