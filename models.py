from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash

DATABASE = SqliteDatabase('journal.db')


def init_db():
    DATABASE.create_tables([User, Entry, Tag], safe=True)


class User(UserMixin, Model):
    username = CharField(unique=True, max_length=30)
    password = CharField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, password, is_admin=False):
        try:
            cls.create(
                username=username,
                password=generate_password_hash(password)
            )
        except IntegrityError:
            raise ValueError('user already exist')


class Entry(Model):
    user = ForeignKeyField(User, related_name='entries')
    title = CharField(unique=True)
    date = DateField()
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
