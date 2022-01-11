# flask lib
from public_lib import *
# addtion lib
import sys


# api default setting
apiGroup = sys.argv[0][:-3]
api = Namespace(
    name="info",
    description="이미지 파일 정보 확인",
)


# info-1. 이미지 파일 EXIF 데이터 확인
@api.route(f'/{api_ver}/image')
class img_info(Resource):
    def get(self):
        msg = "test"
        result = {
            "result_code": 0,
            "result_message": msg
        }
        return result
