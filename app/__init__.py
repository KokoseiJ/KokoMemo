from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile('config.py')

    if test_config is None:
        app.config.from_mapping(test_config)

    from . import views
    for viewname in views.__all__:
        view = getattr(views, viewname)
        bp = getattr(view, "bp")
        app.register_blueprint(bp)

    db.init_app(app)
    migrate.init_app(app)

    return app
