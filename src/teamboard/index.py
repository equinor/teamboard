from flask import Blueprint, render_template
from flask import current_app

root_app = Blueprint("root_app", __name__)


def pulls(project_list):
    project_list = project_list.split(",")
    settings = current_app.config.get('TEAMBOARD_SETTINGS')

    repos = []
    projects = settings['projects']
    for project in [p for p in projects if p in project_list]:
        repos.extend(projects[project]['repos'])

    return repos


@root_app.route("/")
def index():
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    pr_columns = settings['pr_columns']
    return render_template('index.html', pulls=pulls, pr_columns=pr_columns)
