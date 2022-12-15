import time
import random
import string
import logging
import requests
import datetime
import threading
import subprocess
from datetime import timedelta

from flask_login import login_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, \
    send_from_directory
from flask_restful import Resource
from flask_pydantic import validate
from pydantic import ValidationError

from app.models import CommandExecution, Templates, Users, WebhookConnect, InfoWebhook, InfoReturnApi, GettingResult, \
    ExecutionCommand, AlertaAuth, ResultWebhook
from app import app, db, api
from app.forms import ExecuteCommand, TemplateAdded, \
    TemplateTrusted, AlertaLogin, TrustTemplate, ExecuteCommandWebhook

api_v = "v1"


def confirm_template(template_id):
    redirect_to = "template"
    template_curr = Templates.query.filter_by(ID=template_id).first()
    if template_curr is None:
        flash("Template not found")
        return redirect(url_for(redirect_to, id=template_id))
    if template_curr.UserCrt == current_user.email and template_curr.UserCrt != app.config['SU_USER']:
        flash("User created template not permission to trusted this template")
        return redirect(url_for(redirect_to, template_id=template_id))
    if template_curr.Trusted:
        flash(f"Template - ID {template_curr.ID} is trusted.")
        return redirect(url_for(redirect_to, id=template_id))
    template_curr.Trusted = True
    template_curr.ID = template_id
    template_curr.UserTrusted = current_user.email
    template_curr.DataTrusted = datetime.datetime.now()
    db.session.commit()
    flash("Template trusted")


def send_exec_cmd(data_exec):
    token = app.config["SECRET_TOKEN"]
    url_secret = app.config["SECRET_URL"]
    request_secret = requests.get(url_secret)
    if request_secret.status_code == 200:
        template_exec = Templates.query.filter_by(ID=data_exec.TemplateID).first()
        try:
            cmd = ExecutionCommand(
                                   ExecCommand=template_exec.Command,
                                   TimeExec=template_exec.TimeExec,
                                   Interpreter=template_exec.Interpreter,
                                   Token=token,
                                   ID=data_exec.CmdID,
                                   HTTPSecret=request_secret.text
            )
        except ValidationError as e:
            print(e)
            return flash(str(e))
        headers = {'Content-type': 'text/plain'}
        request_webhook = requests.post(data_exec.WebhookURL, data=cmd.json(), headers=headers)
        if request_webhook.status_code == 200:
            return flash("Successful send execute command.")
    return flash("Error send execute command.")


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
    db.session.close()
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
        command_exec = reversed(CommandExecution.query.all())
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
        auth = AlertaAuth(password=form.Password.data, username=form.Email.data)
        request_auth = requests.post(app.config["ALERTA_URL"], json=auth.json())
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
                             Interpreter=form.Interpreter.data,
                             TimeExec=form.TimeExecute.data,
                             UserCrt=current_user.email)
            db.session.add(form)
            db.session.commit()
            flash(f'Template added! ID - {form.ID}')
            form = TemplateAdded()
        return render_template('addedTemplate.html', form=form)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/webhooks', methods=['GET', 'POST'])
@login_required
def webhooks_route():
    if current_user.is_authenticated:
        if not app.config['WEBHOOK']['AutoUpdate']:
            x = threading.Thread(target=update_status_webhook, args=(30,))
            logging.info("Start webhook thread")
            x.start()
            app.config['WEBHOOK']['AutoUpdate'] = True
        webhooks = WebhookConnect.query.all()
        return render_template("webhooks.html", webhooks=webhooks)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/webhook/<webhook_id>')
@login_required
def webhook_info(webhook_id):
    if current_user.is_authenticated:
        webhook = WebhookConnect.query.filter_by(ID=int(webhook_id)).first()
        if webhook is None:
            flash(f'Webhook {webhook_id} not found!')
            return redirect(url_for('index'))
        commands = reversed(CommandExecution.query.filter_by(WebhookName=webhook.uniq_name).all())
        return render_template("webhook.html", webhook=webhook, commands=commands)
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/execCmd/<webhook_id>', methods=['GET', 'POST'])
@login_required
def exec_command_by_id(webhook_id):
    if current_user.is_authenticated:
        webhook = WebhookConnect.query.filter_by(uniq_name=webhook_id).first()
        if webhook_id.isdigit() and webhook is None:
            webhook = WebhookConnect.query.filter_by(ID=int(webhook_id)).first()
        if webhook is None:
            flash(f"Error, not found webhook - {webhook_id}")
            db.session.close()
            return redirect(url_for('exec_command'))
        db.session.close()
        webhook_url = webhook.url
        webhook_uniq_name = webhook.uniq_name
        form = ExecuteCommandWebhook()
        if form.validate_on_submit():
            template_exec = Templates.query.filter_by(ID=form.TemplateID.data).first()
            if not (template_exec is None):
                if template_exec.Trusted or current_user.email == app.config['SU_USER']:
                    cmd = CommandExecution(TemplateID=form.TemplateID.data,
                                           WebhookURL=webhook_url+'/execute',
                                           WebhookName=webhook_uniq_name,
                                           FromUser=current_user.email,
                                           CmdID=gen_uniq_id(10))
                    send_exec_cmd(cmd)
                    db.session.add(cmd)
                    db.session.commit()
                    return render_template("execcommad.html", form=form, webhook_name=webhook_uniq_name)
                flash("Template not trusted")
            else:
                flash("Template not found")
        webhook_uniq_name = webhook.uniq_name
        return render_template("execcommad.html", form=form, webhook_name=webhook_uniq_name)
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
                                           TimeExecute=template_exec.TimeExec,
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
    @validate()
    def post(self, body: GettingResult):
        try:
            result = ResultWebhook(Error=body.Error, Stdout=body.Stdout,
                                   Stderr=body.Stderr, Message=body.Message,
                                   ID=body.ID)
        except ValidationError as e:
            return e.json()
        resp_data = CommandExecution.query.filter_by(CmdID=result.ID).first()
        resp_data.Error = result.Error
        resp_data.Stdout = result.Stdout
        resp_data.Stderr = result.Stderr
        resp_data.CmdID = result.ID
        resp_data.Message = result.Message
        resp_data.TimeUpd = datetime.datetime.now()
        db.session.commit()
        return InfoReturnApi(error=False, message="Success. The result is received.")


class ConnectWebhook(Resource):
    @validate()
    def post(self, body: InfoWebhook):
        resp_data = WebhookConnect.query.filter_by(uniq_name=body.webhook_uniq_name).first()
        if not (resp_data is None):
            if body.Token != app.config["SECRET_TOKEN"]:
                return InfoReturnApi(error=True, message="Token not valid"), 401
            resp_data.hostname = body.hostname
            resp_data.username = body.username
            resp_data.version = body.webhook_vers
            resp_data.url = body.webhook_url
            resp_data.uniq_name = body.webhook_uniq_name
            resp_data.os_type = body.os_type
            resp_data.os_arch = body.os_arch
            resp_data.cpu_core = body.cpu_core
            db.session.commit()
            return InfoReturnApi(error=False, message="Webhook successful connected. Information updated.")
        connect = WebhookConnect(hostname=body.hostname,
                                 username=body.username,
                                 version=body.webhook_vers,
                                 url=body.webhook_url,
                                 os_type=body.os_type,
                                 os_arch=body.os_arch,
                                 cpu_core=body.cpu_core,
                                 uniq_name=body.webhook_uniq_name)
        db.session.add(connect)
        db.session.commit()
        return InfoReturnApi(error=False, message="Webhook successful connected. Information created.")


class InfoApi(Resource):
    def get(self):
        pass  # Future alerta integrations this
        # ?instance=test&source=ewq - example URI


api.add_resource(ResultApi, f'/api/{api_v}/result')
api.add_resource(ConnectWebhook, f'/api/{api_v}/result/connect')
api.add_resource(InfoApi, f'/api/{api_v}/info')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


def update_status_webhook(sleep_time):
    while True:
        with app.app_context():
            webhooks = WebhookConnect.query.all()
            for webhook in webhooks:
                try:
                    if not (webhook is None):
                        headers = {'Content-type': 'text/plain'}
                        request_webhook = requests.post(webhook.url+"/healtcheak", headers=headers, timeout=2)
                        if request_webhook.status_code == 200:
                            # webhook_cur = WebhookConnect.query.filter_by(url=webhook.url).first()
                            webhook.active = True
                            webhook.time_connect = datetime.datetime.now()
                        else:
                            webhook.active = False
                        db.session.commit()
                    logging.info(f"Update state - {webhook.uniq_name}")
                except:  # noqa: E722
                    webhook.active = False
                    db.session.commit()
                    logging.error(f"Error update state webhook - {webhook.uniq_name}")
            time.sleep(sleep_time)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
