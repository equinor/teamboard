import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

import datetime
from agithub.GitHub import GitHub
from flask.templating import render_template

from teamboard import teamboard_logger, pretty_date_since
from flask import Blueprint
from flask import current_app

pr_app = Blueprint("pr_app", __name__)


def check_rate_limits(self):
    status, rate_limit = self.rate_limit.get()
    if status == 200:
        limit = rate_limit['resources']['core']['limit']
        remaining = rate_limit['resources']['core']['remaining']
        reset = rate_limit['resources']['core']['reset']
        reset = datetime.datetime.fromtimestamp(reset)
        teamboard_logger().info("Rate limit %s/%s reset at %s" % (remaining, limit, reset))
        return "Rate limit %s/%s reset at %s" % (remaining, limit, reset)
    else:
        teamboard_logger().debug("Unable to check rate limits: %s - %s" % (status, self.getheaders()))
        return "Failed to check rate limits!"


def get_ci_status(self, owner, repo, pr):
    sha = pr['head']['sha']
    status, pr_status = self.repos[owner][repo].commits[sha].status.get()

    if status != 200:
        teamboard_logger().warning("Unable to find status for PR #%s in repo: %s/%s" % (pr['number'], owner, repo))
        teamboard_logger().debug("Response status: %s - %s" % (status, self.getheaders()))

    return pr_status


def get_review_status(self, owner, repo, pr):
    number = pr['number']
    status, review_status = self.repos[owner][repo].pulls[number].reviews.get()

    if status != 200:
        teamboard_logger().warning("Unable to find review status for PR #%s in repo: %s/%s" % (number, owner, repo))
        teamboard_logger().debug("Response status: %s - %s" % (status, self.getheaders()))

    return review_status


def get_pr_comments(self, owner, repo, pr):
    number = pr['number']
    status, pr_comments = self.repos[owner][repo].issues[number].comments.get()

    if status != 200:
        teamboard_logger().warning("Unable to find comments for PR #%s in repo: %s/%s" % (number, owner, repo))
        teamboard_logger().debug("Response status: %s - %s" % (status, self.getheaders()))

    return pr_comments


def get_pulls(self, owner, repo):
    status, pulls = self.repos[owner][repo].pulls.get()

    result = []

    if status != 200:
        if status == 403:
            teamboard_logger().warning("Unable to access %s/%s - Rate limited or missing token?" % (owner, repo))
            check_rate_limits(self)
        elif status == 404:
            teamboard_logger().warning("Unable to find repository with name: %s/%s" % (owner, repo))
        else:
            teamboard_logger().debug("PR fetch status: %s - %s" % (status, self.getheaders()))
    else:
        for pr in pulls:
            pr_status = get_ci_status(self, owner, repo, pr)
            review_status = get_review_status(self, owner, repo, pr)
            pr_comments = get_pr_comments(self, owner, repo, pr)

            result.append({
                'repo': pr['base']['repo']['full_name'],
                'title': pr['title'],
                'number': pr['number'],
                'updated': pr['updated_at'],
                'user': pr['user']['login'],
                'avatar': pr['user']['avatar_url'],
                'review_status': review_status,
                'pr_comments': pr_comments,
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


def emoji_for_review_status(review_status, pr_comments):
    if len(review_status) == 0 and len(pr_comments) == 0:
        return ""

    APPROVED = '&#x1f44d;'  # Thumbs up
    COMMENTED = '&#x1f4ac;'  # Talk bubble
    DISMISSED = '&#x1f44e;'  # Thumbs down
    PENDING = '&#1f40c;'  # Snail

    state = None

    if len(pr_comments) > 0:
        state = COMMENTED

    for review in review_status:
        if review['state'] == 'COMMENTED':
            if state is None:
                state = COMMENTED
        elif review['state'] == 'APPROVED':
            state = APPROVED
        elif review['state'] == 'PENDING':
            state = PENDING
        elif review['state'] == 'DISMISSED':
            state = DISMISSED
        else:
            teamboard_logger().info("Unknown review state: %s" % review['state'])

    return state if state is not None else ''


@pr_app.route("/<path:repos>")
def get_pull_requests(repos):
    """
    :type repos: string
    """
    token = current_app.config.get('GITHUB_TOKEN')

    g = GitHub(token=token)

    pull_requests = []
    with ThreadPoolExecutor(max_workers=10) as tpe:
        futures = []
        for repo_name in repos.split(","):
            owner, repo = repo_name.split('/')
            futures.append(tpe.submit(get_pulls, g, owner, repo))

        for future in concurrent.futures.as_completed(futures):
            pulls = future.result()
            pull_requests.extend(pulls)

    pull_requests = sorted(pull_requests, key=lambda pr: pr['updated'], reverse=True)

    rendered_pr = ""

    for pr in pull_requests:
        rt = render_template('pr.html', pr=pr, project=project,
                             projectColor=project_color, prettyTime=pretty_date_since,
                             reviewState=emoji_for_review_status)
        rendered_pr += rt

    return rendered_pr


@pr_app.route("/rate_limits")
def get_rates():
    token = current_app.config.get('GITHUB_TOKEN')
    g = GitHub(token=token)
    return check_rate_limits(g)


def pulls(project_list):
    project_list = project_list.split(",")
    settings = current_app.config.get('TEAMBOARD_SETTINGS')

    repos = []
    projects = settings['projects']
    for project in [p for p in projects if p in project_list]:
        repos.extend(projects[project]['repos'])

    return repos


@pr_app.route("/")
def index():
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    pr_columns = settings['pr_columns']
    return render_template('github.html', pulls=pulls, pr_columns=pr_columns)