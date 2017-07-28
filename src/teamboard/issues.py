from flask import Blueprint, render_template
from flask import current_app

from teamboard import teamboard_logger
from teamboard.services.jira import Jira

issues_app = Blueprint("issues_app", __name__)


def search_for_issues(jira, jql, **kwargs):
    status, data = jira.search.get(jql=jql, **kwargs)

    if status != 200:
        teamboard_logger().warning("Unable to get issues for query %s" % jql)
        teamboard_logger().debug("Response status: %s - %s" % (status, jira.getheaders()))
        teamboard_logger().debug("-------------->: %s" % data)
        return []

    return data['issues']


def project_color(project_name):
    projects = current_app.config.get('TEAMBOARD_SETTINGS')['projects']
    for project in projects:
        if project_name.lower() == project.lower():
            return projects[project]['color']

    return current_app.config.get('TEAMBOARD_SETTINGS')['default_project_color']


def process_issue(issue, project_field, value_node):
    result = {
        'key': issue['key'],
        'summary': issue['fields']['summary'],
        'assignee_name': '',
        'assignee_full_name': '',
        'assignee_avatar': '',
        'project': issue['fields'][project_field][value_node],
        'flagged': issue['fields']['customfield_10200'] is not None
    }

    result['color'] = project_color(result['project'])

    if issue['fields']['assignee'] is not None:
        result['assignee_name'] = issue['fields']['assignee']['name']
        result['assignee_full_name'] = issue['fields']['assignee']['displayName']
        result['assignee_avatar'] = issue['fields']['assignee']['avatarUrls']['48x48']

    return result


def fetch_issues(status):
    url = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['url']
    token = current_app.config.get('TEAMBOARD_SETTINGS')['tokens']['jira_token']
    project = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['project']
    project_field = current_app.config.get('TEAMBOARD_SETTINGS')['issue_tracker']['project_field']

    field, value_node = project_field.split("/")

    jql = 'status in ("%s") and project in (%s)' % (status, project)
    fields = 'summary,assignee,customfield_10200,%s' % field

    jira = Jira(url=url, basic_token=token)

    issues = search_for_issues(jira, jql=jql, fields=fields)

    return [process_issue(issue, field, value_node) for issue in issues]


@issues_app.route("/todo")
def fetch_todo():
    issues = fetch_issues('to do')
    return render_template('mini_issues.html', issues=issues, show_avatar=False)


@issues_app.route("/in_progress")
def fetch_in_progress():
    issues = fetch_issues('in progress')
    return render_template('issues.html', issues=issues)


@issues_app.route("/ready_for_review")
def fetch_ready_for_review():
    issues = fetch_issues('ready for review')
    return render_template('issues.html', issues=issues)


@issues_app.route("/in_review")
def fetch_in_review():
    issues = fetch_issues('in review')
    return render_template('issues.html', issues=issues)


@issues_app.route("/external_test")
def fetch_external_test():
    issues = fetch_issues('external test')
    return render_template('mini_issues.html', issues=issues, show_avatar=True)