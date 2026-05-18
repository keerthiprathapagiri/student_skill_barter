# config.py

import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.environ.get("DATABASE_URL")

# Fix old postgres:// format
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace(
    "postgres://",
    "postgresql+psycopg://",
    1
)

if database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

# Add SSL mode for Render PostgreSQL
if database_url and "sslmode" not in database_url:
    if "?" in database_url:
        database_url += "&sslmode=require"
    else:
        database_url += "?sslmode=require"


class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "Studentskillbarter"
    )

    SQLALCHEMY_DATABASE_URI = database_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Prevent stale PostgreSQL connections
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    SOCKETIO_ASYNC_MODE = "threading"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

ActiveConfig = config_map.get(
    os.getenv("FLASK_ENV", "production"),
    ProductionConfig
)