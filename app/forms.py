from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, IntegerField, BooleanField
from flask_wtf import FlaskForm


# class ResponseData(FlaskForm):
#     Error = BooleanField('Error')
#     Stdout = StringField('Stdout')
#     Stderr = StringField('Stderr')
#     ID = StringField('ID')
#     Token = StringField('Token')
#     Message = StringField('Message')

class CommandClass(FlaskForm):
    TemplateID = IntegerField("Template ID", validators=[DataRequired()])
    TimeExecute = IntegerField("Time execute command in seconds", validators=[DataRequired()])
    WebhookURL = StringField("Webhook URL", validators=[DataRequired()])
    CommandID = StringField("CommandID")
    FromUser = StringField("FromUser")
    HTTPSecret = StringField("HTTPSecret")
    HTTPUser = StringField("HTTPUser")
    HTTPPassword = StringField("HTTPPassword")
    submit = SubmitField("Submit")


class TemplateAdded(FlaskForm):
    Command = StringField("Command", validators=[DataRequired()])
    Shebang = StringField("Shebang", validators=[DataRequired()])
    UserCrt = StringField("UserCrt", validators=[DataRequired()])
    Interpreter = StringField("Interpreter", validators=[DataRequired()])
    submit = SubmitField("Submit")


class TemplateTrusted(FlaskForm):
    TemplateID = IntegerField("TemplateID", validators=[DataRequired()])
    UserTrust = StringField("UserTrust", validators=[DataRequired()])
    submit = SubmitField("Submit")


class add_post(FlaskForm):
    post_txt = StringField('Текст поста', validators=[DataRequired()])
    submit = SubmitField('Отправить')
