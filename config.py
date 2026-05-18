# config.py
# Centralised Flask configuration
# Values are read from environment variables (set in .env)

import os
from dotenv import load_dotenv

load_dotenv()

# Fix DATABASE_URL for Render (postgres:// → postgresql://)
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)


class Config:
    """Base configuration shared by all environments."""

    # ── Security ──────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-CHANGE-ME-in-production')

    # ── PostgreSQL ────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = database_url or 'postgresql://postgres@localhost/skill_barter_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session ───────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── SocketIO ──────────────────────────────────────────────────
    SOCKETIO_ASYNC_MODE = 'eventlet'


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True   # only send cookie over HTTPS


# Active config selected by FLASK_ENV env var
config_map = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
}

ActiveConfig = config_map.get(os.getenv('FLASK_ENV', 'development'), DevelopmentConfig)

