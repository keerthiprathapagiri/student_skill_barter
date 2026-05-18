# models/progress.py
# Learning progress tracking model

from database.db import db


class LearningProgress(db.Model):
    """Learning progress model - tracks what users are learning."""
    __tablename__ = 'learning_progress'

    id = db.Column(db.Integer, primary_key=True)
    learner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    progress_pct = db.Column(db.Integer, default=0)  # 0-100
    notes = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Relationships
    learner = db.relationship('User', foreign_keys=[learner_id], back_populates='learning')
    teacher = db.relationship('User', foreign_keys=[teacher_id], back_populates='teaching')

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'learner_id': self.learner_id,
            'teacher_id': self.teacher_id,
            'skill_name': self.skill_name,
            'progress_pct': self.progress_pct,
            'notes': self.notes,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'teacher_name': self.teacher.username if self.teacher else None,
            'teacher_full_name': self.teacher.full_name if self.teacher else None,
            'teacher_color': self.teacher.avatar_color if self.teacher else None,
        }


# ────────────────────────────────────────────────────────────────────────
# Learning Progress Operations
# ────────────────────────────────────────────────────────────────────────

def upsert_progress(learner_id, teacher_id, skill_name, progress_pct, notes=''):
    """Insert or update a learning progress record."""
    try:
        progress = LearningProgress.query.filter_by(
            learner_id=learner_id,
            teacher_id=teacher_id,
            skill_name=skill_name
        ).first()
        
        if progress:
            progress.progress_pct = progress_pct
            progress.notes = notes
        else:
            progress = LearningProgress(
                learner_id=learner_id,
                teacher_id=teacher_id,
                skill_name=skill_name,
                progress_pct=progress_pct,
                notes=notes
            )
            db.session.add(progress)
        
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise Exception(f"Error upserting progress: {exc}")


def get_my_learning(learner_id):
    """What am I currently learning and from whom?"""
    try:
        progress_records = LearningProgress.query.filter_by(learner_id=learner_id).order_by(
            LearningProgress.updated_at.desc()
        ).all()
        
        return [
            {
                'id': p.id,
                'skill_name': p.skill_name,
                'progress_pct': p.progress_pct,
                'notes': p.notes,
                'teacher_id': p.teacher_id,
                'teacher_name': p.teacher.username if p.teacher else None,
                'teacher_full_name': p.teacher.full_name if p.teacher else None,
                'avatar_color': p.teacher.avatar_color if p.teacher else None,
            }
            for p in progress_records
        ]
    except Exception as exc:
        raise Exception(f"Error fetching learning progress: {exc}")


def get_my_teaching(teacher_id):
    """Who am I currently teaching?"""
    try:
        progress_records = LearningProgress.query.filter_by(teacher_id=teacher_id).order_by(
            LearningProgress.updated_at.desc()
        ).all()
        
        return [
            {
                'id': p.id,
                'skill_name': p.skill_name,
                'progress_pct': p.progress_pct,
                'notes': p.notes,
                'learner_id': p.learner_id,
                'learner_name': p.learner.username if p.learner else None,
                'learner_full_name': p.learner.full_name if p.learner else None,
                'avatar_color': p.learner.avatar_color if p.learner else None,
            }
            for p in progress_records
        ]
    except Exception as exc:
        raise Exception(f"Error fetching teaching progress: {exc}")

