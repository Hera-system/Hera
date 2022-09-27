from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
from app import routes, models
migrate = Migrate(app, db)
