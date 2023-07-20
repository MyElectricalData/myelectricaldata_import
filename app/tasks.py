import logging
from os import environ, getenv

from init import CONFIG, DB
from models.jobs import Job


class Tasks:

    def __init__(self):
        self.config = CONFIG
        self.db = DB
        self.enable = True
        self.usage_points = self.db.get_usage_point_all()
        self.usage_point_config = None
        if ("DEV" in environ and getenv("DEV")) or ("DEBUG" in environ and getenv("DEBUG")):
            self.enable = False

    def boot(self):
        if self.enable:
            Job().job_import_data()

    def home_assistant_export(self):
        if self.enable:
            for self.usage_point_config in self.usage_points:
                usage_point_id = self.usage_point_config.usage_point_id
                Job(usage_point_id).export_home_assistant()
