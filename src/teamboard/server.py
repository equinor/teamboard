from flask import Flask
from teamboard import get_env
from teamboard.static import initialize_static
from teamboard.github import pr_app
from teamboard.index import root_app

TEMPLATE_FOLDER = get_env("TEMPLATE_FOLDER", "templates")
STATIC_FOLDER = get_env("STATIC_FOLDER", "static")

app = Flask("The Teamboard", template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

app.config['GITHUB_TOKEN'] = get_env("GITHUB_TOKEN", "")

app.config['TEAMBOARD_SETTINGS'] = {
    'projects': {
        'ERT': {
            'color': "#d33682",
            'repos': ['Statoil/libres', 'Statoil/libecl', 'Statoil/ert', 'Statoil/carolina']
        },
        'RES': {
            'color': "#eac117",
            'repos': ['Statoil/segyio', 'Statoil/segyviewer', 'Statoil/sunbeam']
        },
        'OPM': {
            'color': "#268bd2",
            'repos': ['OPM/opm-parser', 'OPM/opm-output']
        },
        'BYO': {
            'color': "#859900",
            'repos': ['Statoil/teamboard', 'Statoil/pycmake']
        }
    },
    'default_project_color': '#93a1a1'
}

initialize_static(app)
app.register_blueprint(root_app, url_prefix='/')
app.register_blueprint(pr_app, url_prefix='/pr')

if __name__ == '__main__':
    app.run(debug=False)
