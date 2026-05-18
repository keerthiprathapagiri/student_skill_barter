# Gunicorn Startup Debugging Guide

This guide helps debug startup issues when deploying to Render.

---

## Local Testing Before Render Deployment

### 1. Test Basic Flask App

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Test if Flask starts
python app.py
```

Expected output:
```
  ⚡ Student Skill Barter → http://localhost:5000
```

If this fails, check:
- ✅ Python 3.10+
- ✅ Virtual environment activated
- ✅ All dependencies installed: `python -m pip install -r requirements.txt`
- ✅ PostgreSQL running locally
- ✅ `.env` file exists with DATABASE_URL

### 2. Test Gunicorn Locally

```bash
# Install Gunicorn (if not in requirements.txt)
python -m pip install gunicorn

# Test Gunicorn with eventlet worker
gunicorn --worker-class eventlet -w 1 -b 0.0.0.0:5000 app:app
```

Expected output:
```
[YYYY-MM-DD HH:MM:SS +0000] [PID] [INFO] Starting gunicorn ...
[YYYY-MM-DD HH:MM:SS +0000] [PID] [INFO] Listening at: http://0.0.0.0:5000 ...
```

If this fails, check error messages for:
- `ModuleNotFoundError` - Missing package
- `OperationalError` - Database connection issue
- `SyntaxError` - Code syntax error
- `ImportError` - Import path issue

### 3. Test Database Connection

```bash
# Test if app can connect to database
python -c "
from app import app
from database.db import db

try:
    with app.app_context():
        db.create_all()
    print('✓ Database connection successful!')
except Exception as e:
    print(f'✗ Database error: {e}')
"
```

If this fails:
- Check DATABASE_URL format
- Ensure PostgreSQL is running
- Verify database credentials
- Check firewall/network settings

---

## Common Render Deployment Errors

### Error: "Exited with status 1"

This generic error means the app crashed during startup. Check Render logs:

1. Go to Render dashboard
2. Select your web service
3. Click **Logs** tab
4. Look for actual error message

Common causes:

#### `ModuleNotFoundError: No module named 'xxx'`
- Solution: Add missing package to requirements.txt
- Re-deploy after updating requirements.txt

#### `OperationalError: connection to server failed`
- Solution: DATABASE_URL not set or invalid
- Check Render dashboard → Environment Variables
- Ensure PostgreSQL database is running on Render
- Wait for database to finish provisioning (can take 5+ minutes)

#### `ImportError: cannot import name 'xxx'`
- Solution: Circular import or missing model
- Test locally with `python app.py`
- Check all model definitions

#### `AttributeError: 'Config' object has no attribute 'SQLALCHEMY_DATABASE_URI'`
- Solution: Configuration error in config.py
- Verify ActiveConfig is properly set
- Check DATABASE_URL environment variable

### Error: "Address already in use"
- Local issue only, port 5000 already running
- Kill existing process or use different port

---

## Render Environment Variables

Verify these are set in Render dashboard:

```
SECRET_KEY=<secure-random-key>
DATABASE_URL=<from-postgres-database>
FLASK_ENV=production
```

### Getting DATABASE_URL

1. In Render dashboard, go to PostgreSQL database
2. Copy the **Connection String** (starts with `postgres://` or `postgresql://`)
3. Paste into web service **Environment Variables** as `DATABASE_URL`

**Note**: App automatically converts `postgres://` to `postgresql://`

---

## Procfile Configuration

File: `Procfile`

Content:
```
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
```

This tells Render to:
- Use `gunicorn` as web server
- Use `eventlet` for async worker (needed for Socket.IO)
- Start 1 worker
- Bind to Render's PORT environment variable
- Load `app:app` (Flask app from app.py)

---

## Step-by-Step Debugging

### Step 1: Test Locally
```bash
python app.py
```
Visit: http://localhost:5000

### Step 2: Test with Gunicorn Locally
```bash
gunicorn --worker-class eventlet -w 1 app:app
```
Visit: http://localhost:8000

### Step 3: Check Render Logs
- Go to web service
- Click **Logs** tab
- Look for error messages

### Step 4: Fix Issues
- Update code locally
- Commit to GitHub
- Render auto-deploys on push

### Step 5: Verify Deployment
- Check web service status
- Visit provided URL
- Test all features

---

## Deployment Checklist

Before pushing to GitHub:

- [ ] `python app.py` runs without errors locally
- [ ] `gunicorn --worker-class eventlet -w 1 app:app` runs locally
- [ ] All imports resolve correctly
- [ ] `.env` is added to `.gitignore`
- [ ] `requirements.txt` has all packages
- [ ] `Procfile` exists in project root
- [ ] `config.py` handles DATABASE_URL correctly
- [ ] No MySQL references in code
- [ ] All models inherit from `db.Model`

---

## Quick Fixes

### "Module not found" error
```bash
# Update requirements.txt
python -m pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
# Render auto-redeploys
```

### Database connection error
```bash
# Check Render PostgreSQL database
# 1. Go to database in Render
# 2. Verify it's "Available"
# 3. Copy fresh CONNECTION_STRING
# 4. Update DATABASE_URL in web service Environment Variables
# 5. Manually trigger deployment
```

### App still crashes
```bash
# Test app.py locally first
python app.py

# If it works locally, try Gunicorn
gunicorn --worker-class eventlet -w 1 app:app

# If both work, check Render logs for different error
```

---

## Contact Support

If you still have issues:

1. **Check Render Logs** - Most detailed error info
2. **Test Locally First** - Isolate the issue
3. **Verify Environment Variables** - SECRET_KEY and DATABASE_URL
4. **Check requirements.txt** - All packages listed
5. **Review Error Messages** - Look for patterns

---

## Success Indicators

✅ Deployment successful when:
- No errors in Render logs
- Web service shows "Live"
- App accessible at Render URL
- All features work (register, login, chat, skills, etc.)
- Database tables created automatically

---

Last Updated: May 18, 2026
