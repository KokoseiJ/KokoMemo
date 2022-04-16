import os
import sys
import json
import requests
import traceback

TEST_URL = "http://127.0.0.1:5000"

TEST_NAME = "TestUser001"
TEST_EMAIL = "testuser@testemail.com"
TEST_PW = "I_am_testuser"


def merge_route(baseurl, route):
    baseurl = baseurl.rstrip("/")
    route = route.lstrip("/")

    return f"{baseurl}/{route}"


class TestAssertionError(Exception):
    def __init__(self, type_, var1, var2):
        self.var1 = var1
        self.var2 = var2
        txtlist = [
            f"Assert{type_} failed!",
            f"var1: {var1}",
            f"var2: {var2}"
        ]
        self.args = ("\n".join(txtlist),)


class TestAssertionExceptionError(Exception):
    def __init__(self, func, exc, rtn):
        self.func = func
        self.exc = exc
        self.return_value = rtn
        txtlist = [
            f"AssertionException for {func.__name__} failed!"
            f"Raised Exception: {exc.__name__}" if exc
            else f"Returned value: {rtn}"
        ]
        self.args = ("\n".join(txtlist),)


class MemoHTTPError(Exception):
    def __init__(self, status, code, message):
        self.args = (f"Status {status}: {code} {message}")
        self.status = status
        self.code = code
        self.message = message


class TestManager:
    def __init__(self):
        self.tests = []

    def register(self, func):
        self.tests.append(func)
        return func

    def assertEquals(self, val1, val2):
        if val1 == val2:
            return None
        else:
            raise TestAssertionError("Equals", val1, val2)

    def assertNotEquals(self, val1, val2):
        if val1 != val2:
            return None
        else:
            raise TestAssertionError("NotEquals", val1, val2)

    def assertRaises(self, func, *excs):
        try:
            rtnval = func()
        except Exception as e:
            if e.__class__ not in excs:
                raise TestAssertionExceptionError(func, e, None)

            return e

        raise TestAssertionExceptionError(func, None, rtnval)

    def run(self):
        exceptions = {}

        print("="*10 + " Test Started " + "="*10, end="\n\n")

        for func in self.tests:
            print(f"\t{func.__name__}\t| ", end="")
            sys.stdout.flush()

            result = self._run(func)

            if result is None:
                print("PASS")
            else:
                exceptions.update({func: result})
                print("FAIL")

        print("\n" + "="*11 + " Test Ended " + "="*11, end="\n\n")

        print("Errors:\n")

        if exceptions:
            for func, exc in exceptions.items():
                excstrlist = traceback.format_exception(exc)
                argsstr = excstrlist.pop(-1)
                argslist = [f"{x}\n" for x in argsstr.split(os.linesep)]
                excstrlist.extend(argslist)
                excstr = "\n".join(f"\t\t{x}" for x in excstrlist)

                print(f"\t{func.__name__}:")
                print("\n".join(excstr) + "\n")
        else:
            print("\t There were no errors this time. Woohoo!")

    def _run(self, func):
        try:
            func()
            return None
        except Exception as e:
            return e


class TestMemoClient:
    def __init__(self, url=TEST_URL):
        self.url = url

        self.session = requests.session()
        self.session.headers.update({"User-Agent": "TestMemoClient"})

        self.token = None

    # ===== User =====

    def register(self, email, pw, name):
        data = {
            "email": email,
            "password": pw,
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
            "password": pw
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

        headers = kwargs.get("headers", dict())

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

        request_kwargs.update(headers)
        request_kwargs.update(kwargs)

        r = self.session.request(**request_kwargs)

        if r.status_code // 100 != 2:
            error = r.json()['meta']
            code = error['code']
            message = error['message']

            raise MemoHTTPError(r.status_code, code, message)

        return r.json()


test_manager = TestManager()
