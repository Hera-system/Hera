from app import db


class CommandExecution(db.Model):
    RowID = db.Column(db.Integer, primary_key=True)
    TemplateID = db.Column(db.Integer)
    CmdID = db.Column(db.String, unique=True)
    Error = db.Column(db.Boolean)
    Stdout = db.Column(db.String)
    Stderr = db.Column(db.String)
    Message = db.Column(db.String)
    WebhookURL = db.Column(db.String)
    TimeExecute = db.Column(db.String)
    Shebang = db.Column(db.String)
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
    DataCrt = db.Column(db.String(), default="0", index=True)
    DataTrusted = db.Column(db.String(), default="0", index=True)

    def __repr__(self):
        return f'<id - {self.ID}.'
