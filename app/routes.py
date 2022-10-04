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


def AproofTemplate(id):
    redirect_to = "template"
    Template = Templates.query.filter_by(ID=id).first()
    if Template is None:
        flash("Template not found")
        return redirect(url_for(redirect_to, id=id))
    if Template.UserCrt == current_user.email:
        flash("User created template not permission to trusted this template")
        return redirect(url_for(redirect_to, id=id))
    if Template.Trusted:
        flash(f"Template - ID {Template.ID} is trusted.")
        return redirect(url_for(redirect_to, id=id))
    Template.Trusted = True
    Template.ID = id
    Template.UserTrusted = current_user.email
    Template.DataTrusted = datetime.now()
    db.session.commit()
    flash("Template trusted")


def SendExecuteCommand(command):
    Token = app.config["SECRET_TOKEN"]
    URLSecret = app.config["SECRET_URL"]
    requestSecret = requests.get(URLSecret)
    if requestSecret.status_code == 200:
        Template = Templates.query.filter_by(ID=command.TemplateID).first()
        cmd = {"ExecCommand": Template.Command, "Shebang": Template.Shebang, "Interpreter": Template.Interpreter, "Token": Token, "TimeExec": command.TimeExecute, "ID": command.CmdID, "HTTPSecret": requestSecret.text}
        HeaderWebhook = {'Content-type': 'text/plain'}
        requestWebhook = requests.post(command.WebhookURL, json=cmd, headers=HeaderWebhook)
        if requestWebhook.status_code == 200:
            return flash("Successful send execute command.")
    return flash("Error send execute command. Pls check URL")


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


@app.route('/templates')
@login_required
def templates():
    if current_user.is_authenticated:
        templates = Templates.query.all()
        return render_template("templates.html", templates=templates, lenght=15)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/commands')
@login_required
def commands():
    if current_user.is_authenticated:
        commands = CommandExecution.query.all()
        return render_template("commands.html", commands=commands)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/command/<id>')
@login_required
def command(id):
    if current_user.is_authenticated:
        if id.isdigit():
            command = CommandExecution.query.filter_by(RowID=int(id)).first()
            return render_template("command.html", command=command)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/template/<id>', methods=['GET', 'POST'])
@login_required
def template(id):
    if current_user.is_authenticated:
        if id.isdigit():
            template = Templates.query.filter_by(ID=int(id)).first()
            form = TrustTemplate()
            if form.validate():
                AproofTemplate(id)
            return render_template("template.html", template=template, form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AlertaLogin()
    if form.validate():
        cmd = {"password": form.Password.data, "username": form.Email.data}
        requestAuth = requests.post(app.config["ALERTA_URL"], json=cmd)
        if requestAuth.status_code == 200:
            login_user(getUser(form.Email.data), form.RememberMe.data, timedelta(days=7))
            flash("You are authorized in Hera system!")
            return redirect(url_for('templates'))
    return render_template('login.html', form=form)


@app.route('/trustedTemplate', methods=['GET', 'POST'])
@login_required
def TrustedTemplate():
    if current_user.is_authenticated:
        form = TemplateTrusted()
        if form.validate():
            AproofTemplate(form.TemplateID.data)
        return render_template('trustedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/addedTemplate', methods=['GET', 'POST'])
@login_required
def AddedTemplate():
    if current_user.is_authenticated:
        form = TemplateAdded()
        if form.validate_on_submit():
            form = Templates(Command=form.Command.data, Shebang=form.Shebang.data, Interpreter=form.Interpreter.data, UserCrt=current_user.email)
            db.session.add(form)
            db.session.commit()
            flash(f'Template added! ID - {form.ID}')
            form = TemplateAdded()
        return render_template('addedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/execCommand', methods=['GET', 'POST'])
@login_required
def execCommand():
    if current_user.is_authenticated:
        form = ExecuteCommand()
        if form.validate():
            Template = Templates.query.filter_by(ID=form.TemplateID.data).first()
            if not (Template is None):
                if Template.Trusted:
                    cmd = CommandExecution(TemplateID=form.TemplateID.data, WebhookURL=form.WebhookURL.data, TimeExecute=form.TimeExecute.data,  FromUser=current_user.email, CmdID=GenerateUniqID(10))
                    db.session.add(cmd)
                    db.session.commit()
                    SendExecuteCommand(cmd)
                    return render_template("execcommad.html", form=form)
                flash("Template not trusted")
            else:
                flash("Template not found")
        return render_template("execcommad.html", form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def faviconico():
    return send_from_directory('static/', 'image/favicons/favicon.ico')


class ResultApi(Resource):
    def post(self):
        ResponseData = json.loads(request.data.decode("utf-8"))
        RespData = CommandExecution.query.filter_by(CmdID=ResponseData["ID"]).first()
        RespData.Error = ResponseData["Error"]
        RespData.Stdout = ResponseData["Stdout"]
        RespData.Stderr = ResponseData["Stderr"]
        RespData.CmdID = ResponseData["ID"]
        RespData.Message = ResponseData["Message"]
        RespData.TimeUpd = datetime.now()
        db.session.commit()
        return {'message': 'OK'}


class InfoApi(Resource):
    def get(self):
        pass  # Вероято тут будет некая хрень для алерты.
              # ?instance=test&source=ewq - Нужно работать с этим как то


api.add_resource(ResultApi, f'/api/{api_v}/result')
api.add_resource(InfoApi, f'/api/{api_v}/info')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0')
