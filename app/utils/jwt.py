from flask import current_app

import hmac
import json
import base64
import hashlib


def get_secret_key():
    return current_app.config['SECRET_KEY']


def hs256(message, secret_key, digest=hashlib.sha256):
    return hmac.new(
        secret_key,
        message,
        digest
    ).digest()


def b64encode(data):
    if isinstance(data, dict):
        data = json.dumps(data)
    if isinstance(data, str):
        data = data.encode()

    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def b64decode(string):
    if isinstance(string, bytes):
        string = string.decode()
    pstr = string + "=" * (4 - len(string) % 4)

    return base64.urlsafe_b64decode(pstr.encode()).decode()


def jwt_encode(payload, secret_key=None):
    if secret_key is None:
        secret_key = get_secret_key()

    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }

    headers_b64 = b64encode(headers)
    payload_b64 = b64encode(payload)

    body = f"{headers_b64}.{payload_b64}"

    sign = b64encode(hs256(body, secret_key))

    return f"{body}.{sign}"


def jwt_decode(payload, secret_key=None):
    if secret_key is None:
        secret_key = get_secret_key()

    jwt_split = payload.split(".")
    
    if len(jwt_split) != 3:
        return 1

    headers_b64, payload_b64, sign = jwt_split

    headers = json.loads(b64decode(headers_b64))

    if headers.get("typ") != "JWT" or headers.get("alg") != "HS256":
        return 1

    body = f"{headers_b64}.{payload_b64}"

    if b64encode(hs256(body, secret_key)) != sign:
        return 2

    return json.loads(b64decode(payload_b64))
