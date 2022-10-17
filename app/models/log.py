import logging
import os
import sys

import yaml
from art import text2art, decor

if "DEBUG" in os.environ and os.getenv("DEBUG"):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d - %(levelname)8s : %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )


class Log:
    def __init__(self):
        self.message = None
        if os.path.exists("/data/config.yaml"):
            with open(f'/data/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)

    def show(self, message):
        self.separator_warning()
        if type(message) is list:
            for msg in message:
                logging.info(f" {msg}")
        else:
            logging.info(f" {message}")
        self.separator_warning()

    def log(self, message):
        if type(message) is list:
            for msg in message:
                logging.info(f" {msg}")
        else:
            logging.info(f" {message}")

    def title(self, message):
        self.separator()
        logging.info(f" {message.upper()}")
        self.separator()

    def debug(self, message):
        if type(message) is list:
            for msg in message:
                logging.debug(f" {msg}")
        else:
            logging.debug(f" {message}")

    def warning(self, message):
        if type(message) is list:
            for msg in message:
                logging.warning(f" {msg}")
        else:
            logging.warning(f" {message}")

    def error(self, message):
        logging.error(
            "═══════════════════════════════════════════════•°• :ERREUR: •°•════════════════════════════════════════════════")
        logging.error("")
        if type(message) is list:
            for msg in message:
                logging.error(f" {msg}")
        else:
            logging.error(f" {message}")
        logging.error("")
        logging.error(
            "═══════════════════════════════════════════════════════════════════════════════════════════════════════════════")

    def critical(self, message):
        if type(message) is list:
            for msg in message:
                logging.critical(f" {msg}")
        else:
            logging.critical(f" {message}")
        sys.exit()

    def separator(self):
        logging.info(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ◦ ❖ ◦ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def separator_warning(self):
        logging.info(
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ ▲ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def logo(self, version):
        Art = text2art("MyElectricalData")
        self.separator()
        for line in Art.splitlines():
            logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
        self.separator()
        version = f"VERSION : {version}"
        logging.info(f'{decor("barcode1")}{version: ^93}{decor("barcode1", reverse=True)}')
        self.separator()

    def log_usage_point_id(self, usage_point_id):
        text = f"Point de livraison : {usage_point_id}"
        self.separator()
        logging.info(f'{decor("barcode1")}{text: ^93}{decor("barcode1", reverse=True)}')
        self.separator()

    def finish(self):
        finish = text2art("Import Finish!!!")
        self.separator()
        for line in finish.splitlines():
            logging.info(f'{decor("barcode1")}{line: ^93}{decor("barcode1", reverse=True)}')
        self.separator()
