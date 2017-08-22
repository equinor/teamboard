import re
from http.client import HTTPConnection

import time

import sys
from flask import Blueprint, render_template
from flask import current_app

from teamboard import teamboard_logger

root_app = Blueprint("root_app", __name__)

_timestamp = time.time()
teamboard_logger().info("Timestamp set to: %s" % _timestamp)


@root_app.route("/")
def index():
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    return render_template('index.html', ci=settings['ci'])


@root_app.route("/shutdown")
def shutdown():
    teamboard_logger().warning("Shutting down!")
    sys.exit(0)


@root_app.route("/excuse")
def fetch_excuse():
    conn = HTTPConnection("developerexcuses.com")
    conn.request("GET", "/")

    response = conn.getresponse()

    status = response.status
    if status != 200:
        teamboard_logger().warning("Unable to fetch excuse!")
        teamboard_logger().debug("Response status: %s - %s" % (status, response.getheaders()))
        teamboard_logger().debug("-------------->: %s" % response.read())
        return ""

    regex = re.compile("<a(.+?)>(.+?)</a>")
    match = regex.search(str(response.read()))

    if match:
        return match.group(2).replace("\\", "")

    return ""


@root_app.route("/timestamp")
def timestamp():
    return str(_timestamp)
