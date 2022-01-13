# flask lib
from public_lib import *
from flask import request
# addtion lib
import sys
import hashlib
import os


# api default setting
apiGroup = sys.argv[0][:-3]
api = Namespace(
    name="info",
    description="이미지 파일 정보 확인",
)


# info-1. 이미지 파일 업로드
@api.route(f'/{api_ver}/image')
class img_info(Resource):
    def post(self):
        raw_file = request.files['file']
        filename = raw_file.filename
        raw_file.save(f"./uplodas/{filename}")
        raw_data = raw_file.read()
        msg = "Success"
        result = {
            "result_code": 0,
            "result_message": msg,
            "filename": filename,
            "md5": hashlib.md5(raw_data).hexdigest(),
            "sha1": hashlib.sha1(raw_data).hexdigest(),
            "sha256": hashlib.sha256(raw_data).hexdigest()
        }
        return result


# info-2. 이미지 파일 EXIF 데이터 확인
@api.route(f'/{api_ver}/exif')
class img_exif(Resource):
    def get(self):
        msg = "test"
        result = {
            "result_code": 0,
            "result_message": msg
        }
        return result
