from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env()

    if os.path.exists(app.instance_path):
        if os.path.isfile(app.instance_path):
            raise TypeError(f"{app.instance_path} should be a dir.")
    else:
        os.mkdir(app.instance_path)

    if app.config['DEBUG']:
        app.config.from_object("app.config.DebugConfig")
    else:
        app.config.from_object("app.config.ProdConfig")

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

    return app
