# flask lib
from inspect import signature
from public_lib import *
from flask import request
# addtion lib
from werkzeug.utils import secure_filename
from iptcinfo3 import IPTCInfo
import numpy as np
import cv2
import exifread
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
@api.route(f'/{api_ver}/upload')
class img_info(Resource):
    def post(self):
        # 파일 저장
        raw_file = request.files['file']
        filename = secure_filename(raw_file.filename)
        raw_file.save(f"./uplodas/{filename}")

        # 파일 이름 SHA-256 값으로 변경
        raw_data = raw_file.read()
        filetype = os.path.splitext(filename)[-1]
        hash_sha256 = hashlib.sha256(raw_data).hexdigest()
        raw_file.close()
        try:
            os.rename(f"{path_dir}/{filename}", f"{path_dir}/{hash_sha256}{filetype}")
        except FileExistsError:
            msg = "FileExistsError"
            result = {
                "result_code": -1,
                "result_message": msg,
                "filename": filename,
                "md5": hashlib.md5(raw_data).hexdigest(),
                "sha1": hashlib.sha1(raw_data).hexdigest(),
                "sha256": hash_sha256,
                "filesize": os.path.getsize(f"{path_dir}/{filename}"),
                "filetype": filetype[1:]
            }
            return result

        # Result
        msg = "Success"
        result = {
            "result_code": 0,
            "result_message": msg,
            "filename": filename,
            "md5": hashlib.md5(raw_data).hexdigest(),
            "sha1": hashlib.sha1(raw_data).hexdigest(),
            "sha256": hash_sha256,
            "filesize": os.path.getsize(f"{path_dir}/{filename}"),
            "filetype": filetype[1:]
        }
        return result


# info-2. 이미지 파일 데이터 확인
@api.route(f'/{api_ver}/image')
class img_exif(Resource):
    def get(self):
        result = {}

        # 파라미터 파싱
        params = request.args.to_dict()
        if "hash" not in params:
            result["result_code"] = -1
            result["msg"] = "필수 요청 파라미터 값이 없습니다."
            return result
        filehash = params["hash"]

        # 파일 존재 여부 검사
        file_list = os.listdir(path_dir)
        name_list = [os.path.splitext(fullname)[0] for fullname in file_list]
        if filehash not in name_list:
            result["result_code"] = -1
            result["msg"] = "해당하는 파일이 없습니다."
            return result

        # EXIF Parsing
        filename = file_list[name_list.index(filehash)]
        raw_data = open(f"{path_dir}/{filename}", 'rb')
        tags = exifread.process_file(raw_data)
        raw_data.close()

        # Signatures
        raw_data = open(f"{path_dir}/{filename}", 'rb')
        signatures = raw_data.read(16)
        raw_data.close()

        # ELA (Error Level Analysis)
        # img1 = cv2.imread(f"{path_dir}/{filename}")
        '''
        img_array = np.fromfile(f"{path_dir}/{filename}", np.uint8)
        img1 = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        jpg_quality1 = 95
        jpg_quality2 = 90
        scale = 15
        cv2.imwrite(f"{path_dir}/c95_{filename}", img1, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality1])
        img2 = cv2.imread(f"{path_dir}/c95_{filename}")
        diff1 = scale * cv2.absdiff(img1, img2)
        cv2.imwrite(f"{path_dir}/c90_{filename}", img2, [cv2.IMWRITE_JPEG_QUALITY, jpg_quality2])
        img3 = cv2.imread(f"{path_dir}/c90_{filename}")
        diff2 = scale * cv2.absdiff(img2, img3)
        cv2.imwrite(f"{path_dir}/c95_{filename}", diff1)
        cv2.imwrite(f"{path_dir}/c90_{filename}", diff2)
        cv2.imshow("ela95", diff1)
        cv2.imshow("ela90", diff2)
        cv2.waitKey(0)
        '''

        # IPTCInfo
        info = IPTCInfo(f"{path_dir}/{filename}", force=True)
        print(info)

        # Result
        msg = "test"
        result = {
            "result_code": 0,
            "result_message": msg,
            "sha256": filehash,
            "filesize": os.path.getsize(f"{path_dir}/{filename}"),
            "filetype": os.path.splitext(filename)[-1][1:],
            "sigature": str(signatures),
            "sigature_hex": signatures.hex(),
            "exif_tags": str(tags),
            "iptci_nfo": str(info)
        }
        return result
