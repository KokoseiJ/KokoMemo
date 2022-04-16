import pytest

from client import MemoHTTPError
from conftest import TEST_EMAIL, TEST_PW, TEST_NAME


def email_enum():
    i = 1
    while True:
        yield f"nonexistent{i}@testemail.com"


emailgen = email_enum()


class TestUser:
    def test_register(self, client):
        email = next(emailgen)
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
        email = next(emailgen)
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
        email = next(emailgen)
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
