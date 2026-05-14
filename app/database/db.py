import mysql.connector
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            database=current_app.config['MYSQL_DB']
        )
        g.db.autocommit = True
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    with current_app.open_resource('database/schema.sql') as f:
        # Split by command terminator and execute
        statements = f.read().decode('utf8').split(';')
        for statement in statements:
            if statement.strip():
                cursor.execute(statement)
    db.commit()

def init_app(app):
    app.teardown_appcontext(close_db)
    # Add CLI command if needed, or run init_db logic here
