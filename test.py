import pytest

import json
import hashlib
import requests

TEST_URL = "http://127.0.0.1:5000"

TEST_NAME = "TestUser001"
TEST_EMAIL = "testuser@testemail.com"
TEST_PW = "I_am_testuser"


def merge_route(baseurl, route):
    baseurl = baseurl.rstrip("/")
    route = route.lstrip("/")

    return f"{baseurl}/{route}"


class MemoHTTPError(Exception):
    def __init__(self, status, message):
        self.args = (f"Status {status}: {message}")
        self.status = status
        self.message = message


class MemoClient:
    def __init__(self, url=TEST_URL):
        self.url = url

        self.session = requests.session()
        self.session.headers.update({"User-Agent": "TestMemoClient"})

        self.token = None

    # ===== User =====

    def register(self, email, pw, name):
        data = {
            "email": email,
            "password": hashlib.sha256(pw).hexdigest(),
            "name": name
        }

        return self._request(
            "POST", "/user/register", data, noauth=True)['data']

    def read_register_token(self):
        return self._request(
            "GET", "/user/register/_read_token", noauth=True)['data']

    def register_verify(self, token):
        url = f"/user/register/verify?token={token}"
        return self._request("GET", url, noauth=True)['data']

    def login(self, email, pw):
        data = {
            "email": email,
            "password": hashlib.sha256(pw).hexdigest()
        }

        return self._request("POST", "/user/login", data, noauth=True)['data']

    # ===== Memo =====

    def get_all_memos(self):
        return self._request("GET", "/memo/all")['data']

    def get_root(self):
        return self._request("GET", "/memo")['data']

    def get_memo(self, id_):
        return self._request("GET", f"/memo/{id_}")['data']

    def post_memo(self, type_, name, content=None, parent=None):
        data = {
            "type": type_,
            "name": name,
            "parent": parent
        }

        if type_ == "M" and content is not None:
            data.update({"content": content})

        return self._request("POST", "/memo")['data']

    def edit_memo(
            self, id_, name=None, content=None, parent=None, version=None):
        data = {}

        for key in ["id_", "name", "content", "parent", "version"]:
            value = locals().get(key.strip("_"))
            if value is not None:
                data.update({key: value})

        return self._request("PUT", f"/memo/{id_}", data)['data']

    def delete_memo(self, id_):
        return self._request("DELETE", f"/memo/{id_}")['data']

    def update_memo(self, data):
        return self._request("POST", "/memo/update", data)['data']

    # ===== End =====

    def _request(self, method, route, data=None, noauth=False, **kwargs):
        req_url = merge_route(self.baseurl, route)

        headers = {}

        if data is not None and isinstance(data, dict):
            data = json.dumps(data).encode()
            headers.update({"Content-Type": "application/json"})

        if not noauth:
            headers.update({"Authorization": f"Bearer {self.token}"})

        request_kwargs = {
            "method": method,
            "url": req_url
        }

        if data is not None:
            request_kwargs.update({"data": data})

        request_kwargs.update({"headers": headers})
        request_kwargs.update(kwargs)

        r = self.session.request(**request_kwargs)

        if r.status_code // 100 != 2:
            error = r.json()['meta']
            message = error['message']

            raise MemoHTTPError(r.status_code, message)

        return r.json()


@pytest.fixture
def client():
    client = MemoClient()
    client.token = client.login(TEST_EMAIL, TEST_PW)
    return client


class TestUser:
    def __init__(self):
        def email_enum():
            i = 1
            while True:
                yield f"nonexistent{i}@testemail.com"

        self.emailgen = email_enum()

    def test_register(self, client):
        email = next(self.emailgen)
        client.register(
            email,
            TEST_PW,
            TEST_NAME
        )

        token = client.read_register_token()

        client.register_verify(token)

        client.login(email, TEST_PW)

    def test_fail_register(self, client):
        with pytest.raises(
                MemoHTTPError, 
                match=r"Status 403\: .*E\-mail.*"
        ):
            client.register(TEST_EMAIL, TEST_PW, TEST_NAME)

    def test_fail_verify(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 400\: .*Malformed.*"
        ):
            client.register_verify("improperly_formatted_token")

    def test_fail_verify_late(self, client):
        email = next(self.emailgen)
        client.register(
            email,
            TEST_PW,
            TEST_NAME
        )
        token = client.read_register_token()
        client.register_verify(token)

        with pytest.raises(
                MemoHTTPError,
                match=r"Status 403\: .*Already.*"
        ):
            client.register_verify(token)

    def test_fail_verify_signature(self, client):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE1MTYyMzkwMjI"\
                "sImVtYWlsIjoibm9uZXhpc3RlbnQ2OUB0ZXN0ZW1haWwuY29tIiwicGFzc3d"\
                "vcmQiOiJyYW5kb20gcGFzc3dvcmQiLCJuYW1lIjoidGVzdHVzZXIifQ.J0CQ"\
                "UR27t1my8cvXZjbjcolCU4NwYqyrzT7Tn-Ztcro"

        with pytest.raises(
                MemoHTTPError,
                match=r"Status 403\: .*Signature.*"
        ):
            client.register_verfiy(token)

    def test_login(self, client):
        client.login(TEST_EMAIL, TEST_PW)

    def test_fail_login_pw(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 401: .*Incorrect.*"
        ):
            client.login(TEST_EMAIL, "Incorrect Password")

    def test_fail_login_email(self, client):
        email = next(self.emailgen)
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 401: .*Incorrect.*"
        ):
            client.login(email, TEST_PW)

    def test_fail_register_empty(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 400: .*Malformed.*"
        ):
            client._request("POST", "/user/register", {}, noauth=True)

    def test_fail_verify_notgiven(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 400: .*Token.*"
        ):
            client._request("GET", "/user/verify", noauth=True)

    def test_fail_verify_empty(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 400: .*Token.*"
        ):
            client.register_verify("")

    def test_fail_login_empty(self, client):
        with pytest.raises(
                MemoHTTPError,
                match=r"Status 400: .*Malformed.*"
        ):
            client._request("POST", "/user/login", {}, noauth=True)
