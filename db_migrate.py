#!flask/bin/python
from app import db, create_app
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)
