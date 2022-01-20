# 모듈 호출
from flask import Blueprint
from public_lib import *

# blueprint
branch = "projects"
blueprint = Blueprint(branch, __name__, url_prefix='/img')


# 대시보드
@blueprint.route("/imgproc", methods=['GET', 'POST'])
def page_dashboard(img_hash=None):
    if img_hash is None:
        hash_value = request.args.get("img_hash", type=str)
        return redirect(f"/img/dashboard/{hash_value}")

    form = FileForm()
    return render_template(
        "dashboard.html",
        form=form,
        img_hash=img_hash
    )
