# ⚡ Student Skill Barter

A full-stack web platform where students can **trade skills** with each other — teach what you know, learn what you need, and connect in real time.

---

## 🗂️ Project Structure

```
student_skill_barter/
├── app.py                  ← Flask entry point + SocketIO init
├── requirements.txt        ← Python dependencies
├── .env.example            ← Environment variable template
│
├── database/
│   ├── __init__.py
│   ├── db.py               ← PostgreSQL connection (Flask-SQLAlchemy)
│   └── schema.sql          ← Database tables (reference only)
│
├── models/
│   ├── __init__.py
│   ├── user.py             ← User model + CRUD queries
│   ├── skill.py            ← Skill model + matching algorithm
│   ├── message.py          ← Message model + chat queries
│   └── progress.py         ← LearningProgress model + queries
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             ← Login / Register / Logout
│   ├── main.py             ← Home, Profile, Skills, Search APIs
│   └── chat.py             ← Chat HTTP routes + Socket.IO events
│
├── templates/
│   ├── base.html           ← Shared layout with navbar + footer
│   ├── index.html          ← Home / hero / search / matches
│   ├── login.html          ← Login page (sky-blue)
│   ├── register.html       ← Register page (blue + validation)
│   ├── profile.html        ← User profile page
│   ├── chat.html           ← Real-time chat interface
│   ├── user_profile.html   ← Public view of another user
│   └── contact.html        ← Contact page
│
└── static/
    ├── css/
    │   ├── main.css         ← Global design system
    │   ├── auth.css         ← Login / register styles
    │   └── chat.css         ← Chat layout styles
    └── js/
        ├── main.js          ← Navbar, flash, password toggle
        ├── register.js      ← Registration validation
        ├── search.js        ← Live skill search + card render
        └── chat.js          ← Socket.IO real-time messaging
```

---

## 🚀 Setup Instructions

### 1. Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| PostgreSQL | 12+ |
| pip | latest |

---

### 2. Clone / Download the Project

```bash
# If using git
git clone <repo-url>
cd student_skill_barter

# Or extract the ZIP and cd into the folder
```

---

### 3. Create a Python Virtual Environment

```bash
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

---

### 4. Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

---

### 5. Set Up PostgreSQL Database

Install PostgreSQL (if not already installed), then:

```bash
# Create database via psql CLI
psql -U postgres

# In psql prompt:
CREATE DATABASE skill_barter_db;
\q
```

---

### 6. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/skill_barter_db
```

For **Render deployment**:
- Add `DATABASE_URL` as an environment variable in the Render dashboard
- Render automatically converts `postgres://` to `postgresql://` (our app handles both)

---

### 7. Run the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## ✨ Features

### 🔐 Authentication
- Secure registration with password hashing (bcrypt via Werkzeug)
- Client-side validation (password match, strength meter)
- Session-based authentication

### 👤 Profiles
- Avatar with auto-assigned color
- Bio editing
- Offered & needed skill management (add/remove)
- Learning progress tracker

### 🤝 Smart Skill Matching
- **Forward match**: Find users who offer what you need
- **Reverse match**: Find users who need what you offer
- Live search bar (debounced AJAX)

### 💬 Real-Time Chat
- Socket.IO powered instant messaging
- Typing indicators
- Unread message badges
- Message history stored in PostgreSQL

### 🎨 UI/UX
- Dark mode design system with sky-blue accents
- Fully responsive (mobile hamburger menu)
- Animated hero section
- Hover effects on cards
- Flash notifications with auto-dismiss

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Backend | Python Flask 3.0 |
| Real-time | Flask-SocketIO + Socket.IO |
| Database | PostgreSQL 12+ via Flask-SQLAlchemy |
| Auth | Werkzeug password hashing |
| Fonts | Syne + DM Sans (Google Fonts) |

---

## 📡 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Home page |
| GET/POST | `/register` | Register new user |
| GET/POST | `/login` | Login |
| GET | `/logout` | Logout |
| GET | `/profile` | My profile |
| POST | `/profile/update` | Update bio |
| POST | `/skills/add` | Add skill |
| POST | `/skills/delete/<id>` | Remove skill |
| GET | `/api/search?q=<skill>` | Search users by skill (JSON) |
| GET | `/api/matches` | Get suggested matches (JSON) |
| GET | `/user/<username>` | View public profile |
| GET | `/chat` | Chat list |
| GET | `/chat/<username>` | Chat with user |
| GET | `/contact` | Contact page |

### Socket.IO Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `join` | Client→Server | Join a private chat room |
| `send_message` | Client→Server | Send a message |
| `receive_message` | Server→Client | Broadcast message to room |
| `typing` | Client→Server | User is typing |
| `stop_typing` | Client→Server | User stopped typing |
| `user_typing` | Server→Client | Show typing indicator |
| `user_stop_typing` | Server→Client | Hide typing indicator |
| `mark_read` | Client→Server | Mark messages as read |

---

## 🐛 Troubleshooting

**`ModuleNotFoundError: No module named 'psycopg2'`**
→ Run: `python -m pip install psycopg2-binary`

**`connection to server at "localhost"... failed`**
→ Check PostgreSQL is running and DATABASE_URL is correct in `.env`

**`psycopg2.OperationalError: FATAL: role "postgres" does not exist`**
→ Update DATABASE_URL with correct PostgreSQL credentials

**Socket.IO not connecting**
→ Make sure `eventlet` is installed: `python -m pip install eventlet`

**Port 5000 already in use**
→ Change port in `app.py`: `socketio.run(app, port=5001)`

**Tables not created automatically**
→ The app should create tables automatically on first run. If not, check DATABASE_URL is valid.

---

## 📄 License

MIT — free for personal and educational use.
