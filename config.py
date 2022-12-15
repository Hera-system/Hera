import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    default_secret_url = 'https://raw.githubusercontent.com/Hera-system/HTTPSecret/main/HTTPSecret'
    WTF_CSRF_ENABLED = True
    DEBUG = os.getenv("DEBUG")
    ALERTA_URL = os.getenv("ALERTA_URL")
    SU_USER = os.getenv("ADMIN_USERNAME")
    SU_PASS = os.getenv("ADMIN_PASSWORD")
    SECRET_URL = os.environ.get('SECRET_URL') or default_secret_url
    SECRET_TOKEN = os.environ.get('SECRET_TOKEN') or 'VeryStrongString'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_MIGRATE_REPO = "db"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    if (SQLALCHEMY_DATABASE_URI is None) or (SQLALCHEMY_DATABASE_URI == "sqlite"):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 20,
            'pool_reset_on_return': 'commit',
            'pool_timeout': 5
        }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_ADD_STATUS = False
    WEBHOOK = {
        "AutoUpdate": False
    }
