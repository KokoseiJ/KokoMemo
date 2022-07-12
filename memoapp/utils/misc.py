from flask import Blueprint

import os
from importlib import import_module
from collections import deque


def exhaust(generator):
    deque(generator, maxlen=0)


def gen_bp(import_name, path, name=None):
    if name is None:
        name = import_name.rsplit(".", 1)[-1]

    bp = Blueprint(name, import_name, url_prefix=f"/{name}")

    for module_name in [x for x in os.listdir(path) if not x.startswith("__")]:
        module = import_module(f"{import_name}.{module_name.rstrip('.py')}")
        child_bp = getattr(module, 'bp')
        bp.register_blueprint(child_bp)

    return bp
