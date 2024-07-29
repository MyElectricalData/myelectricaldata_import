"""Sidemenu."""
from pathlib import Path

from jinja2 import Template

from config.main import APP_CONFIG
from const import URL


class SideMenu:
    """Sidemenu."""

    def html(self):
        """Open HTML."""
        with Path(f"{APP_CONFIG.application_path}/templates/html/sidemenu.html").open(encoding="UTF-8") as file_:
            side_menu = Template(file_.read())
        return side_menu.render(myelectricaldata=f"{URL}")

    def javascript(self):
        """Open JS."""
        with Path(f"{APP_CONFIG.application_path}/templates/js/sidemenu.js").open(encoding="UTF-8") as file_:
            side_menu = Template(file_.read())
        return side_menu.render()
