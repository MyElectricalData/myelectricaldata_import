import os
import json
import sys
import threading

import datetime
from datetime import timedelta

import sqlite3
import sqlalchemy as db

from dependencies import *
from config import fail_count
from models.config import get_version


class Cache:

    def __init__(self, path="/data"):
        self.path = path
        self.db_name = "cache.db"
        self.db_path = f"{self.path}/{self.db_name}"

        new_db = False
        if not os.path.exists(f'{self.db_path}'):
            new_db = True

        self.engine = db.create_engine(f'sqlite:///{self.db_path}?check_same_thread=False', echo=True)
        # self.engine = db.create_engine(f'sqlite:///{self.db_path}?check_same_thread=False')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

        self.db_config = db.Table(
            'config', self.metadata,
            db.Column('key', db.String(255), primary_key=True, index=True, unique=True),
            db.Column('value', db.String(2000), nullable=False),
        )
        self.db_addresses = db.Table(
            'addresses', self.metadata,
            db.Column('pdl', db.String(255), primary_key=True, index=True, unique=True),
            db.Column('json', db.String(2000), nullable=False),
            db.Column('count', db.Integer()),
        )
        self.db_contracts = db.Table(
            'contracts', self.metadata,
            db.Column('pdl', db.String(255), primary_key=True, index=True, unique=True),
            db.Column('json', db.String(2000), nullable=False),
            db.Column('count', db.Integer()),
        )
        self.db_consumption_daily = db.Table(
            'consumption_daily', self.metadata,
            db.Column('pdl', db.String(255), index=True, nullable=False),
            db.Column('date', db.String(255), nullable=False),
            db.Column('value', db.Integer(), nullable=False),
            db.Column('fail', db.Integer()),
        )
        self.db_consumption_detail = db.Table(
            'consumption_detail', self.metadata,
            db.Column('pdl', db.String(255), index=True, nullable=False),
            db.Column('date', db.String(255), nullable=False),
            db.Column('value', db.Integer(), nullable=False),
            db.Column('interval', db.Integer(), nullable=False),
            db.Column('measure_type', db.String(255), nullable=False),
            db.Column('fail', db.Integer()),
        )
        self.db_production_daily = db.Table(
            'production_daily', self.metadata,
            db.Column('pdl', db.String(255), index=True, nullable=False),
            db.Column('date', db.String(255), nullable=False),
            db.Column('value', db.Integer(), nullable=False),
            db.Column('fail', db.Integer()),
        )
        self.db_production_detail = db.Table(
            'production_detail', self.metadata,
            db.Column('pdl', db.String(255), index=True, nullable=False),
            db.Column('date', db.String(255), nullable=False),
            db.Column('value', db.Integer(), nullable=False),
            db.Column('interval', db.Integer(), nullable=False),
            db.Column('measure_type', db.String(255), nullable=False),
            db.Column('fail', db.Integer()),
        )

        self.metadata.create_all(self.engine)

        if new_db:
            self.init_database()

        self.check()

    def close(self):
        self.sqlite.close()

    def init_database(self):
        logSep()
        log("Initialise new SQLite Database")
        try:
            self.connection.execute(
                self.db_config.insert().values(key='day', value=datetime.datetime.now().strftime('%Y-%m-%d')))
            self.connection.execute(
                self.db_config.insert().values(key='call_number', value=0))
            self.connection.execute(
                self.db_config.insert().values(key='max_call', value=500))
            self.connection.execute(
                self.db_config.insert().values(key='version', value=get_version()))
            log(" => Initialization success")
            sys.exit()
        except Exception as e:
            msg = [
                "=====> ERROR : Exception <======", e,
                '<!> SQLite Database initialisation failed <!>',
            ]
            logging.critical(msg)

    def check(self):
        logSep()
        log("Connect to SQLite Database")
        try:
            self.connection.execute(
                self.db_config.update().where(self.db_config.c.key == 'lastUpdate').values(
                    value=datetime.datetime.now()))
            list_tables = ["config", "addresses", "contracts", "consumption_daily", "consumption_detail",
                           "production_daily", "production_detail"]
            tables = []
            for table in self.metadata.sorted_tables:
                tables.append(str(table).replace("('", "").replace("',)", ''))
            for tab in list_tables:
                if not tab in tables:
                    msg = f"Table {tab} is missing"
                    log(msg)
                    raise msg

            self.connection.execute(self.db_config.insert().values(
                key=0, value=0))
            self.connection.execute(self.db_addresses.insert().values(
                pdl=0, json=0, count=0))
            self.connection.execute(self.db_contracts.insert().values(
                pdl=0, json=0, count=0))
            self.connection.execute(self.db_consumption_daily.insert().values(
                pdl=0, date='1970-01-01', value=0, fail=0))
            self.connection.execute(self.db_consumption_detail.insert().values(
                pdl=0, date='1970-01-01', value=0, interval=0, measure_type="", fail=0))
            self.connection.execute(self.db_production_daily.insert().values(
                pdl=0, date='1970-01-01', value=0, fail=0))
            self.connection.execute(self.db_production_detail.insert().values(
                pdl=0, date='1970-01-01', value=0, interval=0, measure_type="", fail=0))

            self.connection.execute(self.db_config.delete().where(self.db_config.c.key == 0))
            self.connection.execute(self.db_addresses.delete().where(self.db_addresses.c.pdl == 0))
            self.connection.execute(self.db_contracts.delete().where(self.db_contracts.c.pdl == 0))
            self.connection.execute(self.db_consumption_daily.delete().where(self.db_consumption_daily.c.pdl == 0))
            self.connection.execute(self.db_consumption_detail.delete().where(self.db_consumption_detail.c.pdl == 0))
            self.connection.execute(self.db_production_daily.delete().where(self.db_production_daily.c.pdl == 0))
            self.connection.execute(self.db_production_detail.delete().where(self.db_production_detail.c.pdl == 0))

            # config_query = "SELECT * FROM config WHERE key = 'config'"
            # query_result = self.query(query=config_query, data=[], fetch="fetchall")
            # json.loads(query_result[0][1])
            log(" => Connection success")
        except Exception as e:
            log("=====> ERROR : Exception <======")
            log(e)
            log('<!> Database structure is invalid <!>')
            log(" => Reset database")
            self.sqlite.close()
            os.remove(f"{self.db_path}")
            log(" => Reconnect")
            self.init_database()

    def get_usage_points_id(self):
        return self.connection.execute(self.db_contracts.select()).fetchall()

    def purge_cache(self):
        logWarn()
        log("Reset SQLite Database")
        if os.path.exists(f'{self.path}/cache.db'):
            os.remove(f"{self.path}/cache.db")
            log(" => Success")
        else:
            log(" => Not cache detected")

    def get_contract(self, usage_point_id):
        result = self.connection.execute(
            self.db_contracts.select().
            where(self.db_contracts.c.pdl == usage_point_id)
        ).fetchone()
        debug(result)
        return result

    def insert_contract(self, usage_point_id, contract, count=0):
        if self.connection.execute(
                self.db_contracts.select()
                        .where(self.db_contracts.c.pdl == usage_point_id)
        ).fetchone() is None:
            # INSERT
            self.connection.execute(self.db_contracts.insert()
                                    .values(pdl=usage_point_id, json=contract, count=count))
        else:
            # UPDATE
            self.connection.execute(self.db_contracts.update()
                                    .where(self.db_contracts.c.pdl == usage_point_id)
                                    .values(pdl=usage_point_id, json=contract, count=count))

    def get_addresse(self, usage_point_id):
        return self.connection.execute(
            self.db_addresses.select()
            .where(self.db_addresses.c.pdl == usage_point_id)
        ).fetchone()

    def insert_addresse(self, usage_point_id, addresse, count=0):
        if self.connection.execute(
                self.db_addresses.select()
                        .where(self.db_addresses.c.pdl == usage_point_id)
        ).fetchone() is None:
            # INSERT
            self.connection.execute(self.db_addresses.insert()
                                    .values(pdl=usage_point_id, json=addresse, count=count))
        else:
            # UPDATE
            self.connection.execute(self.db_addresses.update()
                                    .where(self.db_addresses.c.pdl == usage_point_id)
                                    .values(pdl=usage_point_id, json=addresse, count=count))

    def get_consumption_daily_all(self, usage_point_id):
        return self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .order_by(self.db_consumption_daily.c.date)
        ).fetchall()

    def get_consumption_daily(self, usage_point_id, begin, end):
        dateBegin = datetime.datetime.strptime(begin, '%Y-%m-%d')
        dateEnded = datetime.datetime.strptime(end, '%Y-%m-%d')

        delta = dateEnded - dateBegin
        result = {
            "missing_data": False,
            "date": {},
            "count": 0
        }
        for i in range(delta.days + 1):
            checkDate = dateBegin + timedelta(days=i)
            checkDate = checkDate.strftime('%Y-%m-%d')
            query_result = self.connection.execute(
                self.db_consumption_daily.select()
                .where(self.db_consumption_daily.c.pdl == usage_point_id)
                .where(self.db_consumption_daily.c.date == checkDate)
                .order_by(self.db_consumption_daily.c.date)
            ).fetchone()
            if query_result is None:
                result["date"][checkDate] = {
                    "status": False,
                    "fail": 0,
                    "value": 0
                }
                result["missing_data"] = True
                result["count"] = result["count"] + 1
            elif query_result[3] >= fail_count:
                result["date"][checkDate] = {
                    "status": True,
                    "fail": query_result[3],
                    "value": query_result[2]
                }
            elif query_result[2] == 0:
                result["date"][checkDate] = {
                    "status": False,
                    "fail": query_result[3],
                    "value": query_result[2]
                }
                result["missing_data"] = True
                result["count"] = result["count"] + 1
            else:
                result["date"][checkDate] = {
                    "status": True,
                    "fail": 0,
                    "value": query_result[2]
                }
        return result

    def insert_consumption_daily(self, usage_point_id, date, value, fail=0):
        current_data = self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .where(self.db_consumption_daily.c.date == date)
        ).fetchone()
        if current_data is None:
            return self.connection.execute(
                self.db_consumption_daily.insert()
                .values(pdl=usage_point_id, date=date, value=value, fail=fail))
        else:
            return self.connection.execute(
                self.db_consumption_daily.update()
                .where(self.db_consumption_daily.c.pdl == usage_point_id)
                .where(self.db_consumption_daily.c.date == date)
                .values(pdl=usage_point_id, date=date, value=value, fail=fail))

    def get_consumption_detail_all(self, usage_point_id):
        return self.connection.execute(
            self.db_consumption_detail.select()
            .where(self.db_consumption_detail.c.pdl == usage_point_id)
            .order_by(self.db_consumption_detail.c.date)
        ).fetchall()

    def get_consumption_detail(self, usage_point_id, begin, end):
        dateBegin = datetime.datetime.strptime(begin, '%Y-%m-%d')
        dateEnded = datetime.datetime.strptime(end, '%Y-%m-%d')
        delta = dateEnded - dateBegin

        result = {
            "missing_data": False,
            "date": {},
            "count": 0
        }

        for i in range(delta.days + 1):
            query_result = self.connection.execute(
                self.db_consumption_detail.select()
                .where(self.db_consumption_detail.c.pdl == usage_point_id)
                .filter(self.db_consumption_detail.c.date <= end)
                .filter(self.db_consumption_detail.c.date >= begin)
            ).fetchall()

            if len(query_result) < 160:
                result["missing_data"] = True
            else:
                for query in query_result:
                    date = query[1]
                    value = query[2]
                    interval = query[3]
                    measure_type = query[4]
                    fail = query[5]
                    result["date"][date] = {
                        "value": value,
                        "interval": interval,
                        "measure_type": measure_type,
                        "fail": fail,
                    }
            return result

    def insert_consumption_detail(self, usage_point_id, date, value, interval, measure_type, fail=0):
        current_data = self.connection.execute(
            self.db_consumption_detail.select()
            .where(self.db_consumption_detail.c.pdl == usage_point_id)
            .where(self.db_consumption_detail.c.date == date)
        ).fetchone()
        if current_data is None:
            return self.connection.execute(
                self.db_consumption_detail.insert()
                .values(
                    pdl=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    fail=fail)
            )
        else:
            return self.connection.execute(
                self.db_consumption_detail.update()
                .where(self.db_consumption_detail.c.pdl == usage_point_id)
                .where(self.db_consumption_detail.c.date == date)
                .values(
                    pdl=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    fail=fail)
            )

    def get_production_daily_all(self, usage_point_id):
        return self.connection.execute(
            self.db_production_daily.select()
            .where(self.db_production_daily.c.pdl == usage_point_id)
            .order_by(self.db_production_daily.c.date)
        ).fetchall()
