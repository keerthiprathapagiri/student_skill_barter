# models/skill.py
# Skill model and database queries

from database.db import db
from sqlalchemy import and_, or_


class Skill(db.Model):
    """Skill model - represents offered or needed skills."""
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    skill_type = db.Column(db.String(20), nullable=False)  # 'offered' or 'needed'
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    user = db.relationship('User', back_populates='skills')

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'skill_name': self.skill_name,
            'skill_type': self.skill_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


# ────────────────────────────────────────────────────────────────────────
# Skill Operations
# ────────────────────────────────────────────────────────────────────────

def add_skill(user_id, skill_name, skill_type):
    """Add a skill (offered or needed) for a user."""
    try:
        # Avoid duplicates
        existing = Skill.query.filter_by(
            user_id=user_id,
            skill_name=skill_name.strip(),
            skill_type=skill_type
        ).first()
        
        if existing:
            return  # already exists
        
        new_skill = Skill(
            user_id=user_id,
            skill_name=skill_name.strip(),
            skill_type=skill_type
        )
        db.session.add(new_skill)
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise Exception(f"Error adding skill: {exc}")


def delete_skill(skill_id, user_id):
    """Remove a skill row (owner check for safety)."""
    try:
        skill = Skill.query.filter_by(id=skill_id, user_id=user_id).first()
        if skill:
            db.session.delete(skill)
            db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise Exception(f"Error deleting skill: {exc}")


def get_skills_for_user(user_id):
    """Returns {'offered': [...], 'needed': [...]}."""
    try:
        skills = Skill.query.filter_by(user_id=user_id).order_by(Skill.created_at).all()
        return {
            'offered': [s.to_dict() for s in skills if s.skill_type == 'offered'],
            'needed': [s.to_dict() for s in skills if s.skill_type == 'needed'],
        }
    except Exception as exc:
        raise Exception(f"Error fetching skills: {exc}")


def search_users_by_skill(search_term, exclude_user_id=None):
    """
    Matching logic:
      Find users whose OFFERED skills contain the search term.
      Optionally exclude the requesting user.
    Returns a list of dicts: {user, offered_skills, needed_skills}
    """
    try:
        from models.user import User
        
        like_term = f"%{search_term}%"
        
        # Find users whose offered skills match the search term
        query = db.session.query(User).distinct()
        query = query.join(Skill)
        query = query.filter(
            and_(
                Skill.skill_type == 'offered',
                Skill.skill_name.ilike(like_term)
            )
        )
        
        if exclude_user_id:
            query = query.filter(User.id != exclude_user_id)
        
        users = query.all()
        
        # Attach skills to each user
        results = []
        for user in users:
            offered_skills = [s.skill_name for s in user.skills if s.skill_type == 'offered']
            needed_skills = [s.skill_name for s in user.skills if s.skill_type == 'needed']
            
            user_dict = user.to_dict()
            user_dict['offered_skills'] = offered_skills
            user_dict['needed_skills'] = needed_skills
            results.append(user_dict)
        
        return results
    except Exception as exc:
        raise Exception(f"Error searching skills: {exc}")


def get_suggested_matches(user_id):
    """
    Smart matching: find users who offer what this user needs,
    OR need what this user offers.
    """
    try:
        from models.user import User
        
        # What does the current user need?
        my_needs = Skill.query.filter_by(
            user_id=user_id,
            skill_type='needed'
        ).all()
        my_need_names = [s.skill_name for s in my_needs]
        
        # What does the current user offer?
        my_offers = Skill.query.filter_by(
            user_id=user_id,
            skill_type='offered'
        ).all()
        my_offer_names = [s.skill_name for s in my_offers]
        
        if not (my_need_names or my_offer_names):
            return []
        
        # Find potential matches
        matches = []
        
        if my_need_names:
            # Users who offer what I need
            query1 = db.session.query(User).distinct()
            query1 = query1.join(Skill)
            query1 = query1.filter(
                and_(
                    Skill.skill_type == 'offered',
                    Skill.skill_name.in_(my_need_names),
                    User.id != user_id
                )
            )
            matches.extend(query1.all())
        
        if my_offer_names:
            # Users who need what I offer
            query2 = db.session.query(User).distinct()
            query2 = query2.join(Skill)
            query2 = query2.filter(
                and_(
                    Skill.skill_type == 'needed',
                    Skill.skill_name.in_(my_offer_names),
                    User.id != user_id
                )
            )
            for user in query2.all():
                if user not in matches:
                    matches.append(user)
        
        # Deduplicate and convert to dicts
        unique_matches = []
        seen_ids = set()
        for user in matches:
            if user.id not in seen_ids:
                seen_ids.add(user.id)
                offered_skills = [s.skill_name for s in user.skills if s.skill_type == 'offered']
                needed_skills = [s.skill_name for s in user.skills if s.skill_type == 'needed']
                
                user_dict = user.to_dict()
                user_dict['offered_skills'] = offered_skills
                user_dict['needed_skills'] = needed_skills
                unique_matches.append(user_dict)
        
        return unique_matches
    except Exception as exc:
        raise Exception(f"Error getting suggested matches: {exc}")


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
