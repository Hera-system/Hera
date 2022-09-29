import json
import random
import string
import requests
from datetime import datetime

from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app.models import *
from app import app, db, api
from app.forms import *
from flask_json import as_json
from flask_restful import Resource, Api

api_v = "v1"


def SendExecuteCommand(command):
    Token = "VeryStrongString"  # Потом надо спрятать
    URLSecret = "https://raw.githubusercontent.com/Hera-system/TOTP/main/TOTP" # Аналогично, так же придется спрятать переменную и ее значение, верояно в переменные окружения.
    requestSecret = requests.get(URLSecret)
    if requestSecret.status_code == 200:
        Template = Templates.query.filter_by(ID=command.TemplateID).first()
        cmd = {"ExecCommand": Template.Command, "Shebang": Template.Shebang, "Interpreter": Template.Interpreter, "Token": Token, "TimeExec": command.TimeExecute, "ID": command.CmdID, "HTTPSecret": requestSecret.text}
        HeaderWebhook = {'Content-type': 'text/plain'}
        requestWebhook = requests.post(command.WebhookURL, json=cmd, headers=HeaderWebhook)
        if requestWebhook.status_code == 200:
            return True
    return False


def GenerateUniqID(Lenght: int) -> str:
    RndString = ""
    RndList = ['ascii_lowercase', 'ascii_uppercase', 'digits']
    ascii_lowercase = list(string.ascii_lowercase)
    ascii_uppercase = list(string.ascii_uppercase)
    digits = list(string.digits)
    for i in range(Lenght):
        RndChoice = random.choices(RndList, k=1)[0]
        if RndChoice == "ascii_lowercase":
            RndString = RndString + random.choices(ascii_lowercase, k=1)[0]
        if RndChoice == "ascii_uppercase":
            RndString = RndString + random.choices(ascii_uppercase, k=1)[0]
        if RndChoice == "digits":
            RndString = RndString + random.choices(digits, k=1)[0]
    CheckQuery = CommandExecution.query.filter_by(CmdID=RndString).first()
    if CheckQuery is None:
        return RndString
    return GenerateUniqID(Lenght)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/trustedTemplate', methods=['GET', 'POST'])
def TrustedTemplate():
    form = TemplateTrusted()
    if form.validate():
        Template = Templates.query.filter_by(ID=form.TemplateID.data).first()
        if Template is None:
            return "Template not found", 404
        if Template.UserCrt == form.UserTrust.data:
            return "User created template not permission to trusted this template", 401
        if Template.Trusted:
            return f"Template - ID {Template.ID} is trusted."
        Template.Trusted = True
        Template.ID = form.TemplateID.data
        Template.UserTrusted = form.UserTrust.data
        Template.DataTrusted = datetime.now().timestamp()
        db.session.commit()
        form = TemplateTrusted()
        flash("Template trusted")
    return render_template('trustedTemplate.html', form=form)


@app.route('/addedTemplate', methods=['GET', 'POST'])
def AddedTemplate():
    form = TemplateAdded()
    if form.validate_on_submit():
        # dataCrt = datetime.now().timestamp()
        form = Templates(Command=form.Command.data, Shebang=form.Shebang.data, Interpreter=form.Interpreter.data, UserCrt=form.UserCrt.data, DataCrt=datetime.now().timestamp())  # Вероятно дату надо будет перенести в дефолт в модели
        db.session.add(form)
        db.session.commit()
        flash(f'Template added! ID - {form.ID}')
        form = TemplateAdded()
    return render_template('addedTemplate.html', form=form)


@app.route('/execCommand', methods=['GET', 'POST'])
def execCommand():
    form = CommandClass()
    if form.validate():
        Template = Templates.query.filter_by(ID=form.TemplateID.data).first()
        if Template.Trusted:
            cmd = CommandExecution(TemplateID=form.TemplateID.data, WebhookURL=form.WebhookURL.data, TimeExecute=form.TimeExecute.data,  FromUser=form.FromUser.data, UnixTimeCrt=datetime.now().timestamp(), CmdID=GenerateUniqID(10))
            db.session.add(cmd)
            db.session.commit()
            SendExecuteCommand(cmd)
            return "OK"
        return "Template not trusted"
    return render_template("execcommad.html", form=form)


class ResultApi(Resource):
    def post(self):
        ResponseData = json.loads(request.data.decode("utf-8"))
        RespData = CommandExecution.query.filter_by(CmdID=ResponseData["ID"]).first()
        RespData.Error = ResponseData["Error"]
        RespData.Stdout = ResponseData["Stdout"]
        RespData.Stderr = ResponseData["Stderr"]
        RespData.CmdID = ResponseData["ID"]
        RespData.Message = ResponseData["Message"]
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
