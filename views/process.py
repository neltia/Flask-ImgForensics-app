# flask
from flask import Blueprint
from matplotlib.image import thumbnail
from public_lib import *
# process lib
import json
# image lib
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash
import exifread
import hashlib


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
blueprint = Blueprint("process", __name__, url_prefix='/img')
# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])


# 대시보드
@blueprint.route("/imgproc", methods=['GET', 'POST'])
def img_process():
    # 로우 데이터 수신
    form = FileForm()
    raw_file = form.form_file.data
    filename = secure_filename(raw_file.filename)
    raw_file.save(f'{path_dir}/{filename}')

    # 파일 이름 SHA-256 값으로 변경
    raw_data = raw_file.read()
    filetype = os.path.splitext(filename)[-1]
    img_hash = hashlib.sha256(raw_data).hexdigest()
    raw_file.close()
    try:
        os.rename(f"{path_dir}/{filename}", f"{path_dir}/{img_hash}{filetype}")
    except FileExistsError:
        pass

    # 이미지 데이터 분석 및 처리
    img_data = {}
    img_data["img_name"] = filename
    img_data["hashed_name"] = f"{img_hash}{filetype}"
    img_data["img_md5"] = hashlib.md5(raw_data).hexdigest()
    img_data["img_sha1"] = hashlib.sha1(raw_data).hexdigest()
    img_data["img_sha256"] = img_hash
    img_data["filesize"] = os.path.getsize(f"{path_dir}/{img_hash}{filetype}")
    img_data["filetype"] = filetype[1:]
    return redirect(url_for("process.page_dashboard", img_hash=img_hash, img_data=img_data))


@blueprint.route("/dashboard/<string:img_hash>")
def page_dashboard(img_hash):
    img_data = json.loads(request.args.get('img_data').replace("'", "\""))
    hashed_name = img_data["hashed_name"]

    image_thumb = Image.open(f"{path_dir}/{hashed_name}")
    image_thumb.thumbnail((100, 100))
    image_thumb.save(f'{path_dir}/thumb_{hashed_name}')

    form = FileForm()
    return render_template(
        "dashboard.html",
        form=form,
        img_hash=img_hash,
        load_name=f"uploads/thumb_{hashed_name}",
        img_data=img_data
    )
