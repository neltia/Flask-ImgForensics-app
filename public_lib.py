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
path_dir = os.path.abspath(f"./static/uploads")
# path_dir = os.path.abspath(f"./uploads")


def get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)
