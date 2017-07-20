from flask import Blueprint, render_template
from flask import current_app

root_app = Blueprint("root_app", __name__)


@root_app.route("/")
def index():
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    return render_template('index.html')
