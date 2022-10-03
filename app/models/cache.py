import os
import json
import datetime

import sqlite3

from dependencies import *
from config import *
from models.log import log, logSep
from models.config import CONFIG


class Cache:

    def __init__(self, path="/data"):
        self.path = path
        self.db_name = "cache.db"
        if not os.path.exists(f'{self.path}/{self.db_name}'):
            self.sqlite = sqlite3.connect(f'{self.path}/{self.db_name}', timeout=10)
            self.cursor = self.sqlite.cursor()
            self.init_database()
        else:
            self.sqlite = sqlite3.connect(f'{self.path}/{self.db_name}', timeout=10)
            self.cursor = self.sqlite.cursor()
        self.check()

    def init_database(self):
        logSep()
        log("Initialise new SQLite Database")
        try:
            self.cursor.executescript(open("/app/init_cache.sql").read())
            ## Default Config
            config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
            self.cursor.execute(config_query, ["config", json.dumps({
                "day": datetime.datetime.now().strftime('%Y-%m-%d'),
                "call_number": 0,
                "max_call": 500,
                "version": VERSION
            })])
            self.sqlite.commit()
            log(" => Success")
        except Exception as e:
            log("=====> ERROR : Exception <======")
            log(e)
            log('<!> SQLite Database initialisation failed <!>')
            log(" => Reset database")

    def check(self):
        logSep()
        log("Connect to SQLite Database")
        try:
            config_query = f"INSERT OR REPLACE INTO config VALUES (?, ?)"
            self.cursor.execute(config_query, ["lastUpdate", datetime.datetime.now()])
            self.sqlite.commit()

            list_tables = ["config", "addresses", "contracts", "consumption_daily", "consumption_detail",
                           "production_daily", "production_detail"]

            query = f"SELECT name FROM sqlite_master WHERE type='table';"
            self.cursor.execute(query)
            query_result = self.cursor.fetchall()
            tables = []
            for table in query_result:
                tables.append(str(table).replace("('", "").replace("',)", ''))
            for tab in list_tables:
                if not tab in tables:
                    msg = f"Table {tab} is missing"
                    log(msg)
                    raise msg
            self.cursor.execute("INSERT OR REPLACE INTO config VALUES (?,?)", [0, 0])
            self.cursor.execute("INSERT OR REPLACE INTO addresses VALUES (?,?,?)", [0, 0, 0])
            self.cursor.execute("INSERT OR REPLACE INTO contracts VALUES (?,?,?)", [0, 0, 0])
            self.cursor.execute("INSERT OR REPLACE INTO consumption_daily VALUES (?,?,?,?)", [0, '1970-01-01', 0, 0])
            self.cursor.execute("INSERT OR REPLACE INTO consumption_detail VALUES (?,?,?,?,?,?)",
                                [0, '1970-01-01', 0, 0, "", 0])
            self.cursor.execute("INSERT OR REPLACE INTO production_daily VALUES (?,?,?,?)", [0, '1970-01-01', 0, 0])
            self.cursor.execute("INSERT OR REPLACE INTO production_detail VALUES (?,?,?,?,?,?)",
                                [0, '1970-01-01', 0, 0, "", 0])
            self.cursor.execute("DELETE FROM config WHERE key = 0")
            self.cursor.execute("DELETE FROM addresses WHERE pdl = 0")
            self.cursor.execute("DELETE FROM contracts WHERE pdl = 0")
            self.cursor.execute("DELETE FROM consumption_daily WHERE pdl = 0")
            self.cursor.execute("DELETE FROM consumption_detail WHERE pdl = 0")
            self.cursor.execute("DELETE FROM production_daily WHERE pdl = 0")
            self.cursor.execute("DELETE FROM production_detail WHERE pdl = 0")
            self.cursor.execute("DELETE FROM production_detail WHERE pdl = 0")
            config_query = f"SELECT * FROM config WHERE key = 'config'"
            self.cursor.execute(config_query)
            query_result = self.cursor.fetchall()
            json.loads(query_result[0][1])
            log(" => Success")
        except Exception as e:
            log("=====> ERROR : Exception <======")
            log(e)
            log('<!> Database structure is invalid <!>')
            log(" => Reset database")
            self.sqlite.close()
            os.remove(f"{self.path}/{self.db_name}")
            log(" => Reconnect")
            self.init_database()

    def purge_cache(self):
        logWarn()
        log("Reset SQLite Database")
        if os.path.exists(f'{self.path}/cache.db'):
            os.remove(f"{self.path}/cache.db")
            log(" => Success")
        else:
            log(" => Not cache detected")
