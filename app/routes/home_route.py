from flask import Blueprint, render_template, current_app
from app.controllers import PubmedDSController
from app.services import PlotFactory
from app.config import PLOT_MODE
from app.dash import register_callbacks
from app.services import ClusteringService

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    dash_app = current_app.extensions['dash']['dash_app']
    pubController = PubmedDSController()
    clustering_service = ClusteringService(6)
    plot_factory = PlotFactory(
        mode=PLOT_MODE.SCATTER, clustering_service=clustering_service)
    small_vectors = pubController.dimension_reduction()

    plot = plot_factory.create_plot(
        small_vectors, pubController.get_ds_names(), clustering=True)
    dash_app.layout.children[0].figure = plot
    register_callbacks(dash_app, plot_factory)
    return render_template('index.html', dash_url='/dash/')
