from peewee import Model

from lazurich.core.cache.db import db


class BaseModel(Model):
    class Meta:
        database = db
