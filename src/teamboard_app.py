import sys
import yaml
from flask import Flask
import os

from teamboard import get_env
from teamboard.achievements import ach_app
from teamboard.static import initialize_static
from teamboard.github import pr_app
from teamboard.index import root_app

app = Flask("The Teamboard", template_folder='templates', static_folder='static')

app.config['GITHUB_TOKEN'] = get_env("GITHUB_TOKEN", "")

initialize_static(app)
app.register_blueprint(root_app, url_prefix='/')
app.register_blueprint(pr_app, url_prefix='/pr')
app.register_blueprint(ach_app, url_prefix='/achievements')

if __name__ == '__main__':
    settings_file = "default_settings.yml"

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        settings_file = sys.argv[1]

    with open(settings_file, 'r') as stream:
        settings = yaml.load(stream)

    app.config['TEAMBOARD_SETTINGS'] = settings

    app.run(debug=False)
