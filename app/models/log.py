import os
from pprint import pprint
import datetime


class Log(object):
    def __init__(self, debug=False, error=False, trace=False):
        self.message = None
        self.trace = trace
        self.debug = debug
        self.error = error

    def msg(self, message, level=0):
        now = datetime.datetime.now()
        tab = ""
        for n in range(level):
            tab += "\t"
        if self.debug:
            if "DEBUG" in os.environ and os.environ['DEBUG']:
                print(f"{now} - DEBUG : {tab}{message}")
        elif self.trace:
            if "TRACE" in os.environ and os.environ['TRACE']:
                print(f"{now} - TRACE : {tab}{message}")
        elif self.error:
            print(f"{now} - ERROR : {tab}{message}")
        else:
            print(f"{now} - INFO  : {tab}{message}")


def log(message):
    Log(debug=False).msg(message)


def debug(message):
    Log(debug=True).msg(message)


def trace(message):
    Log(trace=True).msg(message)


def error(message, detail=None):
    Log(error=True).msg("========================= ERROR =============================")
    Log(error=True).msg(message)
    if detail is not None:
        Log(error=True).msg(detail)
    logSep()


def logg(message, tag=None):
    logSep()
    if tag is not None:
        print(f" => {tag}")
    pprint(message)
    logSep()


def logSep():
    log("==============================================================================")
