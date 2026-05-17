# models/skill.py
# Database queries for skills (offered / needed)

import MySQLdb.cursors
from database.db import commit


def _cur():
    from database.db import mysql
    return mysql.connection.cursor(MySQLdb.cursors.DictCursor)


def add_skill(user_id, skill_name, skill_type):
    """Add a skill (offered or needed) for a user."""
    cur = _cur()
    # Avoid duplicates
    cur.execute(
        "SELECT id FROM skills WHERE user_id=%s AND skill_name=%s AND skill_type=%s",
        (user_id, skill_name.strip(), skill_type)
    )
    if cur.fetchone():
        return  # already exists
    cur.execute(
        "INSERT INTO skills (user_id, skill_name, skill_type) VALUES (%s,%s,%s)",
        (user_id, skill_name.strip(), skill_type)
    )
    commit()


def delete_skill(skill_id, user_id):
    """Remove a skill row (owner check for safety)."""
    cur = _cur()
    cur.execute("DELETE FROM skills WHERE id=%s AND user_id=%s", (skill_id, user_id))
    commit()


def get_skills_for_user(user_id):
    """Returns {'offered': [...], 'needed': [...]}."""
    cur = _cur()
    cur.execute("SELECT * FROM skills WHERE user_id = %s ORDER BY created_at", (user_id,))
    rows = cur.fetchall()
    return {
        'offered': [r for r in rows if r['skill_type'] == 'offered'],
        'needed':  [r for r in rows if r['skill_type'] == 'needed'],
    }


def search_users_by_skill(search_term, exclude_user_id=None):
    """
    Matching logic:
      Find users whose OFFERED skills contain the search term.
      Optionally exclude the requesting user.
    Returns a list of dicts: {user, offered_skills, needed_skills}
    """
    cur = _cur()
    like = f"%{search_term}%"

    if exclude_user_id:
        cur.execute("""
            SELECT DISTINCT u.id, u.full_name, u.username, u.bio, u.avatar_color
            FROM users u
            JOIN skills s ON s.user_id = u.id
            WHERE s.skill_type = 'offered'
              AND s.skill_name LIKE %s
              AND u.id != %s
        """, (like, exclude_user_id))
    else:
        cur.execute("""
            SELECT DISTINCT u.id, u.full_name, u.username, u.bio, u.avatar_color
            FROM users u
            JOIN skills s ON s.user_id = u.id
            WHERE s.skill_type = 'offered'
              AND s.skill_name LIKE %s
        """, (like,))

    users = cur.fetchall()

    # Attach skills to each match
    results = []
    for user in users:
        uid = user['id']
        cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='offered'", (uid,))
        offered = [r['skill_name'] for r in cur.fetchall()]
        cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='needed'", (uid,))
        needed = [r['skill_name'] for r in cur.fetchall()]
        results.append({**user, 'offered_skills': offered, 'needed_skills': needed})

    return results


def get_suggested_matches(user_id):
    """
    Smart matching: find users who offer what this user needs,
    OR need what this user offers.
    """
    cur = _cur()
    # What does the current user need?
    cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='needed'", (user_id,))
    my_needs = [r['skill_name'] for r in cur.fetchall()]

    # What does the current user offer?
    cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='offered'", (user_id,))
    my_offers = [r['skill_name'] for r in cur.fetchall()]

    if not my_needs and not my_offers:
        return []

    matched_ids = set()
    results = []

    # Forward match: find users who offer what I need
    for skill in my_needs:
        like = f"%{skill}%"
        cur.execute("""
            SELECT DISTINCT u.id, u.full_name, u.username, u.bio, u.avatar_color
            FROM users u JOIN skills s ON s.user_id=u.id
            WHERE s.skill_type='offered' AND s.skill_name LIKE %s AND u.id != %s
        """, (like, user_id))
        for row in cur.fetchall():
            if row['id'] not in matched_ids:
                matched_ids.add(row['id'])
                results.append(row)

    # Reverse match: find users who need what I offer
    for skill in my_offers:
        like = f"%{skill}%"
        cur.execute("""
            SELECT DISTINCT u.id, u.full_name, u.username, u.bio, u.avatar_color
            FROM users u JOIN skills s ON s.user_id=u.id
            WHERE s.skill_type='needed' AND s.skill_name LIKE %s AND u.id != %s
        """, (like, user_id))
        for row in cur.fetchall():
            if row['id'] not in matched_ids:
                matched_ids.add(row['id'])
                results.append(row)

    # Attach full skill lists
    enriched = []
    for user in results:
        uid = user['id']
        cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='offered'", (uid,))
        offered = [r['skill_name'] for r in cur.fetchall()]
        cur.execute("SELECT skill_name FROM skills WHERE user_id=%s AND skill_type='needed'", (uid,))
        needed = [r['skill_name'] for r in cur.fetchall()]
        enriched.append({**user, 'offered_skills': offered, 'needed_skills': needed})

    return enriched
