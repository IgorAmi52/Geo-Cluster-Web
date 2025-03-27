from flask import Flask
from dash import Dash, html, dcc
from .routes.home_route import home_bp
from app.controllers import PubmedDSController


def create_app():
    app = Flask(__name__)
    pubController = PubmedDSController()
    pubController.set_ds_data_dict()
    app.config.from_mapping(SECRET_KEY='dev')
    app.register_blueprint(home_bp)
    return app
