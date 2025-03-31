from flask import Flask
from dash import Dash, html, dcc
from .routes.home_route import home_bp
from app.services import ApiService, DatasetApiService, TfIdfService
from app.controllers import PubmedDSController
from app.config import API_CONFIG, PMIDs_CONFIG


def create_app():
    app = Flask(__name__)
    api_service = DatasetApiService(ApiService(
        API_CONFIG.BASE_API, API_CONFIG.API_KEY))
    tf_idf_service = TfIdfService()
    # Initialize PubmedDSController with services
    pubController = PubmedDSController(api_service, tf_idf_service)
    pubController.compute_ds_vectors()
    dash_app = Dash(
        __name__,
        server=app,
        url_base_pathname='/dash/',
        assets_folder=app.static_folder
    )
    dash_app.layout = html.Div(
        id='dashboard-container',
        children=[
            dcc.Graph(id='plot', figure={}),
        ]
    )

    app.extensions['dash'] = {'dash_app': dash_app}
    app.config.from_mapping(SECRET_KEY='dev')
    app.register_blueprint(home_bp)
    return app
