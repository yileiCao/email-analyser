from datetime import timedelta
import os


class Config(object):
    DEBUG = True
    DEVELOPMENT = True
    SECRET_KEY = os.urandom(12).hex()
    SESSION_PERMANENT = True
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=5)
    SESSION_FILE_THRESHOLD = 100
    PROPAGATE_EXCEPTIONS = True


class DbConfig(object):
    url = "sqlite:///email.db"
    echo = False


class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
