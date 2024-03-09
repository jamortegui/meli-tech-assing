import os

from flask import Flask

from . import files
from . import db
from . import settings


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=settings.DATABASE,
        UPLOAD_FOLDER=settings.UPLOAD_FOLDER,
        INIT_SCHEMA=settings.INIT_SCHEMA,
    )

    if test_config is not None:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    app.register_blueprint(files.bp)

    return app
