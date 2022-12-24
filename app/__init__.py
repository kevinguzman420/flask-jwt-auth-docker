from flask import Flask
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_mail import Mail

import logging

from app.db import db
from app.ext import ma, migrate

bcrypt = Bcrypt()
mail = Mail()

def create_app(settings_module):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(settings_module)

    if app.config.get("TESTING", False):
        app.config.from_pyfile("config-testing.py", silent=True)
    else:
        app.config.from_pyfile("config.py", silent=True)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    mail.init_app(app)

    Api(app, catch_all_404s=True)
    app.url_map.strict_slashes = False

    from app.auth.api_v1_0 import auth_bp
    app.register_blueprint(auth_bp)
    configure_logging(app)

    return app


def configure_logging(app):
    # Eliminamos los posibles manejadores, si existen, del logger por defecto
    del app.logger.handlers[:]

    # Añadimos el logger por defecto a la lista de loggers
    loggers = [
        app.logger,
    ]

    # Creamos un manejador para escribir los mensajes por consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(verbose_formatter())

    for log in loggers:
        log.propagate = False
        log.setLevel(logging.DEBUG)

def verbose_formatter():
    return logging.Formatter(
        "[%(asctime)s.%(msecs)d]\t %(levelname)s \t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )