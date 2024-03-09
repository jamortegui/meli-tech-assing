import click
from flask import current_app, g

from .db import get_db_connection


def get_db():
    # Retrieves the active db connection from the current request
    if 'db' not in g:
        g.db = get_db_connection(current_app.config['DATABASE'])

    return g.db


def close_db(e=None):
    # Closes the active db connection from the current request
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    # Excecutes the SQL to create the database tables as empty tables
    db = get_db()

    with current_app.open_resource(current_app.config["INIT_SCHEMA"]) as f:
        cursor = db.cursor()
        cursor.execute(f.read().decode('utf8'))
        db.commit()
        db.close()


@click.command('init-db')
def init_db_command():
    # Clear the existing data and create new tables
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    # Registers commands in Flask app
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
