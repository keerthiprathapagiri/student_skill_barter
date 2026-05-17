# routes/chat.py
# HTTP routes for the chat page + SocketIO event handlers

from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from flask_socketio import emit, join_room, leave_room
from models.user    import get_user_by_id, get_user_by_username
from models.message import save_message, get_conversation, mark_as_read, get_contacts, get_unread_count
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

# SocketIO instance will be set by app.py after init
socketio = None


def init_socketio(sio):
    global socketio
    socketio = sio

    # ── Socket events ─────────────────────────────────────────────────────────

    @sio.on('join')
    def on_join(data):
        """Client joins a private room named after the sorted pair of user IDs."""
        room = _room(data['sender_id'], data['receiver_id'])
        join_room(room)

    @sio.on('send_message')
    def on_send_message(data):
        """Receive a message and broadcast it to the private room."""
        sender_id   = data.get('sender_id')
        receiver_id = data.get('receiver_id')
        message     = data.get('message', '').strip()

        if not (sender_id and receiver_id and message):
            return

        # Persist to DB
        msg_id = save_message(sender_id, receiver_id, message)

        # Lookup sender info for display
        sender = get_user_by_id(sender_id)

        # Broadcast to room
        room = _room(sender_id, receiver_id)
        emit('receive_message', {
            'id':          msg_id,
            'sender_id':   sender_id,
            'receiver_id': receiver_id,
            'sender_name': sender['username'] if sender else 'Unknown',
            'sender_color': sender['avatar_color'] if sender else '#4A90D9',
            'message':     message,
            'sent_at':     datetime.now().strftime('%H:%M'),
        }, room=room)

    @sio.on('typing')
    def on_typing(data):
        room = _room(data['sender_id'], data['receiver_id'])
        emit('user_typing', {'username': data.get('username', '')}, room=room, include_self=False)

    @sio.on('stop_typing')
    def on_stop_typing(data):
        room = _room(data['sender_id'], data['receiver_id'])
        emit('user_stop_typing', {}, room=room, include_self=False)

    @sio.on('mark_read')
    def on_mark_read(data):
        mark_as_read(data['sender_id'], data['receiver_id'])


def _room(uid1, uid2):
    """Deterministic room name for two user IDs."""
    return f"chat_{min(uid1, uid2)}_{max(uid1, uid2)}"


# ── HTTP routes ───────────────────────────────────────────────────────────────

@chat_bp.route('/chat')
def chat_list():
    if 'user_id' not in session:
        flash('Please log in to use chat.', 'info')
        return redirect(url_for('auth.login'))
    user     = get_user_by_id(session['user_id'])
    contacts = get_contacts(session['user_id'])
    unread   = get_unread_count(session['user_id'])
    return render_template('chat.html', user=user, contacts=contacts, unread=unread, active_chat=None)


@chat_bp.route('/chat/<username>')
def chat_with(username):
    if 'user_id' not in session:
        flash('Please log in to use chat.', 'info')
        return redirect(url_for('auth.login'))

    target = get_user_by_username(username)
    if not target:
        flash('User not found.', 'error')
        return redirect(url_for('chat.chat_list'))

    user         = get_user_by_id(session['user_id'])
    contacts     = get_contacts(session['user_id'])
    messages     = get_conversation(session['user_id'], target['id'])
    unread       = get_unread_count(session['user_id'])

    # Mark incoming messages as read
    mark_as_read(target['id'], session['user_id'])

    return render_template('chat.html',
                           user=user,
                           contacts=contacts,
                           messages=messages,
                           active_chat=target,
                           unread=unread)
