from app import db


class CommandExecution(db.Model):
    RowID = db.Column(db.Integer, primary_key=True)
    CmdID = db.Column(db.String)
    Error = db.Column(db.Boolean)
    Stdout = db.Column(db.String)
    Stderr = db.Column(db.String)
    Token = db.Column(db.String)
    Message = db.Column(db.String)
    ServerIP = db.Column(db.String)
    ServerName = db.Column(db.String)
    CmdFrom = db.Column(db.String)
    UnixTime = db.Column(db.String(), default="0", index=True)

    def __repr__(self):
        return f'<id - {self.ID}.'


class Templates(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    Data = db.Column(db.String())
    Trusted = db.Column(db.Boolean(), default=False, index=True)
    StrID = db.Column(db.String(), unique=True)
    DataCrt = db.Column(db.String(), default="0", index=True)

    def __repr__(self):
        return f'<id - {self.ID}.'
