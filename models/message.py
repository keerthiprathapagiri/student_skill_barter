# models/message.py
# Message model and database queries

from database.db import db
from sqlalchemy import and_, or_, case, desc


class Message(db.Model):
    """Message model - represents chat messages between users."""
    
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    message = db.Column(db.Text, nullable=False)

    is_read = db.Column(
        db.Boolean,
        default=False
    )

    sent_at = db.Column(
        db.DateTime,
        default=db.func.now()
    )

    # Relationships
    sender = db.relationship(
        'User',
        foreign_keys=[sender_id],
        back_populates='messages_sent'
    )

    receiver = db.relationship(
        'User',
        foreign_keys=[receiver_id],
        back_populates='messages_received'
    )

    def to_dict(self):
        """Convert message to dictionary."""

        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': self.message,
            'is_read': self.is_read,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'sender_name': self.sender.username if self.sender else None,
            'sender_color': self.sender.avatar_color if self.sender else '#4A90D9',
        }


# ─────────────────────────────────────────────────────────────
# Message Operations
# ─────────────────────────────────────────────────────────────

def save_message(sender_id, receiver_id, message_text):
    """Save a new message."""

    try:
        new_message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=message_text
        )

        db.session.add(new_message)
        db.session.commit()

        return new_message.id

    except Exception as exc:
        db.session.rollback()
        raise Exception(f"Error saving message: {exc}")


def get_conversation(user_id_1, user_id_2, limit=100):
    """Get conversation between two users."""

    try:
        messages = Message.query.filter(
            or_(
                and_(
                    Message.sender_id == user_id_1,
                    Message.receiver_id == user_id_2
                ),
                and_(
                    Message.sender_id == user_id_2,
                    Message.receiver_id == user_id_1
                )
            )
        ).order_by(Message.sent_at.asc()).limit(limit).all()

        return [msg.to_dict() for msg in messages]

    except Exception as exc:
        raise Exception(f"Error fetching conversation: {exc}")


def mark_as_read(sender_id, receiver_id):
    """Mark messages as read."""

    try:
        messages = Message.query.filter(
            Message.sender_id == sender_id,
            Message.receiver_id == receiver_id,
            Message.is_read == False
        ).all()

        for msg in messages:
            msg.is_read = True

        db.session.commit()

    except Exception as exc:
        db.session.rollback()
        raise Exception(f"Error marking messages as read: {exc}")


def get_unread_count(user_id):
    """Get total unread messages."""

    try:
        return Message.query.filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()

    except Exception as exc:
        raise Exception(f"Error counting unread messages: {exc}")


def get_contacts(user_id):
    """
    Get all chat contacts for a user.
    Includes last message and unread count.
    """

    try:
        from models.user import User

        # CASE expression to determine contact id
        contact_case = case(
            (Message.sender_id == user_id, Message.receiver_id),
            else_=Message.sender_id
        )

        # Get unique contacts ordered by latest message
        contact_data = db.session.query(
            contact_case.label('contact_id'),
            db.func.max(Message.sent_at).label('last_sent_at')
        ).filter(
            or_(
                Message.sender_id == user_id,
                Message.receiver_id == user_id
            )
        ).group_by(
            contact_case
        ).order_by(
            desc('last_sent_at')
        ).all()

        contacts = []

        for contact_id, last_sent_at in contact_data:

            if not contact_id:
                continue

            user = User.query.get(contact_id)

            if not user:
                continue

            # Get latest message
            latest_message = Message.query.filter(
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == contact_id
                    ),
                    and_(
                        Message.sender_id == contact_id,
                        Message.receiver_id == user_id
                    )
                )
            ).order_by(
                Message.sent_at.desc()
            ).first()

            # Count unread messages
            unread_count = Message.query.filter(
                Message.sender_id == contact_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).count()

            contacts.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'avatar_color': user.avatar_color,
                'last_message': latest_message.message if latest_message else '',
                'last_sent_at': latest_message.sent_at.isoformat() if latest_message else None,
                'unread': unread_count
            })

        return contacts

    except Exception as exc:
        raise Exception(f"Error fetching contacts: {exc}")