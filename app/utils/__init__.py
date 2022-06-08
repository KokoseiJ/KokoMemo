from flask import jsonify

import os


def resp_json(message="", code=200, data=None):
    return jsonify({
        "meta": {
            "message": message,
            "code": code
        },
        "data": data
    }), code


def check_keys(data, keys):
    if not data:
        return True

    empty = object()

    for key in keys:
        if data.get(key, empty) is empty:
            return key

    return None


def get_module_list(filepath):
    path = os.path.dirname(os.path.abspath(filepath))

    return [
        x.rstrip(".py") for x in os.listdir(path)
        if not x.startswith("_")
    ]
