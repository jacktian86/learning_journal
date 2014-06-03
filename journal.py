# add this import at the top of your file:
import os
import psycopg2
from contextlib import closing

# -*- coding: utf-8 -*-
from flask import Flask

DB_SCHEMA = """
DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
    id serial PRIMARY KEY,
    title VARCHAR (127) NOT NULL,
    text TEXT NOT NULL,
    created TIMESTAMP NOT NULL
)
"""

# add this just below the SQL table definition we just created
app = Flask(__name__)


@app.route('/')
def hello():
    return u'Hello world!'


# add this after app is defined
app.config['DATABASE'] = os.environ.get(
    'DATABASE_URL', 'dbname=learning_journal'
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


# put this at the very bottom of the file.
if __name__ == '__main__':
    app.run(debug=True)
