from flask import Blueprint, request

from app.utils import resp_json, check_keys
from app.utils.auth import verify_login
from app.utils.token import get_auth_token

bp = Blueprint(
    "user",
    __name__,
    url_prefix="/user"
)


@bp.post("/login")
def login():
    check = check_keys(request.json, ("email", "password"))
    if check is not None:
        if check is True:
            return resp_json("Request should contain a valid JSON data.", 400)
        else:
            return resp_json("Malformed request.", 400)

    email = request.json['email']
    passwd = request.json['password']

    user = verify_login(email, passwd)

    if not user:
        return resp_json("Incorrect E-Mail or Password", 401)

    token = get_auth_token(user)

    return resp_json("Successfully Logged in!", data=token)


@bp.post("/register")
def register():
    check = check_keys(request.json, ("email", "password", "name"))
    if check is not None:
        if check is True:
            return resp_json("Request should contain a valid JSON data.", 400)
        else:
            return resp_json("Malformed request.", 400)

        
