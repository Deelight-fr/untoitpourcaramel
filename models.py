from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('database.sqlite')


class Annonce(Model):

    # import logging
    # logger = logging.getLogger('peewee')
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)

    # id = "pap-123456789"
    id = CharField(unique=True, primary_key=True)
    # site = [pap, lbc, logic-immo, seloger]
    site = CharField()
    created = DateTimeField()
    title = CharField()
    description = TextField(null=True)
    telephone = TextField(null=True)
    price = FloatField()
    charges = FloatField(null=True)
    surface = FloatField()
    rooms = IntegerField()
    bedrooms = IntegerField(null=True)
    city = CharField()
    link = CharField()
    picture = TextField(null=True)
    posted2trello = BooleanField(default=False)

    class Meta:
        database = db
        order_by = ('-created',)


def create_tables():
    with db:
        db.create_tables([Annonce])
