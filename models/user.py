# models/user.py
# User model and database queries

import random
from database.db import db


class User(db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text)
    avatar_color = db.Column(db.String(7), default='#4A90D9')
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Relationships
    skills = db.relationship('Skill', back_populates='user', cascade='all, delete-orphan')
    messages_sent = db.relationship(
        'Message', 
        foreign_keys='Message.sender_id',
        back_populates='sender',
        cascade='all, delete-orphan'
    )
    messages_received = db.relationship(
        'Message',
        foreign_keys='Message.receiver_id',
        back_populates='receiver',
        cascade='all, delete-orphan'
    )
    learning = db.relationship(
        'LearningProgress',
        foreign_keys='LearningProgress.learner_id',
        back_populates='learner',
        cascade='all, delete-orphan'
    )
    teaching = db.relationship(
        'LearningProgress',
        foreign_keys='LearningProgress.teacher_id',
        back_populates='teacher',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'full_name': self.full_name,
            'username': self.username,
            'bio': self.bio,
            'avatar_color': self.avatar_color,
        }


class DatabaseError(Exception):
    """Raised when a database operation fails."""
    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original


# ────────────────────────────────────────────────────────────────────────
# CRUD Operations
# ────────────────────────────────────────────────────────────────────────

def create_user(full_name, username, hashed_password):
    """Insert a new user; returns the new user id."""
    try:
        colors = ['#E74C3C','#2ECC71','#9B59B6','#E67E22','#1ABC9C','#3498DB','#F39C12','#E91E63']
        color = random.choice(colors)
        
        new_user = User(
            full_name=full_name,
            username=username,
            password=hashed_password,
            avatar_color=color
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user.id
    except Exception as exc:
        db.session.rollback()
        raise DatabaseError(f"Database error creating user: {exc}", original=exc)


def get_user_by_username(username):
    """Fetch a user by username (or None)."""
    try:
        return User.query.filter_by(username=username).first()
    except Exception as exc:
        raise DatabaseError(f"Database error fetching user: {exc}", original=exc)


def get_user_by_id(user_id):
    """Fetch a user by primary key (or None)."""
    try:
        return User.query.get(user_id)
    except Exception as exc:
        raise DatabaseError(f"Database error fetching user: {exc}", original=exc)


def update_bio(user_id, bio):
    """Update user bio."""
    try:
        user = User.query.get(user_id)
        if user:
            user.bio = bio
            db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise DatabaseError(f"Database error updating bio: {exc}", original=exc)


def username_exists(username):
    """Check if username already exists."""
    try:
        return User.query.filter_by(username=username).first() is not None
    except Exception as exc:
        raise DatabaseError(f"Database error checking username: {exc}", original=exc)


def get_all_users_except(user_id):
    """Return all users except the given one (for discovery)."""
    try:
        return User.query.filter(User.id != user_id).all()
    except Exception as exc:
        raise DatabaseError(f"Database error fetching users: {exc}", original=exc)

