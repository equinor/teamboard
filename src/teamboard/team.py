from flask import Blueprint, render_template, abort
from flask import current_app

from teamboard import teamboard_logger as logger
from teamboard.services.slack import Slack

team_app = Blueprint("team_app", __name__)


def handle_status(handler, status, data, message='REST call failed!'):
    if status != 200:
        logger().warning(message)
        dbg_msg = "Response status: %s - %s" % (status, handler.getheaders())
        logger().debug(dbg_msg)
        logger().debug("[data]: %s" % data)
        abort(status)


@team_app.route("/")
def get_team():
    config = current_app.config.get('TEAMBOARD_SETTINGS')
    team = config['team']
    usernames = {member['slack']: member for member in team}

    token = config['tokens']['slack_token']
    slack = Slack(token)
    status, users = slack['users.list'].get()

    handle_status(slack, status, users, 'Unable to fetch users list')

    if users['ok']:
        members = [usr for usr in users['members'] if usr['name'] in usernames]

        for member in members:
            slack_name = member['name']
            member['full_name'] = usernames[slack_name]['name']
            member['avatar'] = member['profile']['image_72']

    return render_template('team.html', team=members)
