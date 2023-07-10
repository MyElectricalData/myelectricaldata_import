import logging
from os import environ, getenv

from init import CONFIG, DB
from models.jobs import Job


class Tasks:

    def __init__(self):
        if ("DEV" in environ and getenv("DEV")) or ("DEBUG" in environ and getenv("DEBUG")):
            logging.warning("=> Skip startup tasks")
            # self.import_data()
        else:
            self.import_data()

    def import_data(self):
        Job(CONFIG, DB).job_import_data()
