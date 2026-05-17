# config.py
# Centralised Flask configuration
# Values are read from environment variables (set in .env)

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared by all environments."""

    # ── Security ──────────────────────────────────────────────────
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-CHANGE-ME-in-production')

    # ── MySQL ─────────────────────────────────────────────────────
    MYSQL_HOST     = os.getenv('MYSQL_HOST',     'localhost')
    MYSQL_USER     = os.getenv('MYSQL_USER',     'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB       = os.getenv('MYSQL_DB',       'skill_barter_db')
    MYSQL_CURSORCLASS = 'DictCursor'   # rows come back as plain dicts

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
