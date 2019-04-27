from flask import (Flask, render_template, redirect,
                   url_for, g, flash, request, abort)
from flask_login import (LoginManager, login_user,
                         logout_user, login_required, current_user)
from flask_bcrypt import check_password_hash

from peewee import *
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


def make_pages(query=None):
    """
    sets page numbers and next and prev states
    """
    g.page = 1
    if query:
        g.max_page = ceil(query.count(None) / 10)
    else:
        g.max_page = ceil(models.Entry.select().count(None) / 10)
    if g.max_page == 0:
        g.max_page = 1
    # https://stackoverflow.com/questions/46741744
    # /flask-python-pass-input-as-parameter-to-function-of-different-route-with-fixe
    if request.args.get('page'):
        page = int(request.args.get('page'))
        if page < 1:
            page = 1
        if page > g.max_page:
            page = g.max_page
        g.page = page
    else:
        g.page = 1


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
    make_pages()
    entries = (models.Entry.select()
               .order_by(-models.Entry.date))
    data = models.get_data(query=entries, slug=None)
    return render_template('index.html.j2', data=data, url='index')


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
    return render_template('login.html.j2', form=form)


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
    return render_template('register.html.j2', form=form)


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
    """ create new entry"""
    form = forms.EntryForm()
    if form.validate_on_submit():
        # get tags and make it a list
        tags = form.tags.data.split(' ')
        models.Entry.create_entry(
            user=current_user._get_current_object(),
            title=form.title.data,
            date=form.date.data,
            time_spent=int(form.time_spent.data),
            what_you_learned=form.what_i_learned.data,
            resource_to_remember=form.resources_to_remember.data
        )
        # create tags
        entry = models.Entry.get(slug=models.create_slug(form.title.data))
        if tags:
            for tag in tags:
                models.Tag.create(
                    entry=entry,
                    tag=tag
                )
        return redirect(url_for('index'))
    return render_template('new.html.j2', form=form)


@app.route('/entries/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(slug):
    """ edit existing entry"""
    # get current selegted tags and entry
    data = models.Entry.get(models.Entry.slug == slug)
    tags = models.Tag.select().where(models.Tag.entry == data)
    all_tags = list()
    for tag in tags:
        all_tags.append(tag.tag)
    # only access if you created the entry
    if current_user.id != data.user.id:
        return abort(404)
    form = forms.EntryForm()
    if form.validate_on_submit():
        str_tags = form.tags.data.split(' ')
        models.Entry.update(
            title=form.title.data,
            slug=models.create_slug(form.title.data),
            date=form.date.data,
            time_spent=form.time_spent.data,
            what_you_learned=form.what_i_learned.data,
            resource_to_remember=form.resources_to_remember.data
        ).where(
            models.Entry.slug == slug
        ).execute()
        count = 0
        # update tags and remove if neccessary
        for counter, tag in enumerate(tags):
            if tag.tag in str_tags:
                models.Tag.update(
                    entry=data,
                    tag=str_tags[count]
                ).where(
                    models.Tag.id == tag.id
                ).execute()
                count = count + 1
            else:
                models.Tag.delete().where(
                    models.Tag.id == tag.id).execute()
        for counter, tag in enumerate(str_tags, 0):
            if counter < count:
                continue
            models.Tag.create(
                entry=data,
                tag=tag
            )
        return redirect(url_for('index'))
    # populate entry form with old data
    form.title.data = data.title
    form.date.data = data.date
    form.time_spent.data = data.time_spent
    form.what_i_learned.data = data.what_you_learned
    form.resources_to_remember.data = data.resource_to_remember
    form.tags.data = ' '.join(all_tags)
    return render_template('edit.html.j2', form=form, slug=data.slug)


@app.route('/entries/<slug>/delete')
@login_required
def delete_entry(slug):
    data = models.Entry.get(models.Entry.slug == slug)
    # only access if you created the entry
    if current_user.id != data.user.id:
        return abort(404)
    data.delete_instance()
    return redirect(url_for('index'))


@app.route('/entries/<slug>')
def detail(slug):
    data = models.get_data(query=None, slug=slug)
    return render_template('detail.html.j2', entry=data)


@app.route('/tag/<tag>')
def tag(tag):
    """ render entries with the specified tag"""
    # get entries that have the specified tag
    entries = (models.Entry.select().join(models.Tag).where(
        (models.Tag.entry == models.Entry.id) & (
            models.Tag.tag == tag)))
    make_pages(query=entries)
    data = models.get_data(query=entries, slug=None)
    return render_template('index.html.j2', data=data, url='tag', tag=tag)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('abort.html.j2'), 404


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
