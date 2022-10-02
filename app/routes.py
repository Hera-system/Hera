import json
import os
import random
import string
import requests
from datetime import datetime
from datetime import timedelta

from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask import render_template, flash, redirect, url_for, request, send_from_directory
from app.models import *
from app import app, db, api
from app.forms import *
from flask_json import as_json
from flask_restful import Resource, Api

api_v = "v1"
AlertaURLAuth = os.getenv("ALERTA_URL")


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


def getUser(email):
    user = Users.query.filter_by(email=email).first()
    if user is None:
        user = Users(email=email)
        db.session.add(user)
        db.session.commit()
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AlertaLogin()
    if form.validate():
        cmd = {"password": form.Password.data, "username": form.Email.data}
        requestAuth = requests.post(AlertaURLAuth, json=cmd)
        if requestAuth.status_code == 200:
            login_user(getUser(form.Email.data), form.RememberMe.data, timedelta(days=7))
            flash("You are authorized in Hera system!")
    return render_template('login.html', form=form)


@login_required
@app.route('/trustedTemplate', methods=['GET', 'POST'])
def TrustedTemplate():
    if current_user.is_authenticated:
        form = TemplateTrusted()
        if form.validate():
            Template = Templates.query.filter_by(ID=form.TemplateID.data).first()
            if Template is None:
                flash("Template not found")
                return render_template('trustedTemplate.html', form=form), 404
            if Template.UserCrt == current_user.email:
                flash("User created template not permission to trusted this template")
                return render_template('trustedTemplate.html', form=form), 401
            if Template.Trusted:
                flash(f"Template - ID {Template.ID} is trusted.")
                return render_template('trustedTemplate.html', form=form), 401
            Template.Trusted = True
            Template.ID = form.TemplateID.data
            Template.UserTrusted = current_user.email
            Template.DataTrusted = datetime.now().timestamp()
            db.session.commit()
            form = TemplateTrusted()
            flash("Template trusted")
        return render_template('trustedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@login_required
@app.route('/addedTemplate', methods=['GET', 'POST'])
def AddedTemplate():
    if current_user.is_authenticated:
        form = TemplateAdded()
        if form.validate_on_submit():
            form = Templates(Command=form.Command.data, Shebang=form.Shebang.data, Interpreter=form.Interpreter.data, UserCrt=current_user.email, DataCrt=datetime.now().timestamp())  # Вероятно дату надо будет перенести в дефолт в модели
            db.session.add(form)
            db.session.commit()
            flash(f'Template added! ID - {form.ID}')
            form = TemplateAdded()
        return render_template('addedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@login_required
@app.route('/execCommand', methods=['GET', 'POST'])
def execCommand():
    if current_user.is_authenticated:
        form = ExecuteCommand()
        if form.validate():
            Template = Templates.query.filter_by(ID=form.TemplateID.data).first()
            if Template.Trusted:
                cmd = CommandExecution(TemplateID=form.TemplateID.data, WebhookURL=form.WebhookURL.data, TimeExecute=form.TimeExecute.data,  FromUser=current_user.email, UnixTimeCrt=datetime.now().timestamp(), CmdID=GenerateUniqID(10))
                db.session.add(cmd)
                db.session.commit()
                SendExecuteCommand(cmd)
                flash("Success")
                return
            flash("Template not trusted")
        return render_template("execcommad.html", form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


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
