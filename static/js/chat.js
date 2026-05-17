// static/js/chat.js
// Real-time chat powered by Socket.IO

// Guard: only run if we're in an active chat
if (typeof RECEIVER_ID !== 'undefined' && RECEIVER_ID !== null) {

    // ── Connect to Socket.IO ─────────────────────────────────────
    const socket = io({ transports: ['websocket', 'polling'] });

    socket.on('connect', () => {
        // Join the private chat room
        socket.emit('join', {
            sender_id:   CURRENT_USER_ID,
            receiver_id: RECEIVER_ID,
        });
    });

    // ── Receive a message ────────────────────────────────────────
    socket.on('receive_message', (data) => {
        appendMessage(data);
        scrollToBottom();
        // Mark as read if visible
        if (document.hasFocus() && data.sender_id !== CURRENT_USER_ID) {
            socket.emit('mark_read', {
                sender_id:   data.sender_id,
                receiver_id: CURRENT_USER_ID,
            });
        }
    });

    // ── Typing indicators ─────────────────────────────────────────
    let typingTimeout;
    const indicator = document.getElementById('typingIndicator');

    document.getElementById('messageInput')?.addEventListener('input', () => {
        socket.emit('typing', {
            sender_id:   CURRENT_USER_ID,
            receiver_id: RECEIVER_ID,
            username:    CURRENT_USERNAME,
        });
        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(() => {
            socket.emit('stop_typing', {
                sender_id:   CURRENT_USER_ID,
                receiver_id: RECEIVER_ID,
            });
        }, 1500);
    });

    socket.on('user_typing',      () => { if (indicator) indicator.style.display = 'flex'; scrollToBottom(); });
    socket.on('user_stop_typing', () => { if (indicator) indicator.style.display = 'none'; });

    // ── Send on Enter ─────────────────────────────────────────────
    document.getElementById('messageInput')?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // ── Send message ─────────────────────────────────────────────
    window.sendMessage = function () {
        const input = document.getElementById('messageInput');
        const msg   = input?.value?.trim();
        if (!msg) return;

        socket.emit('send_message', {
            sender_id:   CURRENT_USER_ID,
            receiver_id: RECEIVER_ID,
            message:     msg,
        });

        input.value = '';
        // Clear typing indicator
        socket.emit('stop_typing', { sender_id: CURRENT_USER_ID, receiver_id: RECEIVER_ID });
    };
}

// ── Append a message bubble to the DOM ───────────────────────────
function appendMessage(data) {
    const area = document.getElementById('messagesArea');
    if (!area) return;

    // Remove the "start hint" if present
    const hint = area.querySelector('.chat-start-hint');
    if (hint) hint.remove();

    const isOwn = data.sender_id === CURRENT_USER_ID;
    const div   = document.createElement('div');
    div.className = `message ${isOwn ? 'message-out' : 'message-in'}`;
    div.innerHTML = `
        <div class="bubble">${escHtml(data.message)}</div>
        <span class="msg-time">${data.sent_at || nowTime()}</span>
    `;
    area.appendChild(div);
}

// ── Scroll the messages area to the bottom ───────────────────────
function scrollToBottom() {
    const area = document.getElementById('messagesArea');
    if (area) area.scrollTop = area.scrollHeight;
}

// ── Helpers ─────────────────────────────────────────────────────
function nowTime() {
    const d = new Date();
    return `${String(d.getHours()).padStart(2,'0')}:${String(d.getMinutes()).padStart(2,'0')}`;
}
function escHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g,'&amp;')
        .replace(/</g,'&lt;')
        .replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;');
}

// ── Scroll to bottom on page load ───────────────────────────────
document.addEventListener('DOMContentLoaded', scrollToBottom);
