import json
import hashlib


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
    def __init__(self, testclient, version="v1"):
        self.testclient = testclient
        self.baseurl = f"/api/{version}"

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

        token = self._request("POST", "/user/login", data, noauth=True)['data']
        self.token = token

        return token

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
            value = locals().get(key)
            if value is not None:
                data.update({key.strip("_"): value})

        return self._request("PUT", f"/memo/{id_}", data)['data']

    def delete_memo(self, id_):
        return self._request("DELETE", f"/memo/{id_}")['data']

    def update_memo(self, data):
        return self._request("POST", "/memo/update", data)['data']

    # ===== End =====

    def _request(self, method, route, data=None, noauth=False, **kwargs):
        url = merge_route(self.baseurl, route)

        request_kwargs = {
            "method": method,
            "path": url
        }

        headers = {}

        if not noauth and self.token is not None:
            headers.update({"Authorization": f"Bearer {self.token}"})
            request_kwargs.update({"headers": headers})

        if data is not None:
            if isinstance(data, dict):
                data = json.dumps(data).encode()
                request_kwargs.update({"content_type": "application/json"})
            
            request_kwargs.update({"data": data})

        request_kwargs.update(kwargs)

        r = self.testclient.open(**request_kwargs)

        if r.status_code // 100 != 2:
            error = r.json['meta']
            message = error['message']

            raise MemoHTTPError(r.status_code, message)

        return r.json
