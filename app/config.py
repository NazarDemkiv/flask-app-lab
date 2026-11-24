import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///data.sqlite")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    SERVER_SIDE_SESSIONS = True

    MAX_CONTENT_LENGTH = 6 * 1024 * 1024


class DevelopmentConfig(Config):
    DEBUG = True
    # Show SQL statements in the console for laboratory work 8.
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SERVER_SIDE_SESSIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
