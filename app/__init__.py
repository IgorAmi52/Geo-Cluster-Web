from flask import Flask
from dash import Dash, html, dcc

from app.dash.callbacks import register_callbacks
from app.services import PaperApiService
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
            # Graph component
            dcc.Graph(
                id='plot',
                figure={}
            ),

            # Modal component (initially hidden)
            html.Div(
                id='modal-container',
                className='modal-hidden',
                children=[
                    html.Div(
                        id='modal-content',
                        children=[
                            # Close button
                            html.Span(
                                '×',
                                id='close-modal',
                                className='modal-close'
                            ),

                            html.Div(
                                className='modal-body',
                                children=[
                                    html.H3(
                                        id='modal-title',
                                        className='modal-title'
                                    ),
                                    html.Div(
                                        id='modal-organism',
                                        className='modal-organism'
                                    ),
                                    html.Div(
                                        id='modal-references',
                                        className='modal-references',
                                        children=[]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
        ]
    )
    app.extensions['dash'] = {'dash_app': dash_app}
    register_callbacks(dash_app, pubController, PaperApiService(ApiService(
        API_CONFIG.BASE_API, API_CONFIG.API_KEY)))
    app.config.from_mapping(SECRET_KEY='dev')
    app.register_blueprint(home_bp)
    return app
