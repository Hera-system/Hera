from app import db, login
from flask_login import UserMixin


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
    UnixTimeCrt = db.Column(db.String(), default="0", index=True)
    UnixTimeUpd = db.Column(db.String(), default="0", index=True)

    def __repr__(self):
        return f'<id - {self.ID}.'


class Templates(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Command = db.Column(db.String())
    Shebang = db.Column(db.String())
    Interpreter = db.Column(db.String())
    Trusted = db.Column(db.Boolean(), default=False, index=True)
    StrID = db.Column(db.String(), unique=True)
    UserCrt = db.Column(db.String())
    DataCrt = db.Column(db.String(), default="0", index=True)
    UserTrusted = db.Column(db.String())
    DataTrusted = db.Column(db.String(), default="0", index=True)

    def __repr__(self):
        return f'<id - {self.ID}.'


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __repr__(self):
        return '<Users {}>'.format(self.username)

    def repr(self):
        return ''.format(self.username)


@login.user_loader
def load_user(ID):
    return Users.query.get(int(ID))
