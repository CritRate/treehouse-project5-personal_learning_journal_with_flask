from peewee import *

from flask_login import UserMixin
from flask_bcrypt import generate_password_hash
from flask import g

import string

DATABASE = SqliteDatabase('journal.db')


def init_db():
    DATABASE.create_tables([User, Entry, Tag], safe=True)


def create_slug(title):
    slug = title.translate(str.maketrans('', '', string.punctuation))
    slug = slug.replace(' ', '-')
    return slug


def get_data(query=None, slug=None):
    """ 
    if slug is None gets all the entries for index page or tag page
    otherwise gets the entry specified by slug
    """
    data = list()
    if not slug:
        page_query = query.paginate(g.page, 10)
        for entry in page_query:
            tag = (Tag.select().join(Entry).where(
                Entry.id == entry.id))
            username = User.get(id=entry.user).username
            data.append((entry, tag, username))
    else:
        entry = Entry.get(Entry.slug == slug)
        tag = (Tag.select().join(Entry).where(
            Entry.id == entry.id))
        username = User.get(id=entry.user).username
        data.append((entry, tag, username))
    return data


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
    slug = CharField(unique=True)
    date = DateField()
    time_spent = IntegerField()
    what_you_learned = TextField()
    resource_to_remember = TextField()

    class Meta:
        database = DATABASE

    @classmethod
    def create_entry(cls, user, title,
                     date, time_spent, what_you_learned,
                     resource_to_remember):
        try:
            cls.create(
                user=user,
                title=title,
                slug=create_slug(title),
                date=date,
                time_spent=time_spent,
                what_you_learned=what_you_learned,
                resource_to_remember=resource_to_remember
            )
        except IntegrityError:
            raise ValueError('title already exist')


class Tag(Model):
    entry = ForeignKeyField(Entry, related_name='tags')
    tag = CharField()

    class Meta:
        database = DATABASE
