import time
import random
import string
import logging
import requests
import datetime
import threading
from datetime import timedelta

from flask_login import login_user, current_user, login_required
from flask import render_template, flash, redirect, url_for, \
    send_from_directory, request
from flask_restful import Resource
from flask_pydantic import validate
from pydantic import ValidationError

from app.models import CommandExecution, Templates, Users, WebhookConnect, InfoWebhook, InfoReturnApi, GettingResult, \
    ExecutionCommand, AlertaAuth, ResultWebhook, ArgsCommandExecution, HealthcheckResult
from app import app, db, api
from app.forms import TemplateAdded, TemplateTrusted, \
    AlertaLogin, TrustTemplate, ExecuteCommandWebhook  # , ExecuteCommand

api_v = "v1"


def confirm_template(template_id):
    redirect_to = "template"
    template_curr = Templates.query.filter_by(ID=template_id).first()
    if template_curr is None:
        flash("Template not found")
        return redirect(url_for(redirect_to, template_id=template_id))
    if template_curr.UserCrt == current_user.email and template_curr.UserCrt != app.config['SU_USER']:
        flash("User created template not permission to trusted this template")
        return redirect(url_for(redirect_to, template_id=template_id))
    if template_curr.Trusted:
        flash(f"Template - ID {template_curr.ID} is trusted.")
        return redirect(url_for(redirect_to, template_id=template_id))
    template_curr.Trusted = True
    template_curr.ID = template_id
    template_curr.UserTrusted = current_user.email
    template_curr.DataTrusted = datetime.datetime.now()
    db.session.commit()
    flash("Template trusted")


def send_exec_cmd(data_exec):
    token = app.config["SECRET_TOKEN"]
    url_secret = app.config["SECRET_URL"]
    cmd = CommandExecution(TemplateID=data_exec.TemplateID,
                           WebhookURL=data_exec.WebhookURL,
                           WebhookName=data_exec.WebhookName,
                           FromUser=data_exec.FromUser,
                           CmdID=data_exec.CmdID)
    db.session.add(cmd)
    db.session.commit()
    db.session.close()
    request_secret = requests.get(url_secret, timeout=2)
    if request_secret.status_code == 200:
        try:
            cmd = ExecutionCommand(
                                   ExecCommand=data_exec.ExecCommand,
                                   TimeExec=data_exec.TimeExec,
                                   Interpreter=data_exec.Interpreter,
                                   Token=token,
                                   ID=data_exec.CmdID,
                                   HTTPSecret=request_secret.text
            )
        except ValidationError as e:
            print(e)
            return flash(str(e))
        webhook_cur = WebhookConnect.query.filter_by(uniq_name=data_exec.WebhookName).first()
        if webhook_cur is not None:
            if webhook_cur.connect_type == "reverse":
                return flash("Command set in queue to webhook")
        headers = {'Content-type': 'text/plain'}
        request_webhook = requests.post(data_exec.WebhookURL, data=cmd.json(), headers=headers, timeout=2)
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
    f = open("revision.txt", "r")
    revision = f.readline()
    f.close()
    return revision


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
        page = request.args.get('page', default=1, type=int)
        templates_all = Templates.query.order_by(Templates.ID.desc()).paginate(
            page=page,
            per_page=app.config['ITEMS_PER_PAGE'],
            error_out=True
        )
        return render_template(
            "templates.html",
            templates=templates_all.items,
            lenght_str=15,
            pagination=True,
            current_page=templates_all.page,
            pages=templates_all.pages
        )
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/commands')
@login_required
def commands():
    if current_user.is_authenticated:
        page = request.args.get('page', default=1, type=int)
        command_exec = CommandExecution.query.order_by(CommandExecution.RowID.desc()).paginate(
            page=page,
            per_page=app.config['ITEMS_PER_PAGE'],
            error_out=True
        )
        return render_template(
            "commands.html",
            commands=command_exec.items,
            pagination=True,
            current_page=command_exec.page,
            pages=command_exec.pages
        )
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
            return redirect(url_for(request.args.get('next', default="webhooks", type=str)[1:]))
        auth = AlertaAuth(password=form.Password.data, username=form.Email.data)
        request_auth = requests.post(app.config["ALERTA_URL"], json=auth.json())
        if request_auth.status_code == 200:
            login_user(get_user(form.Email.data), form.RememberMe.data, timedelta(days=1))
            flash("You are authorized in Hera system!")
            return redirect(url_for(request.args.get('next', default="webhooks", type=str)[1:]))
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
def addTemplate():
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
def webhooks():
    if current_user.is_authenticated:
        if not app.config['WEBHOOK']['AutoUpdate']:
            x = threading.Thread(target=update_status_webhook, args=(30,))
            logging.info("Start webhook thread")
            x.start()
            app.config['WEBHOOK']['AutoUpdate'] = True
        page = request.args.get('page', default=1, type=int)
        webhooks_all = WebhookConnect.query.order_by(WebhookConnect.ID.desc()).paginate(
            page=page,
            per_page=app.config['ITEMS_PER_PAGE'],
            error_out=True
        )
        return render_template(
            "webhooks.html",
            webhooks=webhooks_all.items,
            pagination=True,
            current_page=webhooks_all.page,
            pages=webhooks_all.pages
        )
    flash("You are not authorized")
    return redirect(url_for('login'))


@app.route('/webhook/<webhook_id>')
@login_required
def webhook_info(webhook_id):
    if current_user.is_authenticated:
        webhook = None
        if webhook_id.isdigit():
            webhook = WebhookConnect.query.filter_by(ID=int(webhook_id)).first()
        if webhook is None:
            webhook = WebhookConnect.query.filter_by(uniq_name=webhook_id).first()
        if webhook is None:
            flash(f'Webhook {webhook_id} not found!')
            return redirect(url_for('index'))
        page = request.args.get('page', default=1, type=int)
        command_all = CommandExecution.query.filter_by(WebhookName=webhook.uniq_name).\
            order_by(CommandExecution.RowID.desc()).paginate(
            page=page,
            per_page=app.config['ITEMS_PER_PAGE'],
            error_out=True
        )
        return render_template(
            "webhook.html",
            webhook=webhook,
            commands=command_all.items,
            pagination=True,
            current_page=command_all.page,
            pages=command_all.pages
        )
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
                    cmd = ArgsCommandExecution(
                                            TemplateID=form.TemplateID.data,
                                            WebhookURL=webhook_url+'/execute',
                                            WebhookName=webhook_uniq_name,
                                            FromUser=current_user.email,
                                            CmdID=gen_uniq_id(10),
                                            ExecCommand=template_exec.Command,
                                            TimeExec=template_exec.TimeExec,
                                            Interpreter=template_exec.Interpreter
                    )
                    send_exec_cmd(cmd)
                    db.session.commit()
                    db.session.close()
                    return render_template("execcommad.html", form=form, webhook_name=webhook_uniq_name)
                flash("Template not trusted")
            else:
                flash("Template not found")
        webhook_uniq_name = webhook.uniq_name
        return render_template("execcommad.html", form=form, webhook_name=webhook_uniq_name)
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

def update_info_webhook(body: InfoWebhook):
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
        resp_data.connect_type = body.connect_type
        db.session.commit()
        return InfoReturnApi(error=False, message="Webhook successful connected. Information updated.")
    connect = WebhookConnect(hostname=body.hostname,
                             username=body.username,
                             version=body.webhook_vers,
                             url=body.webhook_url,
                             os_type=body.os_type,
                             os_arch=body.os_arch,
                             cpu_core=body.cpu_core,
                             connect_type=body.connect_type,
                             uniq_name=body.webhook_uniq_name)
    db.session.add(connect)
    db.session.commit()
    return InfoReturnApi(error=False, message="Webhook successful connected. Information created.")



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
            resp_data.connect_type = body.connect_type
            resp_data.time_connect = datetime.datetime.now()
            db.session.commit()
            return InfoReturnApi(error=False, message="Webhook successful connected. Information updated.")
        connect = WebhookConnect(hostname=body.hostname,
                                 username=body.username,
                                 version=body.webhook_vers,
                                 url=body.webhook_url,
                                 os_type=body.os_type,
                                 os_arch=body.os_arch,
                                 cpu_core=body.cpu_core,
                                 connect_type=body.connect_type,
                                 uniq_name=body.webhook_uniq_name,
                                 time_connect = datetime.datetime.now())
        db.session.add(connect)
        db.session.commit()
        return InfoReturnApi(error=False, message="Webhook successful connected. Information created.")


class Healthcheck(Resource):
    @validate()
    def post(self, body: InfoWebhook):
        if body.connect_type != "reverse":
            return "Method not supported for current webhook type", 405
        ConnectWebhook.post(body)
        command_execution = CommandExecution.query.filter_by(WebhookName=body.webhook_uniq_name).filter_by(TimeUpd=None).first()  # noqa: E501
        if command_execution is None:
            return HealthcheckResult(
                Status="OK.", ExecCommand="", Interpreter="", Token="", TimeExec=0, ID="", HTTPSecret=""
            )
        command_execution.TimeUpd = datetime.datetime.now()
        template = Templates.query.filter_by(ID=command_execution.TemplateID).first()
        if template is None:
            return HealthcheckResult(
                Status="Template not found.", ExecCommand="", Interpreter="", Token="", TimeExec=0, ID="", HTTPSecret=""
            )
        request_secret = requests.get(app.config["SECRET_URL"], timeout=2)
        if request_secret.status_code == 200:
            return HealthcheckResult(
                Status="Queued.", ExecCommand=template.Command, Interpreter=template.Interpreter,
                Token=app.config["SECRET_TOKEN"], TimeExec=template.TimeExec, ID=command_execution.CmdID,
                HTTPSecret=request_secret.text
                )
        return HealthcheckResult(
            Status="Error.", ExecCommand="", Interpreter="", Token="", TimeExec=0, ID="", HTTPSecret=""
        )


class InfoApi(Resource):
    def get(self):
        pass  # Future alerta integrations this
        # ?instance=test&source=ewq - example URI


api.add_resource(ResultApi, f'/api/{api_v}/result')
api.add_resource(ConnectWebhook, f'/api/{api_v}/result/connect')
api.add_resource(Healthcheck, f'/api/{api_v}/healthcheck')
api.add_resource(InfoApi, f'/api/{api_v}/info')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


def update_status_webhook(sleep_time):
    while True:
        with app.app_context():
            webhooks = WebhookConnect.query.filter_by(connect_type="direct")
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
