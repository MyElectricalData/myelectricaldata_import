import datetime
import json
import os
import time
from datetime import timedelta

import __main__ as app
import sqlalchemy as db
from dependencies import *
from models.config import get_version



class Cache:

    def __init__(self, path="/data"):
        self.path = path
        self.db_name = "cache.db"
        self.db_path = f"{self.path}/{self.db_name}"
        self.uri = f'sqlite:///{self.db_path}?check_same_thread=False'

        self.engine = db.create_engine(self.uri)
        self.connection = self.engine.connect()
        self.metadata = db.MetaData()

        self.db_config = None
        self.db_addresses = None
        self.db_contracts = None
        self.db_consumption_daily = None
        self.db_consumption_detail = None
        self.db_production_daily = None
        self.db_production_detail = None

        # if new_db:
        self.init_database()
        self.check()

    def close(self):
        self.connection.invalidate()
        self.connection.close()
        self.engine.dispose()
        time.sleep(5)

    def lock_status(self):
        result = self.connection.execute(
            self.db_config.select().
            where(self.db_config.c.key == "lock")
        ).fetchone()[1]
        if result == "0":
            return False
        else:
            return True

    def lock(self):
        self.connection.execute(
            self.db_config.update().values(value=1)
            .where(self.db_config.c.key == "lock"))
        return self.lock_status()

    def unlock(self):
        self.connection.execute(
            self.db_config.update().values(value=0)
            .where(self.db_config.c.key == "lock"))
        return self.lock_status()

    def init_database(self):
        app.LOG.separator()
        app.LOG.log("Initialise new SQLite Database")
        try:
            self.engine = db.create_engine(self.uri)
            self.connection = self.engine.connect()
            self.metadata = db.MetaData()
            self.db_config = db.Table(
                'config', self.metadata,
                db.Column('key', db.String(255), primary_key=True, index=True, unique=True),
                db.Column('value', db.String(2000), nullable=False),
            )
            app.LOG.log(" => config")
            self.db_addresses = db.Table(
                'addresses', self.metadata,
                db.Column('pdl', db.String(255), primary_key=True, index=True, unique=True),
                db.Column('json', db.String(2000), nullable=False),
                db.Column('count', db.Integer(), default=0),
            )
            app.LOG.log(" => addresses")
            self.db_contracts = db.Table(
                'contracts', self.metadata,
                db.Column('pdl', db.String(255), primary_key=True, index=True, unique=True),
                db.Column('json', db.String(2000), nullable=False),
                db.Column('count', db.Integer(), default=0),
            )
            app.LOG.log(" => contracts")
            self.db_consumption_daily = db.Table(
                'consumption_daily', self.metadata,
                db.Column('pdl', db.String(255), index=True, nullable=False),
                db.Column('date', db.String(255), nullable=False),
                db.Column('value', db.Integer(), nullable=False),
                db.Column('blacklist', db.Integer(), nullable=False, default=0),
                db.Column('fail_count', db.Integer(), nullable=False, default=0),
            )
            app.LOG.log(" => consumption_daily")
            self.db_consumption_detail = db.Table(
                'consumption_detail', self.metadata,
                db.Column('pdl', db.String(255), index=True, nullable=False),
                db.Column('date', db.String(255), nullable=False),
                db.Column('value', db.Integer(), nullable=False),
                db.Column('interval', db.Integer(), nullable=False),
                db.Column('measure_type', db.String(255), nullable=False),
                db.Column('blacklist', db.Integer(), nullable=False, default=0),
                db.Column('fail_count', db.Integer(), nullable=False, default=0),
            )
            app.LOG.log(" => consumption_detail")
            self.db_production_daily = db.Table(
                'production_daily', self.metadata,
                db.Column('pdl', db.String(255), index=True, nullable=False),
                db.Column('date', db.String(255), nullable=False),
                db.Column('value', db.Integer(), nullable=False),
                db.Column('blacklist', db.Integer(), nullable=False, default=0),
                db.Column('fail_count', db.Integer(), nullable=False, default=0),
            )
            app.LOG.log(" => production_daily")
            self.db_production_detail = db.Table(
                'production_detail', self.metadata,
                db.Column('pdl', db.String(255), index=True, nullable=False),
                db.Column('date', db.String(255), nullable=False),
                db.Column('value', db.Integer(), nullable=False),
                db.Column('interval', db.Integer(), nullable=False),
                db.Column('measure_type', db.String(255), nullable=False),
                db.Column('blacklist', db.Integer(), nullable=False, default=0),
                db.Column('fail_count', db.Integer(), nullable=False, default=0),
            )
            app.LOG.log(" => production_detail")
            self.metadata.create_all(self.engine)
            self.set_config(key='day', value=datetime.datetime.now().strftime('%Y-%m-%d'))
            self.set_config(key='call_number', value=0)
            self.set_config(key='max_call', value=500)
            self.set_config(key='version', value=get_version())
            self.set_config(key='lock', value=0)
            self.set_config(key='lastUpdate', value=str(datetime.datetime.now()))
            app.LOG.log(" => Initialization success")
        except Exception as e:
            msg = [
                "=====> ERROR : Exception <======", e,
                '<!> SQLite Database initialisation failed <!>',
            ]
            logging.critical(msg)

    def check(self):
        app.LOG.separator()
        app.LOG.log("Connect to SQLite Database")
        try:
            self.connection.execute(
                self.db_config.update()
                .where(self.db_config.c.key == 'lastUpdate')
                .values(value=datetime.datetime.now()))
            list_tables = ["config", "addresses", "contracts", "consumption_daily", "consumption_detail",
                           "production_daily", "production_detail"]
            tables = []
            for table in self.metadata.sorted_tables:
                tables.append(str(table).replace("('", "").replace("',)", ''))
            for tab in list_tables:
                if not tab in tables:
                    msg = f"Table {tab} is missing"
                    app.LOG.log(msg)
                    raise msg

            self.connection.execute(self.db_config.insert().values(
                key=0, value=0))
            self.connection.execute(self.db_addresses.insert().values(
                pdl=0, json=0, count=0))
            self.connection.execute(self.db_contracts.insert().values(
                pdl=0, json=0, count=0))
            self.connection.execute(self.db_consumption_daily.insert().values(
                pdl=0, date='1970-01-01', value=0, fail_count=0, blacklist=0))
            self.connection.execute(self.db_consumption_detail.insert().values(
                pdl=0, date='1970-01-01', value=0, interval=0, measure_type="", fail_count=0, blacklist=0))
            self.connection.execute(self.db_production_daily.insert().values(
                pdl=0, date='1970-01-01', value=0, fail_count=0, blacklist=0))
            self.connection.execute(self.db_production_detail.insert().values(
                pdl=0, date='1970-01-01', value=0, interval=0, measure_type="", fail_count=0, blacklist=0))

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
            app.LOG.log(" => Connection success")
        except Exception as e:
            app.LOG.log("=====> ERROR : Exception <======")
            app.LOG.log(e)
            app.LOG.log('<!> Database structure is invalid <!>')
            app.LOG.log(" => Reset database")
            self.close()
            os.remove(f"{self.db_path}")
            # for tbl in reversed(self.metadata.sorted_tables):
            #     self.engine.execute(tbl.delete())
            app.LOG.log(" => Reconnect")
            self.init_database()

    def get_usage_points_id(self):
        return self.connection.execute(self.db_contracts.select()).fetchall()

    def purge_cache(self):
        app.LOG.separator_warning()
        app.LOG.log("Reset SQLite Database")
        if os.path.exists(f'{self.path}/cache.db'):
            os.remove(f"{self.path}/cache.db")
            app.LOG.log(" => Success")
        else:
            app.LOG.log(" => Not cache detected")

    ## -----------------------------------------------------------------------------------------------------------------
    ## CONFIG
    ## -----------------------------------------------------------------------------------------------------------------
    def get_config(self, usage_point_id):
        current_data = self.connection.execute(
            self.db_config.select().
            where(self.db_config.c.key == usage_point_id)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return json.loads(current_data[1])

    def set_config(self, key, value):
        current_data = self.connection.execute(
            self.db_config.select().
            where(self.db_config.c.key == key)
        ).fetchone()
        if not current_data:
            self.connection.execute(self.db_config.insert()
                                    .values(key=key, value=value))
        else:
            return self.connection.execute(
                self.db_config.update()
                .where(self.db_config.c.key == key)
                .values(value=json.dumps(value)))

    def save_config(self, usage_point_id, config):
        result = self.get_config(usage_point_id)
        if not result:
            self.connection.execute(self.db_config.insert().values(
                key=usage_point_id, value=json.dumps(config)))
        else:
            return self.connection.execute(
                self.db_config.update()
                .where(self.db_config.c.key == usage_point_id)
                .values(value=json.dumps(config)))

    ## -----------------------------------------------------------------------------------------------------------------
    ## CONTRACT
    ## -----------------------------------------------------------------------------------------------------------------
    def get_contract(self, usage_point_id):
        current_data = self.connection.execute(
            self.db_contracts.select().
            where(self.db_contracts.c.pdl == usage_point_id)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return current_data[1]

    def insert_contract(self, usage_point_id, contract, count=0):
        if not self.get_contract(usage_point_id):
            # INSERT
            self.connection.execute(self.db_contracts.insert()
                                    .values(pdl=usage_point_id, json=contract, count=count))
        else:
            # UPDATE
            self.connection.execute(self.db_contracts.update()
                                    .where(self.db_contracts.c.pdl == usage_point_id)
                                    .values(pdl=usage_point_id, json=contract, count=count))

    ## -----------------------------------------------------------------------------------------------------------------
    ## ADDRESSE
    ## -----------------------------------------------------------------------------------------------------------------
    def get_addresse(self, usage_point_id):
        current_data = self.connection.execute(
            self.db_addresses.select()
            .where(self.db_addresses.c.pdl == usage_point_id)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return current_data[1]

    def insert_addresse(self, usage_point_id, addresse, count=0):
        if not self.get_addresse(usage_point_id):
            # INSERT
            self.connection.execute(self.db_addresses.insert()
                                    .values(pdl=usage_point_id, json=addresse, count=count))
        else:
            # UPDATE
            self.connection.execute(self.db_addresses.update()
                                    .where(self.db_addresses.c.pdl == usage_point_id)
                                    .values(pdl=usage_point_id, json=addresse, count=count))

    ## -----------------------------------------------------------------------------------------------------------------
    ## DAILY CONSUMPTION
    ## -----------------------------------------------------------------------------------------------------------------
    def get_consumption_daily_all(self, usage_point_id):
        return self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .order_by(self.db_consumption_daily.c.date.desc())
        ).fetchall()

    def get_consumption_daily_cache_data(self, usage_point_id, date):
        return self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .where(self.db_consumption_daily.c.date == date)
        ).fetchone()

    def get_consumption_daily_cache_state(self, date, usage_point_id):
        current_data = self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .where(self.db_consumption_daily.c.date == date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return True

    def get_consumption_daily_last_date(self, usage_point_id):
        current_data = self.connection.execute(
            self.db_consumption_daily.select()
            .where(self.db_consumption_daily.c.pdl == usage_point_id)
            .order_by(self.db_consumption_daily.c.date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return current_data[1]

    def consumption_daily_fail_increment(self, usage_point_id, date):
        result = self.get_consumption_daily_cache_state(usage_point_id, date)
        if not result:
            return self.connection.execute(
                self.db_consumption_daily.insert()
                .values(pdl=usage_point_id, date=date, value=0, blacklist=0, fail_count=1))
        else:
            return self.connection.execute(
                self.db_consumption_daily.update()
                .where(self.db_consumption_daily.c.pdl == usage_point_id)
                .where(self.db_consumption_daily.c.date == date)
                .values(pdl=usage_point_id, date=date, value=0, blacklist=0, fail_count=int(result[3])+1))

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
                # NEVER QUERY
                result["date"][checkDate] = {
                    "status": False,
                    "blacklist": 0,
                    "value": 0
                }
                result["missing_data"] = True
            else:
                # pdl = query_result[0]
                # date = query_result[1]
                consumption = query_result[2]
                blacklist = query_result[3]
                # fail_count = query_result[4]
                if blacklist == 1:
                    # IN BLACKLIST ?
                    result["date"][checkDate] = {
                        "status": True,
                        "blacklist": blacklist,
                        "value": consumption
                    }
                elif consumption == 0:
                    # ENEDIS RETURN NO DATA
                    result["date"][checkDate] = {
                        "status": False,
                        "blacklist": blacklist,
                        "value": consumption
                    }
                    result["missing_data"] = True
                    self.consumption_daily_fail_increment(usage_point_id, checkDate)
                else:
                    # SUCCESS
                    result["date"][checkDate] = {
                        "status": True,
                        "blacklist": blacklist,
                        "value": consumption
                    }
        return result

    def insert_consumption_daily(self, usage_point_id, date, value, blacklist=0):
        result = self.get_consumption_daily_cache_state(usage_point_id, date)
        app.LOG.show(result)
        if not result:
            return self.connection.execute(
                self.db_consumption_daily.insert()
                .values(pdl=usage_point_id, date=date, value=value, fail_count=0, blacklist=blacklist))
        else:
            return self.connection.execute(
                self.db_consumption_daily.update()
                .where(self.db_consumption_daily.c.pdl == usage_point_id)
                .where(self.db_consumption_daily.c.date == date)
                .values(pdl=usage_point_id, date=date, value=value, fail_count=0, blacklist=blacklist))

    def delete_consumption_daily(self, usage_point_id, date=None):
        if date is not None:
            current_data = self.get_consumption_daily_cache_state(usage_point_id, date)
            if not current_data:
                return False
            else:
                return self.connection.execute(
                    self.db_consumption_daily.delete()
                    .where(self.db_consumption_daily.c.pdl == usage_point_id)
                    .where(self.db_consumption_daily.c.date == date))
        else:
            return self.connection.execute(
                self.db_consumption_daily.delete()
                .where(self.db_consumption_daily.c.pdl == usage_point_id))

    def blacklist_consumption_daily(self, usage_point_id, date, action=True):
        current_data = self.get_consumption_daily_cache_state(usage_point_id, date)
        if not current_data:
            return self.connection.execute(
                self.db_consumption_daily.insert()
                .values(pdl=usage_point_id, date=date, value=0, fail_count=0, blacklist=action))
        else:
            return self.connection.execute(
                self.db_consumption_daily.update()
                .where(self.db_consumption_daily.c.pdl == usage_point_id)
                .where(self.db_consumption_daily.c.date == date)
                .values(blacklist=action))

    ## -----------------------------------------------------------------------------------------------------------------
    ## DETAIL CONSUMPTION
    ## -----------------------------------------------------------------------------------------------------------------
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
                    blacklist = query[5]
                    result["date"][date] = {
                        "value": value,
                        "interval": interval,
                        "measure_type": measure_type,
                        "blacklist": blacklist,
                    }
            return result

    def get_consumption_detail_cache_state(self, usage_point_id, date):
        current_data = self.connection.execute(
            self.db_consumption_detail.select()
            .where(self.db_consumption_detail.c.pdl == usage_point_id)
            .where(self.db_consumption_detail.c.date == date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return True

    def insert_consumption_detail(self, usage_point_id, date, value, interval, measure_type, blacklist=0):
        current_data = self.get_consumption_detail_cache_state(usage_point_id, date)
        if not current_data:
            return self.connection.execute(
                self.db_consumption_detail.insert()
                .values(
                    pdl=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    blacklist=blacklist)
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
                    blacklist=blacklist)
            )

    def delete_consumption_detail(self, usage_point_id, date=None):
        if date is not None:
            current_data = self.get_consumption_detail_cache_state(usage_point_id, date)
            if not current_data:
                return False
            else:
                return self.connection.execute(
                    self.db_consumption_detail.delete()
                    .where(self.db_consumption_detail.c.pdl == usage_point_id)
                    .where(self.db_consumption_detail.c.date == date))
        else:
            return self.connection.execute(
                self.db_consumption_detail.delete()
                .where(self.db_consumption_detail.c.pdl == usage_point_id))

    ## -----------------------------------------------------------------------------------------------------------------
    ## DAILY PRODUCTION
    ## -----------------------------------------------------------------------------------------------------------------
    def get_production_daily_all(self, usage_point_id):
        return self.connection.execute(
            self.db_production_daily.select()
            .where(self.db_production_daily.c.pdl == usage_point_id)
            .order_by(self.db_production_daily.c.date.desc())
        ).fetchall()

    def get_production_daily_cache_data(self, usage_point_id, date):
        return self.connection.execute(
            self.db_production_daily.select()
            .where(self.db_production_daily.c.pdl == usage_point_id)
            .where(self.db_production_daily.c.date == date)
        ).fetchone()

    def get_production_daily_cache_state(self, usage_point_id, date):
        current_data = self.connection.execute(
            self.db_production_daily.select()
            .where(self.db_production_daily.c.pdl == usage_point_id)
            .where(self.db_production_daily.c.date == date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return True

    def get_production_daily_last_date(self, usage_point_id):
        current_data = self.connection.execute(
            self.db_production_daily.select()
            .where(self.db_production_daily.c.pdl == usage_point_id)
            .order_by(self.db_production_daily.c.date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return current_data[1]

    def get_production_daily(self, usage_point_id, begin, end):
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
                self.db_production_daily.select()
                .where(self.db_production_daily.c.pdl == usage_point_id)
                .where(self.db_production_daily.c.date == checkDate)
                .order_by(self.db_production_daily.c.date)
            ).fetchone()
            if query_result is None:
                result["date"][checkDate] = {
                    "status": False,
                    "blacklist": 0,
                    "value": 0
                }
                result["missing_data"] = True
                result["count"] = result["count"] + 1
            elif query_result[2] == 0:
                result["date"][checkDate] = {
                    "status": False,
                    "blacklist": query_result[3],
                    "value": query_result[2]
                }
                result["missing_data"] = True
                result["count"] = result["count"] + 1
            else:
                result["date"][checkDate] = {
                    "status": True,
                    "blacklist": 0,
                    "value": query_result[2]
                }
        return result

    def insert_production_daily(self, usage_point_id, date, value, blacklist=0):
        current_data = self.get_production_daily_cache_state(usage_point_id, date)
        if not current_data:
            return self.connection.execute(
                self.db_production_daily.insert()
                .values(pdl=usage_point_id, date=date, value=value, blacklist=blacklist))
        else:
            return self.connection.execute(
                self.db_production_daily.update()
                .where(self.db_production_daily.c.pdl == usage_point_id)
                .where(self.db_production_daily.c.date == date)
                .values(pdl=usage_point_id, date=date, value=value, blacklist=blacklist))

    def delete_production_daily(self, usage_point_id, date=None):
        if date is not None:
            current_data = self.get_production_daily_cache_state(usage_point_id, date)
            if not current_data:
                return False
            else:
                return self.connection.execute(
                    self.db_production_daily.delete()
                    .where(self.db_production_daily.c.pdl == usage_point_id)
                    .where(self.db_production_daily.c.date == date))
        else:
            return self.connection.execute(
                self.db_production_daily.delete()
                .where(self.db_production_daily.c.pdl == usage_point_id))

    def blacklist_production_daily(self, usage_point_id, date, action=True):
        current_data = self.get_production_daily_cache_state(usage_point_id, date)
        if not current_data:
            return self.connection.execute(
                self.db_production_daily.insert()
                .values(pdl=usage_point_id, date=date, value=0, blacklist=action))
        else:
            return self.connection.execute(
                self.db_production_daily.update()
                .where(self.db_production_daily.c.pdl == usage_point_id)
                .where(self.db_production_daily.c.date == date)
                .values(blacklist=action))

    ## -----------------------------------------------------------------------------------------------------------------
    ## DETAIL PRODUCTION
    ## -----------------------------------------------------------------------------------------------------------------
    def get_production_detail_all(self, usage_point_id):
        return self.connection.execute(
            self.db_production_detail.select()
            .where(self.db_production_detail.c.pdl == usage_point_id)
            .order_by(self.db_production_detail.c.date)
        ).fetchall()

    def get_production_detail(self, usage_point_id, begin, end):
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
                self.db_production_detail.select()
                .where(self.db_production_detail.c.pdl == usage_point_id)
                .filter(self.db_production_detail.c.date <= end)
                .filter(self.db_production_detail.c.date >= begin)
            ).fetchall()

            if len(query_result) < 160:
                result["missing_data"] = True
            else:
                for query in query_result:
                    date = query[1]
                    value = query[2]
                    interval = query[3]
                    measure_type = query[4]
                    blacklist = query[5]
                    result["date"][date] = {
                        "value": value,
                        "interval": interval,
                        "measure_type": measure_type,
                        "blacklist": blacklist,
                    }
            return result

    def get_production_detail_cache_state(self, usage_point_id, date):
        current_data = self.connection.execute(
            self.db_production_detail.select()
            .where(self.db_production_detail.c.pdl == usage_point_id)
            .where(self.db_production_detail.c.date == date)
        ).fetchone()
        if current_data is None:
            return False
        else:
            return True

    def insert_production_detail(self, usage_point_id, date, value, interval, measure_type, blacklist=0):
        current_data = self.get_production_detail_cache_state(usage_point_id, date)
        if not current_data:
            return self.connection.execute(
                self.db_production_detail.insert()
                .values(
                    pdl=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    blacklist=blacklist)
            )
        else:
            return self.connection.execute(
                self.db_production_detail.update()
                .where(self.db_production_detail.c.pdl == usage_point_id)
                .where(self.db_production_detail.c.date == date)
                .values(
                    pdl=usage_point_id,
                    date=date,
                    value=value,
                    interval=interval,
                    measure_type=measure_type,
                    blacklist=blacklist)
            )

    def delete_production_detail(self, usage_point_id, date=None):
        if date is not None:
            current_data = self.get_production_detail_cache_state(usage_point_id, date)
            if not current_data:
                return False
            else:
                return self.connection.execute(
                    self.db_production_detail.delete()
                    .where(self.db_production_detail.c.pdl == usage_point_id)
                    .where(self.db_production_detail.c.date == date))
        else:
            return self.connection.execute(
                self.db_production_detail.delete()
                .where(self.db_production_detail.c.pdl == usage_point_id))
