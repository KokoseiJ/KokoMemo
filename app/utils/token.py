from flask import current_app

from .jwt import jwt_encode
from .auth import ensure_sha256

import time


def get_verify_token(email, password, name):
    now = round(time.time())

    payload = {
        "ctx": "verify",
        "exp": now + current_app.config['VERIFY_EXPIRY_TIME'],
        "email": email,
        "password": ensure_sha256(password),
        "name": name
    }

    return jwt_encode(payload)


def get_auth_token(user):
    now = round(time.time())

    payload = {
        "ctx": "auth",
        "iat": now,
        "exp": now + current_app.config['AUTH_EXPIRY_TIME'],
        "sub": user.id
    }

    return jwt_encode(payload)
