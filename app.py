# flask lib
from flask import Flask
from flask import jsonify
from flask_restx import Api
# addtion lib
import logging

# app config
app = Flask(__name__)
app.config['SECRET_KEY'] = "justsecretmsg"
logging.basicConfig(level=logging.INFO) # filename="/var/log/flask.log"

# api setting
api = Api(
    app,
    version='0.1',
    title='Trivy API Server',
    description='Trivy 컨테이너를 사용한 도커 취약점 진단'
)


# valid url
@app.errorhandler(404)
def page_not_found(error):
    msg = "Invalid request: Not Found URI"
    return jsonify(
            {
                "result_code": 404,
                "result_message": msg
            }
        ), 404


# Namespace Binding
from info import api as rsc
api.add_namespace(rsc, '/info')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5001)
