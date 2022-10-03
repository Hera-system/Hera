import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    WTF_CSRF_ENABLED = True
    SECRET_URL = os.environ.get('SECRET_URL') or 'https://raw.githubusercontent.com/Hera-system/HTTPSecret/main/HTTPSecret'
    SECRET_TOKEN = os.environ.get('SECRET_TOKEN') or 'VeryStrongString'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_MIGRATE_REPO = "db"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    if (SQLALCHEMY_DATABASE_URI is None) or (SQLALCHEMY_DATABASE_URI == "sqlite"):
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_ADD_STATUS = False
    #STATIC_FOLDER = '/app/static'
