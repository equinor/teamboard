import ssl
import sys

import yaml

import os

from teamboard import bundle_certificates, initialize_logger, DEBUG, INFO

initialize_logger(level=INFO)


def _create_https_context(**kwargs):
    cert_pem = 'certificates/bundle.pem'
    if not os.path.exists(cert_pem):
        bundle_certificates(name='bundle')

    context = ssl.create_default_context(**kwargs)
    context.load_verify_locations(cafile=cert_pem)
    return context


ssl._create_default_https_context = _create_https_context

from flask import Flask

from teamboard.achievements import ach_app
from teamboard.ci import ci_app
from teamboard.static import initialize_static
from teamboard.github import pr_app
from teamboard.index import root_app
from teamboard.team import team_app
from teamboard.issues import issues_app

app = Flask("The Teamboard", template_folder='templates', static_folder='static')


@app.template_filter('idify')
def idify(name):
    return name.replace(" ", "_")


initialize_static(app)
app.register_blueprint(root_app)
app.register_blueprint(pr_app, url_prefix='/pr')
app.register_blueprint(ach_app, url_prefix='/achievements')
app.register_blueprint(ci_app, url_prefix='/ci')
app.register_blueprint(team_app, url_prefix='/team')
app.register_blueprint(issues_app, url_prefix='/issues')

if __name__ == '__main__':
    settings_file = "default_settings.yml"

    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        settings_file = sys.argv[1]

    with open(settings_file, 'r') as stream:
        settings = yaml.load(stream)

    app.config['TEAMBOARD_SETTINGS'] = settings

    app.run(debug=False, threaded=True)
