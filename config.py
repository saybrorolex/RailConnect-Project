import os

class Config:
    # ── Security ───────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

    # ── Database ───────────────────────────────────────────────────────────
    DATABASE_URL = os.environ.get('DATABASE_URL')

    if DATABASE_URL:
        if DATABASE_URL.startswith('mysql://'):
            DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        MYSQL_HOST     = os.environ.get('MYSQL_HOST', 'localhost')
        MYSQL_USER     = os.environ.get('MYSQL_USER', 'root')
        MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'your_password')
        MYSQL_DB       = os.environ.get('MYSQL_DB', 'railconnect')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{MYSQL_HOST}/{MYSQL_DB}"
            if not MYSQL_USER
            else f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
