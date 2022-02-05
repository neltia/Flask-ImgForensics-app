# flask
from flask import Blueprint
from public_lib import *
# image lib
from PIL import Image
# process lib
from pymongo import MongoClient
import datetime
import folium
import pytesseract


# var setting
blueprint = Blueprint("result", __name__, url_prefix='/img')
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


# 이미지 데이터 표현
@blueprint.route("/dashboard/<string:img_hash>")
def page_dashboard(img_hash):
    # load data (db find)
    img_data = cursor.find_one({"img_sha256": img_hash})
    hashed_name = img_data["hashed_name"]

    # folium map
    if "exif_gpsinfo" in img_data:
        locatoin = tuple(img_data["exif_gpsinfo"])
        folium_map = folium.Map(location=locatoin, zoom_start=15)
        folium.Marker(img_data["exif_gpsinfo"],
                popup="This Place",
                tooltip="This Place").add_to(folium_map)
        folium_map=folium_map._repr_html_()
    else:
        folium_map = "<div></div>"

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
        "result.html",
        form=form,
        img_hash=img_hash,
        load_name=f"uploads/thumb_{hashed_name}",
        img_data=img_data,
        analyzed_time=analyzed_time,
        folium_map=folium_map
    )
