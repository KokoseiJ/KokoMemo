from flask import Flask


def create_app():
    app = Flask(__name__)
    print(__file__)

    from memoapp import views
    
    app.register_blueprint(views.bp)

    return app
