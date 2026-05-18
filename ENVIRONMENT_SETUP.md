# Environment Setup Guide

This guide explains how to set up your environment for local development and Render deployment.

---

## Local Development Setup

### 1. Install PostgreSQL

**Windows**:
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Run installer, remember the password for `postgres` user
- PostgreSQL will run on `localhost:5432` by default

**macOS** (using Homebrew):
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux** (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Local Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql prompt, create database:
CREATE DATABASE skill_barter_db;
\q
```

### 3. Set Up Python Environment

```bash
# Clone or navigate to your project
cd student_skill_barter

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies using python -m pip
python -m pip install -r requirements.txt
```

### 4. Configure `.env` for Local Development

Create a `.env` file in your project root:

```env
SECRET_KEY=your-local-secret-key-here

# Local PostgreSQL connection
DATABASE_URL=postgresql://postgres:your_postgres_password@localhost:5432/skill_barter_db

# Flask environment
FLASK_ENV=development
```

Replace `your_postgres_password` with the password you set during PostgreSQL installation.

### 5. Run Local App

```bash
# Make sure venv is activated
python app.py
```

Visit: **http://localhost:5000**

---

## Render Deployment Setup

### 1. Create PostgreSQL Database on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Configure:
   - **Name**: `skill-barter-db`
   - **Database**: `skill_barter_db`
   - **User**: `postgres`
   - **Region**: Choose your closest region
   - **Plan**: Free (for testing)
4. Click **Create Database**
5. **COPY the DATABASE_URL** from the dashboard

### 2. Deploy Web Service to Render

1. Push your code to GitHub first:
   ```bash
   git push origin main
   ```

2. In Render Dashboard, click **New +** → **Web Service**

3. Connect your GitHub repository

4. Configure:
   - **Name**: `student-skill-barter`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free or Starter

5. Click **Create Web Service**

### 3. Set Environment Variables on Render

1. In your web service dashboard, go to **Environment**

2. Add these variables:

   ```
   SECRET_KEY=<generate-a-secure-random-string>
   DATABASE_URL=<paste-the-URL-from-step-1>
   FLASK_ENV=production
   ```

3. Click **Save**

### 4. Verify Deployment

- Render will automatically deploy your app
- Check **Logs** tab for any errors
- Once deployed, your app will be at: `https://student-skill-barter.onrender.com`

---

## Environment Variables Reference

### Local Development (`.env`)

```env
# Application security
SECRET_KEY=your-local-secret-key

# Database connection (PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/skill_barter_db

# Flask mode
FLASK_ENV=development

# Optional: Debug mode (not recommended for production)
FLASK_DEBUG=True
```

### Render Deployment (Dashboard)

Set these in Render's Environment Variables section:

```
SECRET_KEY=<secure-random-key>
DATABASE_URL=<from-render-postgres>
FLASK_ENV=production
```

---

## Testing Database Connection

### Verify Local Connection

```bash
# Activate venv first
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run this Python script to test connection
python -c "
from app import create_app
app = create_app()
with app.app_context():
    from database.db import db
    print('✓ Database connection successful!')
"
```

### Verify Render Connection

- Check Render dashboard **Logs** tab for connection errors
- Look for messages like:
  - `✓ Database tables created`
  - Connection errors will show `OperationalError` details

---

## Troubleshooting

### PostgreSQL not running locally

**Windows**: 
- Start from Services (services.msc) → PostgreSQL

**macOS**:
```bash
brew services start postgresql@15
```

**Linux**:
```bash
sudo systemctl start postgresql
```

### "role postgres does not exist" error

PostgreSQL user might not exist. Create it:

```bash
psql -U postgres -c "CREATE ROLE postgres WITH LOGIN PASSWORD 'password';"
```

### Wrong DATABASE_URL format

**Incorrect**:
```
DATABASE_URL=postgresql://user:pass@host/db  # Missing port
DATABASE_URL=postgres://user:pass@host:5432/db  # Old format
```

**Correct**:
```
DATABASE_URL=postgresql://user:password@localhost:5432/skill_barter_db
```

### Permission denied errors

**macOS/Linux**: PostgreSQL might need permissions:

```bash
# Fix PostgreSQL ownership
sudo chown -R $(whoami) /usr/local/var/postgres

# Or reinstall cleanly with Homebrew
brew uninstall postgresql
brew install postgresql@15
```

### Render deployment fails

Check these in order:
1. **Logs tab** - Look for error messages
2. **DATABASE_URL** - Make sure it's set and correct
3. **requirements.txt** - Ensure all packages are listed
4. **Python version** - Render defaults to Python 3, should be fine

---

## Security Notes

### For Local Development
- Store `.env` in `.gitignore` (don't commit to GitHub)
- It's OK to use simple passwords locally

### For Production (Render)
- Use **strong, random SECRET_KEY**: 
  ```python
  import secrets
  secrets.token_hex(32)
  ```
- Use **strong password** for PostgreSQL (Render generates one)
- DATABASE_URL should be auto-generated by Render
- Never commit `.env` to GitHub
- Use HTTPS only (Render enforces this)

---

## Development Tips

### Running migrations

```bash
# SQLAlchemy creates tables automatically
# If you need to reset:
python -c "
from app import create_app
from database.db import db

app = create_app()
with app.app_context():
    db.drop_all()  # WARNING: Deletes all tables
    db.create_all()  # Recreates tables
    print('Database reset!')
"
```

### Debugging database issues

```bash
# Connect to PostgreSQL directly
psql -U postgres -d skill_barter_db

# List tables
\dt

# Quit
\q
```

### Testing API endpoints

```bash
# Using curl (or Postman)
curl -X POST http://localhost:5000/register \
  -d "full_name=Test&username=testuser&password=pass123&confirm_password=pass123"
```

---

## File Location Reference

```
student_skill_barter/
├── .env                    ← Your local settings (don't commit!)
├── .env.example            ← Template for .env
├── requirements.txt        ← Python packages
├── app.py                  ← Flask app entry point
├── config.py               ← Configuration
├── database/
│   └── db.py              ← SQLAlchemy setup
├── models/                 ← Database models
├── routes/                 ← Flask blueprints
└── templates/              ← HTML templates
```

---

## Next Steps

1. ✅ Set up PostgreSQL locally
2. ✅ Create `.env` with DATABASE_URL
3. ✅ Install dependencies: `python -m pip install -r requirements.txt`
4. ✅ Run app: `python app.py`
5. ✅ Test locally at `http://localhost:5000`
6. ✅ Deploy to Render following RENDER_DEPLOYMENT.md
