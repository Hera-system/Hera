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
        form = Templates(Data=form.data.data, DataCrt=datetime.now().timestamp())
        db.session.add(form)
        db.session.commit()
        form = TemplateAdded()
        flash('Форма отправлена!')
    return render_template('addedTemplate.html', form=form)


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
