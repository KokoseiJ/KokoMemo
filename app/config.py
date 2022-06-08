class Config(object):
    SQLALCHEMY_DATABASE_URI = ""
    VERIFY_EXPIRY_TIME = 30 * 60
    AUTH_EXPIRY_TIME = 3 * 60 * 60
    RENEW_EXPIRY_TIME = 7 * 24 * 60 * 60


class ProdConfig(Config):
    pass


class DebugConfig(Config):
    pass
