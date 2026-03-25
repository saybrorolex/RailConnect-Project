import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL or 'sqlite:///railconnect.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
