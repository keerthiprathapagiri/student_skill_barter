# models/user.py
# All database queries related to users

from database.db import get_cursor, commit
import MySQLdb
import MySQLdb.cursors


class DatabaseError(Exception):
    """Raised when a database operation fails."""
    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


# ---------- helpers ----------

def _dict_cursor():
    """Return a cursor that yields rows as plain dicts."""
    from database.db import mysql
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)


# ---------- CRUD ----------

def create_user(full_name, username, hashed_password):
    """Insert a new user; returns the new row id."""
    import random
    colors = ['#E74C3C','#2ECC71','#9B59B6','#E67E22','#1ABC9C','#3498DB','#F39C12','#E91E63']
    color = random.choice(colors)

    try:
        cur = _dict_cursor()
        cur.execute(
            "INSERT INTO users (full_name, username, password, avatar_color) VALUES (%s,%s,%s,%s)",
            (full_name, username, hashed_password, color)
        )
        commit()
        return cur.lastrowid
    except MySQLdb.Error as exc:
        raise DatabaseError(f"Database error creating user: {exc}", original=exc)


def get_user_by_username(username):
    """Fetch a user row by username (or None)."""
    try:
        cur = _dict_cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cur.fetchone()
    except MySQLdb.Error as exc:
        raise DatabaseError(f"Database error fetching user: {exc}", original=exc)


def get_user_by_id(user_id):
    """Fetch a user row by primary key (or None)."""
    cur = _dict_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    return cur.fetchone()


def update_bio(user_id, bio):
    cur = _dict_cursor()
    cur.execute("UPDATE users SET bio = %s WHERE id = %s", (bio, user_id))
    commit()


def username_exists(username):
    try:
        cur = _dict_cursor()
        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        return cur.fetchone() is not None
    except MySQLdb.Error as exc:
        raise DatabaseError(f"Database error checking username: {exc}", original=exc)


def get_all_users_except(user_id):
    """Return all users except the given one (for discovery)."""
    cur = _dict_cursor()
    cur.execute("SELECT * FROM users WHERE id != %s", (user_id,))
    return cur.fetchall()
