from flask import (Flask, render_template, redirect,
                   url_for, g, flash, request)
from flask_login import (LoginManager, login_user,
                         logout_user, login_required, current_user)
from flask_bcrypt import check_password_hash

from peewee import *
import datetime
from math import ceil

import models
import forms

DEBUG = True
PORT = '8000'
HOST = '0.0.0.0'


app = Flask(__name__)
app.secret_key = 'dfjhshvkshvnsvlnhsvsvsvvsvdsfsfsf'


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def user_loader(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_first_request
def init():
    models.init_db()
    models.DATABASE.close()


@app.before_request
def before_requets():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    # https://stackoverflow.com/questions/46741744
    # /flask-python-pass-input-as-parameter-to-function-of-different-route-with-fixe
    if request.args.get('page'):
        g.page = int(request.args.get('page'))
    else:
        g.page = 1
    g.max_page = ceil(models.Entry.select().count(None) / 10)
    data = models.Entry.select().paginate(g.page, 10)
    return render_template('index.html', data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username**form.username.data)
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash('Username or password is incorrect!')
        except models.DoesNotExist:
            flash('Username or password is incorrect!')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            username=form.username.data,
            password=form.password.data
        )
        flash('User created successfully!')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('index'))


@app.route('/entries')
def entries():
    return redirect(url_for('index'))


@app.route('/entries/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create(
            user=current_user._get_current_object(),
            title=form.title.data,
            date=form.date.data,
            time_spent=int(form.time_spent.data),
            what_you_learned=form.what_i_learned.data,
            resource_to_remember=form.resources_to_remember.data
        )
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<slug>/edit')
@login_required
def edit_entry(slug):
    form = forms.EntryForm()
    if form.validate_on_submit():
        pass
    return render_template('edit.html', form=form)


@app.route('/entries/<slug>/delete')
@login_required
def delete_entry(slug):
    return redirect(url_for('index'))


@app.route('/entries/<slug>')
def detail(slug):
    return render_template('detail.html')


if __name__ == "__main__":
    try:
        models.User.create_user(
            username='miro',
            password='miro123'
        )
        models.User.create_user(
            username='miro2',
            password='miro456'
        )
        models.User.create_user(
            username='miro3',
            password='miro789'
        )
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)
