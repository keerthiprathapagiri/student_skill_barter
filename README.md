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
│   ├── db.py               ← MySQL connection (Flask-MySQLdb)
│   └── schema.sql          ← Database tables + sample data
│
├── models/
│   ├── __init__.py
│   ├── user.py             ← User CRUD queries
│   ├── skill.py            ← Skill queries + matching algorithm
│   ├── message.py          ← Chat message queries
│   └── progress.py         ← Learning progress queries
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
| MySQL | 8.0+ |
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
pip install -r requirements.txt
```

> **Note:** If `mysqlclient` fails to install on Windows, try:
> ```bash
> pip install PyMySQL
> ```
> Then change `Flask-MySQLdb` to `flask-pymysql` in requirements and update `database/db.py` accordingly.

---

### 5. Set Up MySQL Database

Open MySQL Workbench or the MySQL CLI:

```sql
-- Run the schema file
SOURCE /path/to/student_skill_barter/database/schema.sql;

-- Or manually:
CREATE DATABASE skill_barter_db;
USE skill_barter_db;
-- then paste the contents of schema.sql
```

---

### 6. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
SECRET_KEY=your-super-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=skill_barter_db
```

If you see a login or registration error about database connection, double-check these MySQL credentials and make sure the `skill_barter_db` database is initialized.

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
- Message history stored in MySQL

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
| Database | MySQL 8 via Flask-MySQLdb |
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

**`ModuleNotFoundError: No module named 'MySQLdb'`**
→ Run: `pip install mysqlclient` (needs MySQL dev headers on Linux: `sudo apt install libmysqlclient-dev`)

**`Access denied for user 'root'@'localhost'`**
→ Check your `.env` password matches MySQL

**Socket.IO not connecting**
→ Make sure `eventlet` is installed: `pip install eventlet`

**Port 5000 already in use**
→ Change port in `app.py`: `socketio.run(app, port=5001)`

---

## 📄 License

MIT — free for personal and educational use.
