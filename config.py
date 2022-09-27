import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_MIGRATE_REPO = "db"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    #if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
    #    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_ADD_STATUS = False
    #STATIC_FOLDER = '/app/static'
