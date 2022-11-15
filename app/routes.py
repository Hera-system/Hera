import json
import random
import string
import requests
import datetime
import subprocess
from datetime import timedelta

from flask_login import login_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, request, \
    send_from_directory
from flask_restful import Resource

from app.models import CommandExecution, Templates, Users, WebhookConnect
from app import app, db, api
from app.forms import ExecuteCommand, TemplateAdded, \
    TemplateTrusted, AlertaLogin, TrustTemplate

api_v = "v1"


def confirm_template(template_id):
    redirect_to = "template"
    template_curr = Templates.query.filter_by(ID=template_id).first()
    if template_curr is None:
        flash("Template not found")
        return redirect(url_for(redirect_to, id=template_id))
    if template_curr.UserCrt == current_user.email:
        flash("User created template not permission to trusted this template")
        return redirect(url_for(redirect_to, id=template_id))
    if template_curr.Trusted:
        flash(f"Template - ID {template_curr.ID} is trusted.")
        return redirect(url_for(redirect_to, id=template_id))
    template_curr.Trusted = True
    template_curr.ID = template_id
    template_curr.UserTrusted = current_user.email
    template_curr.DataTrusted = datetime.now()
    db.session.commit()
    flash("Template trusted")


def send_exec_cmd(data_exec):
    token = app.config["SECRET_TOKEN"]
    url_secret = app.config["SECRET_URL"]
    request_secret = requests.get(url_secret)
    if request_secret.status_code == 200:
        template_exec = Templates.query.filter_by(ID=data_exec.TemplateID).first()
        cmd = {
            "ExecCommand": template_exec.Command,
            "Shebang": template_exec.Shebang,
            "Interpreter": template_exec.Interpreter,
            "Token": token,
            "TimeExec": data_exec.TimeExecute,
            "ID": data_exec.CmdID,
            "HTTPSecret": request_secret.text
        }
        headers = {'Content-type': 'text/plain'}
        request_webhook = requests.post(data_exec.WebhookURL, json=cmd, headers=headers)
        if request_webhook.status_code == 200:
            return flash("Successful send execute command.")
    return flash("Error send execute command. Pls check URL")


def gen_uniq_id(lenght: int) -> str:
    rnd_string = ""
    rnd_list = ['ascii_lowercase', 'ascii_uppercase', 'digits']
    ascii_lowercase = list(string.ascii_lowercase)
    ascii_uppercase = list(string.ascii_uppercase)
    digits = list(string.digits)
    for i in range(lenght):
        rnd_choice = random.choices(rnd_list, k=1)[0]
        if rnd_choice == "ascii_lowercase":
            rnd_string = rnd_string + random.choices(ascii_lowercase, k=1)[0]
        if rnd_choice == "ascii_uppercase":
            rnd_string = rnd_string + random.choices(ascii_uppercase, k=1)[0]
        if rnd_choice == "digits":
            rnd_string = rnd_string + random.choices(digits, k=1)[0]
    check_query = CommandExecution.query.filter_by(CmdID=rnd_string).first()
    if check_query is None:
        return rnd_string
    return gen_uniq_id(lenght)


def get_git_revision_short_hash() -> str:
    return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', git_revision=get_git_revision_short_hash())


def get_user(email):
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
        template_all = Templates.query.all()
        return render_template("templates.html", templates=template_all, lenght=15)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/commands')
@login_required
def commands():
    if current_user.is_authenticated:
        command_exec = CommandExecution.query.all()
        return render_template("commands.html", commands=command_exec)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/command/<template_id>')
@login_required
def command(template_id):
    if current_user.is_authenticated:
        if template_id.isdigit():
            command_exec = CommandExecution.query.filter_by(RowID=int(template_id)).first()
            return render_template("command.html", command=command_exec)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/template/<template_id>', methods=['GET', 'POST'])
@login_required
def template(template_id):
    if current_user.is_authenticated:
        if template_id.isdigit():
            template_curr = Templates.query.filter_by(ID=int(template_id)).first()
            form = TrustTemplate()
            if form.validate_on_submit():
                confirm_template(template_id)
            return render_template("template.html", template=template_curr, form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AlertaLogin()
    if form.validate_on_submit():
        if form.Email.data == app.config['SU_USER'] and form.Password.data == app.config['SU_PASS']:
            login_user(get_user(form.Email.data), form.RememberMe.data, timedelta(days=1))
            flash("You are authorized in Hera system!")
            return redirect(url_for('templates'))
        cmd = {"password": form.Password.data, "username": form.Email.data}
        request_auth = requests.post(app.config["ALERTA_URL"], json=cmd)
        if request_auth.status_code == 200:
            login_user(get_user(form.Email.data), form.RememberMe.data, timedelta(days=7))
            flash("You are authorized in Hera system!")
            return redirect(url_for('templates'))
    return render_template('login.html', form=form)


@app.route('/confirmTemplate', methods=['GET', 'POST'])
@login_required
def confirm_templates():
    if current_user.is_authenticated:
        form = TemplateTrusted()
        if form.validate_on_submit():
            confirm_template(form.TemplateID.data)
        return render_template('trustedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/addTemplate', methods=['GET', 'POST'])
@login_required
def add_template():
    if current_user.is_authenticated:
        form = TemplateAdded()
        if form.validate_on_submit():
            form = Templates(Command=form.Command.data,
                             Shebang=form.Shebang.data,
                             Interpreter=form.Interpreter.data,
                             UserCrt=current_user.email)
            db.session.add(form)
            db.session.commit()
            flash(f'Template added! ID - {form.ID}')
            form = TemplateAdded()
        return render_template('addedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/execCommand', methods=['GET', 'POST'])
@login_required
def exec_command():
    if current_user.is_authenticated:
        form = ExecuteCommand()
        if form.validate_on_submit():
            template_exec = Templates.query.filter_by(ID=form.TemplateID.data).first()
            if not (template_exec is None):
                if template_exec.Trusted or current_user.email == app.config['SU_USER']:
                    cmd = CommandExecution(TemplateID=form.TemplateID.data,
                                           WebhookURL=form.WebhookURL.data,
                                           TimeExecute=form.TimeExecute.data,
                                           FromUser=current_user.email,
                                           CmdID=gen_uniq_id(10))
                    db.session.add(cmd)
                    db.session.commit()
                    send_exec_cmd(cmd)
                    return render_template("execcommad.html", form=form)
                flash("Template not trusted")
            else:
                flash("Template not found")
        return render_template("execcommad.html", form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/', 'image/favicons/favicon.ico')


class ResultApi(Resource):
    def post(self):
        response_data = json.loads(request.data.decode("utf-8"))
        resp_data = CommandExecution.query.filter_by(CmdID=response_data["ID"]).first()
        resp_data.Error = response_data["Error"]
        resp_data.Stdout = response_data["Stdout"]
        resp_data.Stderr = response_data["Stderr"]
        resp_data.CmdID = response_data["ID"]
        resp_data.Message = response_data["Message"]
        resp_data.TimeUpd = datetime.now()
        db.session.commit()
        return {'message': 'OK'}


class ConnectWebhook(Resource):
    def post(self):
        print("LOL")
        return {'message': 'OK'}
        # response_data = json.loads(request.data.decode("utf-8"))
        # resp_data = WebhookConnect.query.filter_by(webhook_uniq_name=response_data["webhook_uniq_name"]).first()
        # if not (resp_data is None):
        #     resp_data.webhook_hostname = response_data["hostname"]
        #     resp_data.webhook_username = response_data["username"]
        #     resp_data.webhook_version = response_data["webhook_vers"]
        #     resp_data.webhook_cmd_url = response_data["webhook_cmd_url"]
        #     resp_data.webhook_uniq_name = response_data["webhook_uniq_name"]
        #     db.session.commit()
        #     return {'message': 'OK'}
        # connect = WebhookConnect(webhook_hostname=response_data["hostname"],
        #                          webhook_username=response_data["username"],
        #                          webhook_version=response_data["webhook_vers"],
        #                          webhook_cmd_url=response_data["webhook_cmd_url"],
        #                          webhook_uniq_name=response_data["webhook_uniq_name"])
        # db.session.add(connect)
        # db.session.commit()
        # return {'message': 'OK'}


class InfoApi(Resource):
    def get(self):
        pass  # Вероято тут будет некая хрень для алерты.
        # ?instance=test&source=ewq - Нужно работать с этим как то


api.add_resource(ResultApi, f'/api/{api_v}/result')
api.add_resource(ConnectWebhook, f'/api/{api_v}/result/WebhookConnect')
api.add_resource(InfoApi, f'/api/{api_v}/info')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(host='0.0.0.0')
