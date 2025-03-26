from flask import Flask
from dash import Dash, html, dcc

from .routes.home_route import home_bp


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='dev')
    app.register_blueprint(home_bp)
    return app
