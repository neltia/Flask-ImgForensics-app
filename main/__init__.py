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


# default route
@app.route("/")
def index():
    form = FileForm()
    return render_template("index.html", form=form)
