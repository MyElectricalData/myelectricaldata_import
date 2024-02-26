import __main__ as app
from jinja2 import Template

from dependencies import APPLICATION_PATH
from init import DB
from templates.models.configuration import Configuration


class Loading:
    def __init__(self):
        self.application_path = APPLICATION_PATH
        self.configuration_div = Configuration(DB, "Page de chargement", display_usage_point_id=True)

    def display(self):
        with open(f"{self.application_path}/templates/html/loading.html") as file_:
            index_template = Template(file_.read())
        html = index_template.render(
            head=open(f"{self.application_path}/templates/html/head.html").read(),
            javascript=(open(f"{self.application_path}/templates/js/loading.js").read()),
            configuration=self.configuration_div.html().strip(),
        )
        return html
