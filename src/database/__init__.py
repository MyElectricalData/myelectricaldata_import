"""Module to manage database data."""
from database.main import Database

DB = Database()
DB.init_database()
DB.unlock()
