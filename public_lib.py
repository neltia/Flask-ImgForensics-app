# flask lib
from flask import jsonify
from flask_restx import Resource
from flask_restx import Namespace
import os

# develop api version
api_ver = "0.0.1"
path_dir = os.path.abspath(f"./uplodas")
