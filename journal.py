# -*- coding: utf-8 -*-
# add this import at the top of your file:
import os
import psycopg2
from contextlib import closing
from flask import g
import datetime
from flask import render_template

from flask import Flask
from flask import abort
from flask import request
from flask import url_for
from flask import redirect
from flask import session

from passlib.hash import pbkdf2_sha256

DB_SCHEMA = """
DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""


DB_ENTRY_INSERT = """
INSERT INTO entries (title, text, created) VALUES (%s, %s, %s)
"""


# add this new SQL string below the others
DB_ENTRIES_LIST = """
SELECT id, title, text, created FROM entries ORDER BY created DESC
"""


DB_ENTRY_LIST = """
SELECT title, text, created FROM entries WHERE id = %s
"""


# update an existing entry
DB_ENTRY_UPDATE = """
UPDATE entries
SET (title, text, created) = (%s, %s, %s)
WHERE id=(%s)

"""


app = Flask(__name__)


def get_entry(entry_id):
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ENTRY_LIST, [entry_id])
    keys = ('title', 'text', 'created')
    return dict(zip(keys, cur.fetchone()))


def get_all_entries():
    """return a list of all entries as dicts"""
    con = get_database_connection()
    cur = con.cursor()
    cur.execute(DB_ENTRIES_LIST)
    keys = ('id', 'title', 'text', 'created')
    entries = cur.fetchall()
    print entries
    return [dict(zip(keys, row)) for row in entries]
# add this just below the SQL table definition we just created


def write_entry(title, text):
    if not title or not text:
        raise ValueError("Title and text required for writing an entry")
    con = get_database_connection()
    cur = con.cursor()
    now = datetime.datetime.utcnow()
    cur.execute(DB_ENTRY_INSERT, [title, text, now])


def update_entry(entry_id, title, text):
    if not title or not text:
        raise ValueError("Title and text required for updating an entry")
    con = get_database_connection()
    cur = con.cursor()
    now = datetime.datetime.utcnow()
    cur.execute(DB_ENTRY_UPDATE, (title, text, now, entry_id))


@app.route('/')
def show_entries():
    entries = get_all_entries()
    return render_template('list_entries.html', entries=entries)


@app.route('/entries/<int:entry_id>/')
def show_entry(entry_id):
    entry = get_entry(entry_id)
    return render_template('list_entry.html', entry=entry)


@app.route('/add', methods=['POST'])
def add_entry():
    try:
        write_entry(request.form['title'], request.form['text'])
    except psycopg2.Error:
        # this will catch any errors generated by the database
        abort(500)
    return redirect(url_for('show_entries'))


@app.route('/entries/<int:entry_id>/edit/', methods=['GET', 'POST'])
def edit(entry_id):
    if request.method == 'GET':
        print "in edit with entry_id: {0} and request.method: {1}".format(
            entry_id, request.method)
        # TODO what happens when edit is called and GET method?

    elif request.method == 'POST':
        print "in edit with entry_id: {0} and request.method: {1}".format(
            entry_id, request.method)
        try:
            update_entry(request.form['title'], request.form['text'])
        except psycopg2.Error:
            # this will catch any errors generated by the database
            abort(500)
        return redirect(url_for('show_entry'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        try:
            do_login(request.form['username'].encode('utf-8'),
                     request.form['password'].encode('utf-8'))
        except ValueError:
            error = "Login Failed"
        else:
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('show_entries'))

# add this after app is defined
app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=learning_journal'
)
# add the following two new settings just below
app.config['ADMIN_USERNAME'] = os.environ.get(
    'ADMIN_USERNAME', 'admin'
)
# then update the ADMIN_PASSWORD config setting:
app.config['ADMIN_PASSWORD'] = os.environ.get(
    'ADMIN_PASSWORD', pbkdf2_sha256.encrypt('admin')
)
app.config['SECRET_KEY'] = os.environ.get(
    'FLASK_SECRET_KEY', 'sooperseekritvaluenooneshouldknow'
)


# add the rest of this below the app.config statement
def connect_db():
    """Return a connection to the configured databse"""
    return psycopg2.connect(app.config['DATABASE'])


# add this function after the connect_db function
def init_db():
    """Initialize the database using DB_SCHEMA

    WARNING:  executing this function will drop existing tables.
    """

    with closing(connect_db()) as db:
        db.cursor().execute(DB_SCHEMA)
        db.commit()


# add these function after init_db
def get_database_connection():
    db = getattr(g, 'db', None)
    if db is None:
        g.db = db = connect_db()
    return db


def do_login(username='', passwd=''):
    if username != app.config['ADMIN_USERNAME']:
        raise ValueError
    if not pbkdf2_sha256.verify(passwd, app.config['ADMIN_PASSWORD']):
        raise ValueError
    session['logged_in'] = True


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        if exception and isinstance(exception, psycopg2.Error):
            # if there was a problem with the database, rollback any
            # existing transaction
            db.rollback()
        else:
            # otherwise, commit
            db.commit()
        db.close()

# put this at the very bottom of the file.
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", debug=True)
