from flask import Blueprint, render_template
from flask import current_app

root_app = Blueprint("root_app", __name__)


def pulls():
    settings = current_app.config.get('TEAMBOARD_SETTINGS')

    repos = []
    projects = settings['projects']
    for prj in projects:
        repos.extend(projects[prj]['repos'])

    return repos


@root_app.route("/")
def index():
    return render_template('index.html', pulls=pulls)
