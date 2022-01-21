# flask
from flask import Blueprint
from isort import file
from matplotlib.image import thumbnail
from public_lib import *
# process lib
import json
import random
import string
import hashlib
import datetime
# image lib
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
blueprint = Blueprint("process", __name__, url_prefix='/img')
# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])


# 이미지 처리
@blueprint.route("/imgproc", methods=['GET', 'POST'])
def img_process():
    # 로우 데이터 수신
    form = FileForm()
    raw_file = form.form_file.data
    filename = raw_file.filename

    # 한글 이름 처리 및 데이터 저장
    filename_secure = secure_filename(filename)
    extension = ["jpg", "jpeg", "png", "bmp", "rle", "gif", "psd", "tif", "tiff", "exif", "jfif", "raw", "pdf", "svg"]
    if filename_secure == "" or filename_secure.lower() in extension:
        filename_secure = "".join([random.choice(string.ascii_uppercase) for _ in range(10)]) + ".png"
    raw_file.save(f'{path_dir}/{filename_secure}')

    # 파일 이름 SHA-256 값으로 변경
    with open(f'{path_dir}/{filename_secure}', 'rb') as f:
        raw_data = f.read()
    filetype = os.path.splitext(filename_secure)[-1]
    img_hash = hashlib.sha256(raw_data).hexdigest()
    raw_file.close()
    try:
        os.rename(f"{path_dir}/{filename_secure}", f"{path_dir}/{img_hash}{filetype}")
    except FileExistsError:
        os.remove(f'{path_dir}/{filename_secure}')

    # 이미지 데이터 분석
    # Signatures
    with open(f"{path_dir}/{img_hash}{filetype}", 'rb') as f:
        signatures = f.read(16)

    # PIL open
    # - EXIF
    image_pil = Image.open(f"{path_dir}/{img_hash}{filetype}")
    img_exif = image_pil._getexif()
    image_pil.close()
    exif_data = img_exif.items()
    if exif_data is not None:
        taglabel = {}
        for tag, value in exif_data:
            try:
                decoded = TAGS.get(tag, tag)
            except AttributeError:
                continue
            taglabel[decoded] = value

        # - EXIF GPS parsing
        # 북위/남위 : Key 1 (N/S)
        # 위도(Latitude) : Key 2 (Tuple 형식 3개;도분초;1도=60분=3600초)
        # 동경/서경 : Key 3 (E/W)
        # 경도(Longitude) : Key 4 (Tuple 형식 3개;도분초;1도=60분=3600초)
        # ex) 1: 'N', 2: (37.0, 34.0, 10.2), 3: 'E', 4: (126.0, 53.0, 56.79)
        #     Key 1: 'N',
        #     Key 2: (37.0, 34.0, 10.2),
        #     Key 3: 'E',
        #     Key 4: (126.0, 53.0, 56.79)
        exifGPS = taglabel['GPSInfo']
        latData =  str(get_decimal_from_dms(exifGPS[2], exifGPS[1]))
        longData = str(get_decimal_from_dms(exifGPS[4], exifGPS[3]))
        print(latData, longData)

    # 이미지 데이터 처리
    img_data = {}
    img_data["img_name"] = filename
    img_data["hashed_name"] = f"{img_hash}{filetype}"
    img_data["img_md5"] = hashlib.md5(raw_data).hexdigest()
    img_data["img_sha1"] = hashlib.sha1(raw_data).hexdigest()
    img_data["img_sha256"] = img_hash
    img_data["filesize"] = list(image_pil.size)
    img_data["filevolum"] = os.path.getsize(f"{path_dir}/{img_hash}{filetype}")
    img_data["filetype"] = filetype[1:]
    img_data["exif_gpsinfo"] = [latData, longData]
    img_data["DateTimeOriginal"] = taglabel['DateTimeOriginal']
    img_data["DateTimeDigitized"] = taglabel['DateTimeDigitized']
    img_data["DateTime"] = taglabel['DateTime']
    # img_data["signatures"] =
    print(img_data)
    return redirect(url_for("process.page_dashboard", img_hash=img_hash, img_data=img_data))


# 이미지 데이터 표현
@blueprint.route("/dashboard/<string:img_hash>")
def page_dashboard(img_hash):
    # load data
    img_data = json.loads(request.args.get('img_data').replace("'", "\""))
    hashed_name = img_data["hashed_name"]

    # thumbnail image
    image_thumb = Image.open(f"{path_dir}/{hashed_name}")
    image_thumb.thumbnail((120, 120))
    image_thumb.save(f'{path_dir}/thumb_{hashed_name}')

    # analyzed time
    time = str(datetime.datetime.now())
    analyzed_time=time[:time.find('.')]

    # return
    form = FileForm()
    return render_template(
        "dashboard.html",
        form=form,
        img_hash=img_hash,
        load_name=f"uploads/thumb_{hashed_name}",
        img_data=img_data,
        analyzed_time=analyzed_time
    )
