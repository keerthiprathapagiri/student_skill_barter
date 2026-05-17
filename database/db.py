# database/db.py
# Handles MySQL connection using Flask-MySQLdb
# Configure your credentials in .env or config.py

from flask_mysqldb import MySQL

mysql = MySQL()  # initialized in app.py via init_app()


def get_cursor():
    """Return a DictCursor so rows come back as dicts, not tuples."""
    return mysql.connection.cursor()


def commit():
    """Shortcut to commit a transaction."""
    mysql.connection.commit()
