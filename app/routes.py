import json
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app.models import *
from app import app, db, api
from app.forms import *
from flask_json import as_json
from flask_restful import Resource, Api

api_v = "v1"


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/addedTemplate', methods=['GET', 'POST'])
def AddedTemplate():
    form = TemplateAdded()
    if form.validate_on_submit():
        form = Templates(Command=form.Command.data, Shebang=form.Shebang.data, Interpreter=form.Interpreter.data, DataCrt=datetime.now().timestamp())
        db.session.add(form)
        db.session.commit()
        form = TemplateAdded()
        flash('Template added!')
    return render_template('addedTemplate.html', form=form)


@app.route('/execCommand', methods=['GET', 'POST'])
def execCommand():
    form = CommandClass()
    if form.validate():
        cmd = CommandExecution(TemplateID=form.TemplateID.data, WebhookURL=form.WebhookURL.data, TimeExecute=form.TimeExecute.data,  UnixTimeCrt=datetime.now().timestamp(), CmdID="qwe")
        db.session.add(cmd)
        db.session.commit()
        return "OK"
    return render_template("execcommad.html", form=form)

        # class CommandExecution(db.Model):
        #     RowID = db.Column(db.Integer, primary_key=True)
        #     CmdID = db.Column(db.String)
        #     Error = db.Column(db.Boolean)
        #     Stdout = db.Column(db.String)
        #     Stderr = db.Column(db.String)
        #     Token = db.Column(db.String)
        #     Message = db.Column(db.String)
        #     WebhookURL = db.Column(db.String)
        #     ServerName = db.Column(db.String)
        #     CmdFrom = db.Column(db.String)
        #     UnixTime = db.Column(db.String(), default="0", index=True)
        # user = Users(username=form.username.data, email=form.email.data)
        # user.set_password(form.password.data)
        # db.session.add(user)
        # db.session.commit()
    return False
        # Форму CommandClass распарсить на страницу и далее с ней работаь



class ResultApi(Resource):
    def post(self):
        ResponseData = json.loads(request.data.decode("utf-8"))
        RespData = CommandExecution.query.filter_by(CmdID=ResponseData["ID"]).first()
        RespData(Error=ResponseData["Error"], Stdout=ResponseData["Stdout"], Stderr=ResponseData["Stderr"], CmdID=ResponseData["ID"], Token=ResponseData["Token"], Message=ResponseData["Message"])
        db.session.commit()  # https://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
        return {'message': 'OK'}

class InfoApi(Resource):
    def get(self):
        pass # Вероято тут будет некая хрень для алерты.
             # ?instance=test&source=ewq - Нужно работать с этим как то


api.add_resource(ResultApi, f'/api/{api_v}/result')
api.add_resource(InfoApi, f'/api/{api_v}/info')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
