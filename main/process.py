# 모듈 호출
from main import *
from flask import Blueprint
import logging
from PIL import Image
import imagehash

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
blueprint = Blueprint("process", __name__, url_prefix='/img')
# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])
# path
img_path = "././analysis"

# 대시보드
@blueprint.route("/imgproc", methods=['GET', 'POST'])
def process_dashboard():
    form = FileForm()
    img_data = form.form_file.data
    img_data.save(f'{img_path}/{img_data.filename}')
    print(img_data)
    img_hash = imagehash.average_hash(Image.open(f'{img_path}/{img_data.filename}'))
    print("img_hash:", img_hash)
    return redirect(url_for("process.page_dashboard", img_hash=img_hash))
    # "http://localhost:5000/img/dashboard/{img_hash}")


@blueprint.route("/dashboard", methods=['GET', 'POST'])
@blueprint.route("/dashboard/<string:img_hash>")
def page_dashboard(img_hash=None):
    if img_hash is None:
        hash_value = request.args.get("img_hash", type=str)
        return redirect(f"/img/dashboard/{hash_value}")

    logger.warning(img_hash)
    form = FileForm()
    return render_template(
        "dashboard.html", 
        form=form,
        img_hash=img_hash
    )
