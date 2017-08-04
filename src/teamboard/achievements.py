from flask import Blueprint, render_template
from flask import current_app

from teamboard import teamboard_logger
from teamboard.services.jira import Jira

ach_app = Blueprint('achievements_app', __name__)


def calculate_achievement(jira, project, achievement_setting):
    achievement = dict(achievement_setting)

    date = achievement_setting['since']
    jql = 'status = done and project in (%s) and resolutionDate >= %s' % (project, date)
    status, result = jira.search.get(jql=jql, fields='key')

    if status != 200:
        teamboard_logger().warning('Unable to get achievement count for %s' % achievement_setting['name'])
        teamboard_logger().debug('Response status: %s - %s' % (status, jira.getheaders()))
        teamboard_logger().debug('-------------->: %s' % result)
        count = 0
    else:
        count = int(result['total'])

    achievement['progress'] = count
    achievement['progress_percent'] = min(100.0, 100.0 * achievement['progress'] / achievement['count'])
    achievement['style'] = 'green-blink' if achievement['progress_percent'] >= 100.0 else ''

    return achievement


@ach_app.route('/')
def get_achievements():
    achievement_settings = current_app.config.get('TEAMBOARD_SETTINGS')['achievements']

    url = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['url']
    token = current_app.config.get('TEAMBOARD_SETTINGS')['tokens']['jira_token']

    jira = Jira(url=url, basic_token=token)

    project = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['project']

    achievements = [calculate_achievement(jira, project, achievement) for achievement in achievement_settings]

    return render_template('achievements.html', achievements=achievements)
