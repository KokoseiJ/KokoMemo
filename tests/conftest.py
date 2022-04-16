import pytest

from app import create_app

from client import MemoClient

TEST_URL = "http://127.0.0.1:5000"

TEST_NAME = "TestUser001"
TEST_EMAIL = "testuser@testemail.com"
TEST_PW = "I_am_testuser"


@pytest.fixture
def client():
    client = MemoClient(TEST_URL)
    client.token = client.login(TEST_EMAIL, TEST_PW)
    return client
