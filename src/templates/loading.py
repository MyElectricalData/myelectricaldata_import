"""Loading Screen."""

from pathlib import Path

from jinja2 import Template

from config.main import APP_CONFIG
from templates.models.configuration import Configuration


class Loading:
    """Loading Screen."""

    def __init__(self):
        self.configuration_div = Configuration("Page de chargement", display_usage_point_id=True)

    def display(self):
        """Display Loading Screen."""
        with Path(f"{APP_CONFIG.application_path}/templates/html/loading.html").open(encoding="UTF-8") as file_:
            index_template = Template(file_.read())
        html = index_template.render(
            head=Path(f"{APP_CONFIG.application_path}/templates/html/head.html").open(encoding="UTF-8").read(),
            javascript=(Path(f"{APP_CONFIG.application_path}/templates/js/loading.js").open(encoding="UTF-8").read()),
            configuration=self.configuration_div.html().strip(),
        )
        return html
