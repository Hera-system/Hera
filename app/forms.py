from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, BooleanField
from flask_wtf import FlaskForm


# class ResponseData(FlaskForm):
#     Error = BooleanField('Error')
#     Stdout = StringField('Stdout')
#     Stderr = StringField('Stderr')
#     ID = StringField('ID')
#     Token = StringField('Token')
#     Message = StringField('Message')

class TemplateAdded(FlaskForm):
    data = StringField("Template", validators=[DataRequired()])
    submit = SubmitField("Добавить")


class add_post(FlaskForm):
    post_txt = StringField('Текст поста', validators=[DataRequired()])
    submit = SubmitField('Отправить')
