from app import db, login
from flask_login import UserMixin
from datetime import datetime


class CommandExecution(db.Model):
    RowID = db.Column(db.Integer, primary_key=True)
    TemplateID = db.Column(db.Integer)
    CmdID = db.Column(db.String, unique=True)
    Error = db.Column(db.Boolean)
    Stdout = db.Column(db.String)
    Stderr = db.Column(db.String)
    Message = db.Column(db.String)
    WebhookURL = db.Column(db.String)
    TimeExecute = db.Column(db.Integer)
    FromUser = db.Column(db.String)
    TimeCrt = db.Column(db.DateTime(), default=datetime.now(), index=True)
    TimeUpd = db.Column(db.DateTime())

    def __repr__(self):
        return f'<id - {self.ID}.'


class WebhookConnect(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    webhook_hostname = db.Column(db.String)
    webhook_username = db.Column(db.String)
    webhook_version = db.Column(db.String)
    webhook_uniq_name = db.Column(db.String)
    webhook_cmd_url = db.Column(db.String)
    time_connect = db.Column(db.DateTime(), default=datetime.now(), index=True)


class Templates(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Command = db.Column(db.String())
    Shebang = db.Column(db.String())
    Interpreter = db.Column(db.String())
    Trusted = db.Column(db.Boolean(), default=False, index=True)
    StrID = db.Column(db.String(), unique=True)
    UserCrt = db.Column(db.String())
    DataCrt = db.Column(db.DateTime(), default=datetime.now(), index=True)
    UserTrusted = db.Column(db.String())
    DataTrusted = db.Column(db.DateTime())

    def __repr__(self):
        return f'<id - {self.ID}.'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def repr(self):
        return self.username


@login.user_loader
def load_user(ID):
    return Users.query.get(int(ID))
