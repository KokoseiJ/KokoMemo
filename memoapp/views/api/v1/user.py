from flask import Blueprint

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.get("/")
def test():
    return 'test bp registered successfully!'
