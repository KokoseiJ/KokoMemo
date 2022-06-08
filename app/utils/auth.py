from app.models import User

import re
import bcrypt
import hashlib

SHA256_PATTERN = re.compile(r"[0-9a-f]{32}")


def ensure_sha256(pw):
    if SHA256_PATTERN.fullmatch(pw):
        return pw
    else:
        return hashlib.sha256(pw.encode()).hexdigest()


def verify_login(email, pw):
    user = User.query.filter_by(email=email).first()
    if user is None:
        return False

    pw = ensure_sha256(pw)

    if bcrypt.checkpw(pw, user.password):
        return user
    else:
        return False
