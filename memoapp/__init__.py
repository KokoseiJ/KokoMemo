from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import os
from importlib import import_module

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    dbpath = os.path.join(app.instance_path, "app.db")

    if not os.path.exists(app.instance_path):
        os.mkdir(app.instance_path)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{dbpath}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    import_module("memoapp.models")
    db.init_app(app)
    migrate.init_app(app, db)

    from memoapp import views
    app.register_blueprint(views.bp)

    return app
