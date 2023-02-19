from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please logging to view this page.'
bootstrap = Bootstrap5()
api = Api()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    bootstrap.init_app(app)
    login.init_app(app)
    login.login_message = "Please logging to view this page."
    api.init_app(app)
    app.config.from_object(Config)
    from app import models  # noqa: F401,E402
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    db.init_app(app)
    migrate.init_app(app, db)
    login.login_view = 'login'
    return app
