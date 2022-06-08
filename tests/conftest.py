import pytest

from client import MemoClient

from app import create_app
from app.config import Config


TEST_NAME = "TestUser001"
TEST_EMAIL = "testuser@testemail.com"
TEST_PW = "I_am_testuser"
TEST_SECRETKEY = b"testing_key"

TEST_VER = "v1"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URL = 'SQLITE:///:memory:'
    SECRET_KEY = TEST_SECRETKEY


def test_prepare(app):
    pass


@pytest.fixture
def app():
    app = create_app()
    app.config.from_object(TestingConfig)

    test_prepare(app)

    yield app


@pytest.fixture
def client(app):
    client = MemoClient(app.test_client(), f"/api/{TEST_VER}")
    return client
