from distutils.cmd import Command

from app import db, login
from flask_login import UserMixin
from datetime import datetime
from pydantic import BaseModel


class CommandExecution(db.Model):
    RowID = db.Column(db.Integer, primary_key=True)
    TemplateID = db.Column(db.Integer)
    CmdID = db.Column(db.String, unique=True)
    Error = db.Column(db.Boolean)
    Stdout = db.Column(db.String)
    Stderr = db.Column(db.String)
    Message = db.Column(db.String)
    WebhookURL = db.Column(db.String)
    WebhookName = db.Column(db.String)
    TimeExecute = db.Column(db.Integer)
    FromUser = db.Column(db.String)
    TimeCrt = db.Column(db.DateTime(), default=datetime.now(), index=True)
    TimeUpd = db.Column(db.DateTime())

    def __repr__(self):
        return f'<id - {self.RowID}.'


class WebhookConnect(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String)
    username = db.Column(db.String)
    version = db.Column(db.String)
    uniq_name = db.Column(db.String)
    url = db.Column(db.String)
    os_type = db.Column(db.String)
    os_arch = db.Column(db.String)
    cpu_core = db.Column(db.Integer)
    time_connect = db.Column(db.DateTime(), default=datetime.now(), index=True)
    active = db.Column(db.Boolean, default=True)


class Templates(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Command = db.Column(db.String())
    Interpreter = db.Column(db.String())
    Trusted = db.Column(db.Boolean(), default=False, index=True)
    UserCrt = db.Column(db.String())
    DataCrt = db.Column(db.DateTime(), default=datetime.now(), index=True)
    TimeExec = db.Column(db.Integer)
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


class InfoReturnApi(BaseModel):
    error: bool
    message: str


class InfoWebhook(BaseModel):
    Token: str
    hostname: str
    username: str
    webhook_vers: str
    webhook_url: str
    webhook_uniq_name: str
    os_type: str
    os_arch: str
    cpu_core: int


class GettingResult(BaseModel):
    Error: str
    Stdout: str
    Stderr: str
    ID: str
    Message: str


class ExecutionCommand(BaseModel):
    ExecCommand: str
    Interpreter: str
    Token: str
    TimeExec: int
    ID: str
    HTTPSecret: str


class AlertaAuth(BaseModel):
    password: str
    username: str


class ResultWebhook(BaseModel):
    Error: bool
    Stdout: str
    Stderr: str
    ID: str
    Message: str

class ArgsCommandExecution(BaseModel):
    TemplateID: int
    WebhookURL: str
    WebhookName: str
    FromUser: str
    CmdID: str
    ExecCommand: str
    TimeExec: int
    Interpreter: str
