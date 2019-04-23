from flask import (Flask, render_template, redirect, url_for)

DEBUG = True
PORT = '8000'
HOST = '0.0.0.0'


app = Flask(__name__)
app.secret_key = 'dfjhshvkshvnsvlnhsvsvsvvsvdsfsfsf'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/entries')
def entries():
    return redirect(url_for('index'))


@app.route('/entries/new')
def new_entry():
    return render_template('new.html')


@app.route('/entries/<slug>/edit')
def edit_entry(slug):
    return render_template('edit.html')


@app.route('/entries/<slug>/delete')
def delete_entry(slug):
    return redirect(url_for('index'))


@app.route('/entries/<slug>')
def detail(slug):
    return render_template('detail.html')


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
