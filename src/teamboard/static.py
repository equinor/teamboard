import os
from flask import send_from_directory


def initialize_static(app):
    css_root = os.path.join(app.static_folder, 'styles')
    img_root = os.path.join(app.static_folder, 'img')
    libs_root = os.path.join(app.static_folder, 'libs')

    @app.route('/css/<path:path>')
    def send_css(path):
        return send_from_directory(css_root, path)

    @app.route('/img/<path:path>')
    def send_img(path):
        return send_from_directory(img_root, path)

    @app.route('/js/<path:path>')
    def send_js(path):
        return send_from_directory(libs_root, path)

    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico')
