# models/message.py
# Database queries for chat messages

import MySQLdb.cursors
from database.db import commit


def _cur():
    from database.db import mysql
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)


def save_message(sender_id, receiver_id, message_text):
    """Persist a new chat message."""
    cur = _cur()
    cur.execute(
        "INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s,%s,%s)",
        (sender_id, receiver_id, message_text)
    )
    commit()
    return cur.lastrowid


def get_conversation(user_id_1, user_id_2, limit=100):
    """Return the last N messages between two users, oldest first."""
    cur = _cur()
    cur.execute("""
        SELECT m.*, u.username AS sender_name, u.avatar_color AS sender_color
        FROM messages m
        JOIN users u ON u.id = m.sender_id
        WHERE (m.sender_id=%s AND m.receiver_id=%s)
           OR (m.sender_id=%s AND m.receiver_id=%s)
        ORDER BY m.sent_at DESC
        LIMIT %s
    """, (user_id_1, user_id_2, user_id_2, user_id_1, limit))
    rows = cur.fetchall()
    return list(reversed(rows))  # return oldest-first


def mark_as_read(sender_id, receiver_id):
    """Mark messages from sender to receiver as read."""
    cur = _cur()
    cur.execute(
        "UPDATE messages SET is_read=TRUE WHERE sender_id=%s AND receiver_id=%s AND is_read=FALSE",
        (sender_id, receiver_id)
    )
    commit()


def get_unread_count(user_id):
    """Total unread messages for a user."""
    cur = _cur()
    cur.execute(
        "SELECT COUNT(*) AS cnt FROM messages WHERE receiver_id=%s AND is_read=FALSE",
        (user_id,)
    )
    row = cur.fetchone()
    return row['cnt'] if row else 0


def get_contacts(user_id):
    """
    Return users this person has had conversations with,
    along with the last message and unread count.
    """
    cur = _cur()
    cur.execute("""
        SELECT DISTINCT
            u.id, u.username, u.full_name, u.avatar_color,
            (SELECT message FROM messages
             WHERE (sender_id=u.id AND receiver_id=%s) OR (sender_id=%s AND receiver_id=u.id)
             ORDER BY sent_at DESC LIMIT 1) AS last_message,
            (SELECT COUNT(*) FROM messages
             WHERE sender_id=u.id AND receiver_id=%s AND is_read=FALSE) AS unread
        FROM messages m
        JOIN users u ON u.id = CASE WHEN m.sender_id=%s THEN m.receiver_id ELSE m.sender_id END
        WHERE m.sender_id=%s OR m.receiver_id=%s
        ORDER BY (SELECT sent_at FROM messages
                  WHERE (sender_id=u.id AND receiver_id=%s) OR (sender_id=%s AND receiver_id=u.id)
                  ORDER BY sent_at DESC LIMIT 1) DESC
    """, (user_id, user_id, user_id, user_id, user_id, user_id, user_id, user_id))
    return cur.fetchall()
