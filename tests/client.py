import json
import hashlib
import requests


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
    def __init__(self, url):
        self.baseurl = url

        self.session = requests.session()
        self.session.headers.update({"User-Agent": "TestMemoClient"})

        self.token = None

    # ===== User =====

    def register(self, email, pw, name):
        data = {
            "email": email,
            "password": hashlib.sha256(pw.encode()).hexdigest(),
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
            "password": hashlib.sha256(pw.encode()).hexdigest()
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
