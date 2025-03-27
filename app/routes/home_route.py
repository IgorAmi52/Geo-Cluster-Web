from flask import Blueprint, render_template, current_app
from app.controllers import PubmedDSController

home_bp = Blueprint('home', __name__)


@home_bp.route('/')
def home():
    pubController = PubmedDSController()
    ds_data = pubController.get_ds_data()
    return render_template('index.html', dash_url='/dash/')
