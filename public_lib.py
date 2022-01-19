# flask
from flask import render_template
from flask import request, redirect, url_for
import logging

# form
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

# file analysis
import os


# development option
path_dir = os.path.abspath(f"./uplodas")
