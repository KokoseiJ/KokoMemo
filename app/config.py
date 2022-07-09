import os.path

basepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
instance_path = os.path.join(basepath, "instance")


class Config(object):
    SQLALCHEMY_DATABASE_URI = f"sqlite://{instance_path}/data.db"
    VERIFY_EXPIRY_TIME = 30 * 60
    AUTH_EXPIRY_TIME = 3 * 60 * 60
    RENEW_EXPIRY_TIME = 7 * 24 * 60 * 60


class ProdConfig(Config):
    pass


class DebugConfig(Config):
    pass
