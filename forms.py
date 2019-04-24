from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, IntegerField, TextAreaField)
from wtforms.fields.html5 import DateField
from wtforms.validators import (
    DataRequired, Length, EqualTo, ValidationError, NumberRange)


import models


def name_exists(form, field):
    try:
        models.User.get(models.User.username**field.data)
        raise ValidationError('Name already exists!')
    except models.DoesNotExist:
        return None


def title_exists(form, field):
    try:
        models.Entry.get(models.Entry.title**field.data)
        raise ValidationError('Title already exists! Try a different one')
    except models.DoesNotExist:
        return None


class LoginForm(FlaskForm):
    username = StringField(
        'username',
        validators=[
            DataRequired()
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(),
            Length(min=3)
        ]
    )


class RegisterForm(FlaskForm):
    username = StringField(
        'username',
        validators=[
            DataRequired(),
            name_exists
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(),
            Length(min=3),
            EqualTo('password2', 'Passwords must match!')
        ]
    )
    password2 = PasswordField(
        'confirm password',
        validators=[
            DataRequired(),
            Length(min=3)
        ]
    )


class EntryForm(FlaskForm):
    title = StringField(
        'Title', validators=[DataRequired(), title_exists]
    )
    date = DateField(
        'Date', validators=[DataRequired()]
    )
    time_spent = IntegerField(
        'Time spent(in hours)', validators=[DataRequired(),
                                            NumberRange(min=0, max=24)]
    )
    what_i_learned = TextAreaField(
        'What i learned', validators=[DataRequired()]
    )
    resources_to_remember = TextAreaField(
        'Resources to remember', validators=[DataRequired()]
    )
