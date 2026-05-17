# models/progress.py
# Learning progress tracking

import MySQLdb.cursors
from database.db import commit


def _cur():
    from database.db import mysql
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)


def upsert_progress(learner_id, teacher_id, skill_name, progress_pct, notes=''):
    """Insert or update a learning progress record."""
    cur = _cur()
    cur.execute("""
        SELECT id FROM learning_progress
        WHERE learner_id=%s AND teacher_id=%s AND skill_name=%s
    """, (learner_id, teacher_id, skill_name))
    row = cur.fetchone()
    if row:
        cur.execute("""
            UPDATE learning_progress
            SET progress_pct=%s, notes=%s
            WHERE id=%s
        """, (progress_pct, notes, row['id']))
    else:
        cur.execute("""
            INSERT INTO learning_progress (learner_id, teacher_id, skill_name, progress_pct, notes)
            VALUES (%s,%s,%s,%s,%s)
        """, (learner_id, teacher_id, skill_name, progress_pct, notes))
    commit()


def get_my_learning(learner_id):
    """What am I currently learning and from whom?"""
    cur = _cur()
    cur.execute("""
        SELECT lp.*, u.username AS teacher_name, u.full_name AS teacher_full_name, u.avatar_color
        FROM learning_progress lp
        JOIN users u ON u.id = lp.teacher_id
        WHERE lp.learner_id = %s
        ORDER BY lp.updated_at DESC
    """, (learner_id,))
    return cur.fetchall()


def get_my_teaching(teacher_id):
    """Who am I currently teaching?"""
    cur = _cur()
    cur.execute("""
        SELECT lp.*, u.username AS learner_name, u.full_name AS learner_full_name, u.avatar_color
        FROM learning_progress lp
        JOIN users u ON u.id = lp.learner_id
        WHERE lp.teacher_id = %s
        ORDER BY lp.updated_at DESC
    """, (teacher_id,))
    return cur.fetchall()
