# 모듈 호출
from main import *
from flask import Blueprint
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
blueprint = Blueprint("process", __name__, url_prefix='/img')
# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])

# 대시보드
@blueprint.route("/dashboard")
@blueprint.route("/dashboard/<string:hash>")
def page_cover(hash=None):
    logger.warning(hash)
    form = FileForm()
    return render_template("index.html", form=form)
