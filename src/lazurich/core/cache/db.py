from peewee import SqliteDatabase

from lazurich.core.paths import CACHE_FILE

db = SqliteDatabase(None, pragmas={'journal_mode': 'wal', 'foreign_keys': 1})

def init_db():
    db.init(CACHE_FILE)
    db.connect()
    from lazurich.core.cache import ALL_MODELS

    db.create_tables(ALL_MODELS)
