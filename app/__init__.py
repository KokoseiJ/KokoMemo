from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from .config import test_setup

import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env()

    if app.config['DEBUG']:
        app.config.from_object("config.DebugConfig")
    else:
        app.config.from_object("config.ProdConfig")

    if app.config['TESTING']:
        app.config.from_object("config.TestConfig")

    inst_config_path = os.path.join(app.instance_path, "config.py")

    if os.path.exists(inst_config_path):
        app.config.from_pyfile(inst_config_path)

    from . import views
    for viewname in views.__all__:
        view = getattr(views, viewname)
        bp = getattr(view, "bp")
        app.register_blueprint(bp)

    db.init_app(app)
    migrate.init_app(app)

    if app.config['TESTING']:
        test_setup()

    return app
