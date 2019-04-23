from peewee import *

from flask_login import UserMixin

DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):

    class Meta:
        database = DATABASE


class Entry(Model):
    title = CharField()
    Date = DateField()
    time_spent = IntegerField()
    what_you_learned = TextField()
    resource_to_remember = TextField()

    class Meta:
        database = DATABASE


class Tag(Model):
    entry = ForeignKeyField(Entry, related_name='tags')
    tag = CharField()

    class Meta:
        database = DATABASE
