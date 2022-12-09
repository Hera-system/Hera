from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_login import LoginManager
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(db)
login = LoginManager(app)
login.login_message = "Please logging to view this page."
login.login_view = 'login'
bootstrap = Bootstrap5(app)
api = Api(app)
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
from app import routes, models  # noqa: F401,E402


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from app import routes, models  # noqa: F401,E402
    return app
