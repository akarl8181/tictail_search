# -*- coding: utf-8 -*-

import os
from flask import Flask
from server.api import api
from flask_cors import CORS


def create_app(settings_overrides=None):
    app = Flask(__name__)
    CORS(app)
    configure_settings(app, settings_overrides)
    configure_blueprints(app)

    return app


def configure_settings(app, settings_overrides):
    parent = os.path.dirname(__file__)
    data_path = os.path.join(parent, '..', 'data')
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'DATA_PATH': data_path,
    })

    if settings_overrides:
        app.config.update(settings_overrides)


def configure_blueprints(app):
    app.register_blueprint(api)
