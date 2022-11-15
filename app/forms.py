from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, IntegerField, BooleanField,\
    PasswordField
from flask_wtf import FlaskForm


class CommandClass(FlaskForm):
    TemplateID = IntegerField("Template ID", validators=[DataRequired()])
    TimeExecute = IntegerField("Time execute command in seconds",
                               validators=[DataRequired()])
    WebhookURL = StringField("Webhook URL", validators=[DataRequired()])
    CommandID = StringField("CommandID")
    FromUser = StringField("FromUser")
    HTTPSecret = StringField("HTTPSecret")
    HTTPUser = StringField("HTTPUser")
    HTTPPassword = StringField("HTTPPassword")
    submit = SubmitField("Submit")


class ExecuteCommand(FlaskForm):
    WebhookURL = StringField("Webhook URL", validators=[DataRequired()])
    TemplateID = IntegerField("Template ID", validators=[DataRequired()])
    TimeExecute = IntegerField("Time execute command in seconds",
                               validators=[DataRequired()])
    submit = SubmitField("Submit")


class ExecuteCommandWebhook(FlaskForm):
    TemplateID = IntegerField("Template ID", validators=[DataRequired()])
    TimeExecute = IntegerField("Time execute command in seconds",
                               validators=[DataRequired()])
    submit = SubmitField("Submit")


class TemplateAdded(FlaskForm):
    Command = StringField("Command", validators=[DataRequired()])
    Shebang = StringField("Shebang", validators=[DataRequired()])
    Interpreter = StringField("Interpreter", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TemplateTrusted(FlaskForm):
    TemplateID = IntegerField("TemplateID", validators=[DataRequired()])
    submit = SubmitField("Submit")


class AlertaLogin(FlaskForm):
    Email = StringField('Email', validators=[DataRequired()])
    Password = PasswordField('Password', validators=[DataRequired()])
    RememberMe = BooleanField('Remember me')
    Submit = SubmitField('Submit')


class TrustTemplate(FlaskForm):
    submit = SubmitField("Trust")
