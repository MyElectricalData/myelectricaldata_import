import os
import sys
import yaml
from pprint import pprint
import datetime


class Log:
    def __init__(self, debug=False, error=False, trace=False):
        self.message = None
        if os.path.exists("/data/config.yaml"):
            with open(f'/data/config.yaml') as file:
                self.config = yaml.load(file, Loader=yaml.FullLoader)
        self.trace = self.config["trace"]
        self.debug = self.config["debug"]
        self.error = self.config["error"]


    def msg(self, message, level=0):
        now = datetime.datetime.now()
        tab = ""
        for n in range(level):
            tab += "\t"
        if self.debug:
            print(f"{now} - DEBUG : {tab}{message}")
        elif self.trace:
            print(f"{now} - TRACE : {tab}{message}")
        elif self.error:
            print(f"{now} - ERROR : {tab}{message}")
        else:
            print(f"{now} - INFO  : {tab}{message}")


def log(message):
    Log(debug=False).msg(message)


def debug(message):
    if type(message) is list:
        for msg in message:
            Log(debug=True).msg(msg)
    else:
        Log(debug=True).msg(message)


def trace(message):
    if type(message) is list:
        for msg in message:
            Log(trace=True).msg(msg)
    else:
        Log(trace=True).msg(message)


def error(message, detail=None):
    Log(error=True).msg("=================================== ERROR ========================================")
    Log(error=True).msg(message)
    if detail is not None:
        Log(error=True).msg(detail)
    logSep()


def warning(message, detail=None):
    Log().msg("================================== WARNING ======================================")
    if type(message) is list:
        for msg in message:
            Log().msg(msg)
    else:
        Log().msg(message)


def critical(message, detail=None):
    Log().msg("================================== CRITICAL ======================================")
    if type(message) is list:
        for msg in message:
            Log().msg(msg)
    else:
        Log().msg(message)
    logSep()
    sys.exit()


def logg(message, tag=None):
    logSep()
    if tag is not None:
        print(f" => {tag}")
    pprint(message)
    logSep()


def logSep():
    log("==================================================================================")


def logWarn():
    log("**********************************************************************************")
    log("**********************************************************************************")
