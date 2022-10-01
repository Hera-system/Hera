from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api
from flask_login import LoginManager
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_message = "Please logging to view this page."
api = Api(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
from app import routes, models
migrate = Migrate(app, db)
login.login_view = 'login'

