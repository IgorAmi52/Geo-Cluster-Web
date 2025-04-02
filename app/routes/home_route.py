from flask import Blueprint, render_template, current_app
from app.controllers import PubmedDSController
from app.services import PlotFactory
from app.config import PLOT_MODE
from app.services import ClusteringService

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    dash_app = current_app.extensions['dash']['dash_app']
    pub_controller = PubmedDSController()
    clustering_service = ClusteringService(6)
    plot_factory = PlotFactory(
        mode=PLOT_MODE.SCATTER, clustering_service=clustering_service)
    small_vectors = pub_controller.dimension_reduction()

    plot = plot_factory.create_plot(
        small_vectors, pub_controller.get_ds_names(), clustering=True)
    dash_app.layout.children[0].figure = plot
    return render_template('index.html', dash_url='/dash/')
