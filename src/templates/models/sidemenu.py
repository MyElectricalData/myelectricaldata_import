from jinja2 import Template

from config import URL
from dependencies import APPLICATION_PATH


class SideMenu:
    def __init__(self):
        self.application_path = APPLICATION_PATH

    def html(self):
        with open(f"{self.application_path}/templates/html/sidemenu.html") as file_:
            side_menu = Template(file_.read())
        return side_menu.render(myelectricaldata=f"{URL}")

    def javascript(self):
        with open(f"{self.application_path}/templates/js/sidemenu.js") as file_:
            side_menu = Template(file_.read())
        return side_menu.render()
