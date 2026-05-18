# Deploying Student Skill Barter to Render

This guide explains how to deploy your Student Skill Barter Flask app to **Render**, a modern cloud platform.

---

## Prerequisites

- A GitHub account (to host your code)
- A Render account (free tier available at [render.com](https://render.com))
- Your Flask app migrated to PostgreSQL (using Flask-SQLAlchemy)

---

## Step 1: Push Code to GitHub

If you haven't already, initialize a Git repository and push your code:

```bash
git init
git add .
git commit -m "Initial commit: Flask app with PostgreSQL"
git branch -M main
git remote add origin https://github.com/your-username/student-skill-barter.git
git push -u origin main
```

**Important**: Add a `.gitignore` to exclude sensitive files:

```gitignore
.env
*.pyc
__pycache__/
venv/
*.db
.DS_Store
```

---

## Step 2: Create a Render PostgreSQL Database

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **PostgreSQL**
3. Fill in:
   - **Name**: `skill-barter-db`
   - **Database**: `skill_barter_db`
   - **User**: `postgres`
   - **Region**: Choose your region
   - **Plan**: **Free** (for testing)
4. Click **Create Database**
5. **Copy the DATABASE_URL** (you'll need it in Step 4)

---

## Step 3: Create a Render Web Service

1. Click **New +** → **Web Service**
2. Connect your GitHub repository
3. Fill in the deployment settings:

   | Field | Value |
   |-------|-------|
   | **Name** | `student-skill-barter` |
   | **Environment** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app` |
   | **Plan** | **Free** (or paid for better performance) |

4. Click **Create Web Service**

---

## Step 4: Set Environment Variables

In the Render dashboard for your web service:

1. Go to **Environment** tab
2. Click **Add Environment Variable**
3. Add these variables:

   | Key | Value |
   |-----|-------|
   | `SECRET_KEY` | Generate a secure key (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`) |
   | `DATABASE_URL` | Paste the PostgreSQL URL from Step 2 |
   | `FLASK_ENV` | `production` |

4. Click **Save**

---

## Step 5: Configure Your Flask App for Production

Ensure your `config.py` has:

```python
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URI = database_url
```

This automatically handles Render's `postgres://` → `postgresql://` conversion.

---

## Step 6: Create a `Procfile` (Optional but Recommended)

Create a file named `Procfile` in your project root:

```
web: gunicorn app:app
```

This tells Render exactly how to run your app.

---

## Step 7: Update `requirements.txt`

Make sure you have:

```txt
Flask==3.0.0
Flask-SocketIO==5.3.6
Flask-SQLAlchemy==3.1.1
Flask-Session==0.5.0
Werkzeug==3.0.1
python-dotenv==1.0.0
eventlet==0.35.1
psycopg2-binary==2.9.9
gunicorn
```

---

## Step 8: Deploy

1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Add Render deployment config"
   git push origin main
   ```

2. Render automatically detects the push and starts deployment
3. Monitor the build in the **Logs** tab
4. Once deployed, your app will be live at: `https://student-skill-barter.onrender.com`

---

## Troubleshooting

### Database connection fails
- Verify `DATABASE_URL` is correct in Environment Variables
- Check PostgreSQL database is running in Render
- Look at app logs: **Logs** tab in Render dashboard

### Import errors after deployment
- Rebuild: Click **Manual Deploy** → **Deploy latest commit**
- Check `requirements.txt` has all packages

### Socket.IO not working
- Ensure `eventlet` is in `requirements.txt`
- Check your frontend JavaScript is connecting to correct URL (should use relative paths)

### App crashes on startup
- Check logs in Render dashboard for errors
- Verify `db.create_all()` in `app.py` is called with `app.app_context()`
- Test locally first: `python app.py`

---

## Monitoring & Logs

- **View Logs**: Go to your service → **Logs** tab
- **Health Status**: Check the service page for current status
- **Metrics**: Render provides basic metrics on the dashboard

---

## Scaling

For production use:
- Upgrade from **Free** to **Standard** plan for better uptime
- Add environment variables for any sensitive data
- Consider using Redis for session management
- Set up automated backups for PostgreSQL

---

## Next Steps

1. Test your app at the Render URL
2. Create sample users and test skill matching
3. Test real-time chat with Socket.IO
4. Monitor logs for any errors
5. Set up a custom domain (optional)

---

## Support

- **Render Docs**: https://render.com/docs
- **Flask Deployment**: https://flask.palletsprojects.com/en/latest/deploying/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
