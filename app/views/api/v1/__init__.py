# pylint: disable=wrong-import-position,import-self

from flask import Blueprint

from app.utils import get_module_list

from importlib import import_module

__all__ = get_module_list(__file__)

bp = Blueprint(
    "v1",
    __name__,
    url_prefix="/v1"
)

for viewname in __all__:
    view = import_module(f".{viewname}", __name__)
    sub_bp = getattr(view, "bp")
    bp.register_blueprint(sub_bp)

del Blueprint, get_module_list, import_module, view, viewname, sub_bp
