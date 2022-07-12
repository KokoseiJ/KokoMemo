from flask import Blueprint

bp = Blueprint('test', __name__, url_prefix='/test')


@bp.get("/")
def test():
    return 'test bp registered successfully!'
