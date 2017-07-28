from flask import Blueprint, render_template
from flask import current_app

from teamboard import teamboard_logger
from teamboard.services.jira import Jira

team_app = Blueprint("team_app", __name__)


def fetch_team_member(jira, name):
    status, data = jira.user.get(username=name)

    if status != 200:
        teamboard_logger().warning("Unable to get member info for %s" % name)
        teamboard_logger().debug("Response status: %s - %s" % (status, jira.getheaders()))
        teamboard_logger().debug("-------------->: %s" % data)
        return None

    return {
        'full_name': data['displayName'],
        'name': data['name'],
        'avatar': data['avatarUrls']['48x48']
    }


@team_app.route("/")
def get_team():
    team_names = current_app.config.get('TEAMBOARD_SETTINGS')['team']

    url = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['url']
    token = current_app.config.get('TEAMBOARD_SETTINGS')['tokens']['jira_token']

    jira = Jira(url=url, basic_token=token)

    members = [fetch_team_member(jira, name) for name in team_names]
    team = [member for member in members if member is not None]

    return render_template('team.html', team=team)
