# flask 
from flask import Flask, request, Response
from flask import redirect, url_for, abort
from flask import render_template, jsonify
from datetime import datetime
import os
# form
from flask import send_file
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
# file
from . import process


# app config
app = Flask(__name__)
app.config['SECRET_KEY'] = "justsecretmsg"
app.register_blueprint(process.blueprint)
# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])


@app.errorhandler(404)
def page_not_found(error):
    msg = "존재하지 않는 페이지로 접근했습니다."
    return render_template("status_error.html", msg=msg), 404


# default route
@app.route("/")
def index():
    form = FileForm()
    return render_template("index.html", form=form)
