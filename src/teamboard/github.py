from agithub.GitHub import GitHub
from flask.templating import render_template

from teamboard import teamboard_logger, pretty_date_since
from flask import Blueprint
from flask import current_app

pr_app = Blueprint("pr_app", __name__)


def get_status(self, owner, repo, pr):
    sha = pr['head']['sha']
    status, pr_status = self.repos[owner][repo].commits[sha].statuses.get()

    if status != 200:
        teamboard_logger().warning("Unable to find status for PR #%s in repo: %s/%s" % (pr['number'], owner, repo))
        teamboard_logger().debug("Status: %s - %s" % (status, self.getheaders()))

    return pr_status[0]


def get_pulls(self, owner, repo):
    status, pulls = self.repos[owner][repo].pulls.get()

    result = []

    if status != 200:
        teamboard_logger().warning("Unable to find repository with name: %s/%s" % (owner, repo))
        teamboard_logger().debug("Status: %s - %s" % (status, self.getheaders()))
    else:
        for pr in pulls:
            pr_status = get_status(self, owner, repo, pr)

            result.append({
                'repo': pr['base']['repo']['full_name'],
                'title': pr['title'],
                'number': pr['number'],
                'updated': pr['updated_at'],
                'user': pr['user']['login'],
                'avatar': pr['user']['avatar_url'],
                'status': pr_status['state']
            })
    return result


def project(repo):
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    for prj, repos in settings['projects'].items():
        if repo in repos['repos']:
            return prj

    teamboard_logger().info("Unable to find project for repo '%s'" % repo)
    teamboard_logger().debug("Using default project for '%s'" % repo)

    return "???"


def project_color(project):
    settings = current_app.config.get('TEAMBOARD_SETTINGS')

    try:
        return settings['projects'][project]['color']
    except KeyError:
        teamboard_logger().info("Unable to find project color for '%s'" % project)
        teamboard_logger().debug("Using default project color for '%s'" % project)
        return settings['default_project_color']


@pr_app.route("/<path:repos>")
def get_pull_requests(repos):
    """
    :type repos: string
    """
    token = current_app.config.get('GITHUB_TOKEN')

    g = GitHub(token=token)

    pull_requests = []
    for repo_name in repos.split(","):
        owner, repo = repo_name.split('/')
        pulls = get_pulls(g, owner, repo)
        pull_requests.extend(pulls)

    pull_requests = sorted(pull_requests, key=lambda pr: pr['updated'], reverse=True)

    rendered_pr = ""

    for pr in pull_requests:
        rt = render_template('pr.html', pr=pr, project=project, projectColor=project_color, prettyTime=pretty_date_since)
        rendered_pr += rt

    return rendered_pr
