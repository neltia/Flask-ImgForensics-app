# flask
from flask import Blueprint
from public_lib import *
from flask import flash
# image lib
from werkzeug.utils import secure_filename
from PIL import Image
from PIL.ExifTags import TAGS
import binascii
# process lib
from pymongo import MongoClient
import random
import string
import hashlib
import pytesseract
import clipboard
import bson


# var setting
blueprint = Blueprint("process", __name__, url_prefix='/process')
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
connection = MongoClient()
db = connection["img_forensic"]
collection = db["imginfo"]
cursor = db.collection

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# form setting
class FileForm(FlaskForm):
    form_file = FileField(validators=[FileRequired('업로드할 파일을 넣어주세요')])


# 이미지 처리
@blueprint.route("/imgproc", methods=['POST'])
def process_img():
    # 로우 데이터 수신
    form = FileForm()
    raw_file = form.form_file.data
    filename = raw_file.filename
    img_data = {}

    # 한글 이름 처리 및 데이터 저장
    allow_extension = ["jpg", "jpeg", "png", "bmp", "rle", "gif", "psd", "tif", "tiff", "exif", "jfif", "raw", "pdf", "svg"]
    allow_mintype = ["image/png", "image/jpeg"]

    filename_secure = secure_filename(filename)
    if filename_secure == "" or filename_secure.lower() in allow_extension:
        filename_secure = "".join([random.choice(string.ascii_uppercase) for _ in range(10)]) + ".png"
    raw_file.save(f'{path_dir}/{filename_secure}')

    # 파일 이름 SHA-256 값으로 변경
    with open(f'{path_dir}/{filename_secure}', 'rb') as f:
        raw_data = f.read()
    filetype = os.path.splitext(filename_secure)[-1]
    # - 확장자 검사 (check. 1 file_extension)
    minetype = raw_file.mimetype
    if minetype not in allow_mintype:
        flash("허용되지 않은 파일입니다.")
        return redirect("/")

    img_hash = hashlib.sha256(raw_data).hexdigest()
    raw_file.close()
    try:
        os.rename(f"{path_dir}/{filename_secure}", f"{path_dir}/{img_hash}{filetype}")
    except FileExistsError:
        os.remove(f'{path_dir}/{filename_secure}')

    # exists check
    query_data = cursor.find_one({"img_sha256": img_hash})
    if query_data is not None:
        cursor.delete_one({"img_sha256": img_hash})

    # 이미지 데이터 분석
    # - Signatures
    with open(f"{path_dir}/{img_hash}{filetype}", 'rb') as f:
        file_bin = f.read()
    file_hex = binascii.b2a_hex(file_bin)
    header_signature = file_hex[:16].decode('utf-8').upper()
    footer_signatrue = file_hex[-16:].decode('utf-8').upper()

    # PIL open
    # - OCR & EXIF
    image_pil = Image.open(f"{path_dir}/{img_hash}{filetype}")
    img_pytesseract_en = pytesseract.image_to_string(image_pil)
    # img_pytesseract_kor = pytesseract.image_to_string(image_pil, lang='kor')

    img_exif = image_pil._getexif()
    image_pil.close()
    try:
        exif_data = img_exif.items()
    except AttributeError:
        exif_data = None
    if exif_data is None:
        img_data["exif_data"] = {}
    else:
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
        if 'GPSInfo' in taglabel:
            exifGPS = taglabel['GPSInfo']
            try:
                latData =  str(get_decimal_from_dms(exifGPS[2], exifGPS[1]))
                longData = str(get_decimal_from_dms(exifGPS[4], exifGPS[3]))
                img_data["exif_gpsinfo"] = [latData, longData]
            except KeyError:
                print("exifGPS:", exifGPS)
            del taglabel["GPSInfo"]

        # - exif meta data
        # img_data.update(taglabel)
        if "XResolution" in taglabel or "YResolution" in taglabel:
            del taglabel["XResolution"]
            del taglabel["YResolution"]
        img_data["exif_data"] = taglabel

    # 이미지 데이터 처리
    img_data["img_name"] = filename
    img_data["hashed_name"] = f"{img_hash}{filetype}"
    img_data["img_md5"] = hashlib.md5(raw_data).hexdigest()
    img_data["img_sha1"] = hashlib.sha1(raw_data).hexdigest()
    img_data["img_sha256"] = img_hash
    img_data["filesize"] = list(image_pil.size)
    img_data["filevolum"] = os.path.getsize(f"{path_dir}/{img_hash}{filetype}")
    img_data["filetype"] = filetype[1:]
    # - signatrue
    img_data["header_signature"] = header_signature
    img_data["footer_signatrue"] = footer_signatrue
    # - image ocr
    img_data["img_strings_en"] = str(img_pytesseract_en)

    # db insert
    try:
        cursor.insert_one(img_data)
    except bson.errors.InvalidDocument:
        print(img_data)
        error_msg = "이미지를 처리하는 중 오류가 발생했습니다."
        flash(error_msg)
        return redirect("/")
    return redirect(url_for("result.page_dashboard", img_hash=img_hash))


# 이미지 처리
@blueprint.route("/copy/<string:img_hash>/<string:data>")
def process_clipboard(img_hash, data):
    clipboard.copy(data)
    flash("클립보드에 복사되었습니다!")
    return redirect(url_for("result.page_dashboard", img_hash=img_hash))
