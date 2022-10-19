import logging
import os
import sys
from pprint import pprint

import yaml
from art import text2art, decor


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class Log:
    def __init__(self):
        self.message = None
        if os.path.exists("/data/config.yaml"):
            with open(f'/data/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

        logging.basicConfig(
            format='%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        self.logging = logging.getLogger(__name__)
        if "DEBUG" in os.environ and str2bool(os.getenv("DEBUG")):
            self.logging.setLevel("DEBUG")
        else:
            self.logging.setLevel("INFO")

    def show(self, message):
        self.separator_warning()
        if type(message) is list:
            for msg in message:
                pprint(f" {msg}")
        else:
            pprint(f" {message}")
        self.separator_warning()

    def log(self, message):
        if type(message) is list:
            for msg in message:
                self.logging.info(f" {msg}")
        else:
            self.logging.info(f" {message}")

    def title(self, message):
        self.separator()
        self.logging.info(f" {message.upper()}")
        self.separator()

    def debug(self, message):
        if type(message) is list:
            for msg in message:
                self.logging.debug(f" {msg}")
        else:
            self.logging.debug(f" {message}")

    def warning(self, message):
        if type(message) is list:
            for msg in message:
                self.logging.warning(f" {msg}")
        else:
            self.logging.warning(f" {message}")

    def error(self, message):
        self.logging.error(
            "═══════════════════════════════════════════════•°• :ERREUR: •°•════════════════════════════════════════════════")
        self.logging.error("")
        if type(message) is list:
            for msg in message:
                self.logging.error(f" {msg}")
        else:
            self.logging.error(f" {message}")
        self.logging.error("")
        self.logging.error(
            "═══════════════════════════════════════════════════════════════════════════════════════════════════════════════")

    def critical(self, message):
        if type(message) is list:
            for msg in message:
                self.logging.critical(f" {msg}")
        else:
            self.logging.critical(f" {message}")
        sys.exit()

    def separator(self):
        self.logging.info(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ ❖ ◦ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def separator_warning(self):
        self.logging.info(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ▲ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def logo(self, version):
        Art = text2art("MyElectricalData")
        self.separator()
        for line in Art.splitlines():
            self.logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
        self.separator()
        version = f"VERSION : {version}"
        self.logging.info(f'{decor("barcode1")}{version: ^93}{decor("barcode1", reverse=True)}')
        self.separator()

    def log_usage_point_id(self, usage_point_id):
        text = f"Point de livraison : {usage_point_id}"
        self.separator()
        self.logging.info(f'{decor("barcode1")}{text: ^93}{decor("barcode1", reverse=True)}')
        self.separator()

    def finish(self):
        finish = text2art("Import Finish!!!")
        self.separator()
        for line in finish.splitlines():
            self.logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
        self.separator()
