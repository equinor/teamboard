from flask import Blueprint, render_template, abort
from flask import current_app

from teamboard import teamboard_logger
from teamboard.services.jenkins import Jenkins
from teamboard.services.travis import Travis

ci_app = Blueprint("ci_app", __name__)

SUCCESS = "success"
FAILED = "failed"
IN_PROGRESS = "in-progress"
UNKNOWN = "unknown"


def convert_status_to_style(status):
    status_style = "ci-status-unknown"

    if status == "success":
        status_style = "ci-status-ok"
    elif status == "in-progress":
        status_style = "ci-status-working ci-yellow-blink"
    elif status == "failed":
        status_style = "ci-status-fail ci-red-blink"

    return status_style


def get_travis_job_status(self, project, branch):
    slug = project['slug']
    status, slug_data = self.repos[slug].branches[branch].get()

    if status != 200:
        teamboard_logger().warning("Unable to get CI status for master branch on %s" % slug)
        teamboard_logger().debug("Response status: %s - %s" % (status, self.getheaders()))
        teamboard_logger().debug("-------------->: %s" % slug_data)
        return {'name': slug, 'state': UNKNOWN}

    if slug_data['branch']['state'] == "passed":
        state = SUCCESS
    elif slug_data['branch']['state'] == "failed":
        state = FAILED
    elif slug_data['branch']['state'] == "started":
        state = IN_PROGRESS
    else:
        state = UNKNOWN

    return {'name': slug, 'state': state, 'style': convert_status_to_style(state)}


def fetch_travis_ci(build):
    token = current_app.config['TEAMBOARD_SETTINGS']['tokens']['travis_token']
    t = Travis(build['url'], token)

    repo = build['repo']
    status, repo_data = t.repos[repo].get()

    if status != 200:
        teamboard_logger().warning("Unable to get CI status for repo %s" % repo)
        teamboard_logger().debug("Response status: %s - %s" % (status, t.getheaders()))

    result = {
        'status': SUCCESS,
        'jobs': []
    }

    for project in repo_data['repos']:
        if project['active']:
            job_status = get_travis_job_status(t, project, 'master')

            if job_status['state'] != SUCCESS:
                result['jobs'].append(job_status)

            if result['status'] is not FAILED and job_status['state'] is IN_PROGRESS:
                result['status'] = IN_PROGRESS
            elif job_status['state'] is FAILED:
                result['status'] = FAILED

    result['style'] = convert_status_to_style(result['status'])
    result['jobs'] = sorted(result['jobs'], key=lambda x: x['name'])

    return result


def fetch_jenkins_ci(build):
    j = Jenkins(build['url'])

    repo = build['repo']
    status, ci_data = j.view[repo].get()

    if status != 200:
        teamboard_logger().warning("Unable to get CI status for repo %s" % repo)
        teamboard_logger().debug("Response status: %s - %s" % (status, j.getheaders()))

    result = {
        'status': SUCCESS,
        'jobs': []
    }

    for job in ci_data['jobs']:

        if job['color'] == "blue":
            state = SUCCESS
        elif job['color'] in ['red']:
            state = FAILED
        elif job['color'] in ["yellow", "yellow_anime", "blue_anime", "red_anime"]:
            state = IN_PROGRESS
        else:
            # ['grey', 'grey anime', 'disabled', 'disabled anime',
            #  'aborted', 'aborted anime', 'nobuilt', 'nobuilt_anime']
            state = UNKNOWN

        if result['status'] is not FAILED and state is IN_PROGRESS:
            result['status'] = IN_PROGRESS
        elif state is FAILED:
            result['status'] = FAILED

        if state != SUCCESS:
            result['jobs'].append({'name': job['name'], 'state': state, 'style': convert_status_to_style(state)})

    result['style'] = convert_status_to_style(result['status'])
    result['jobs'] = sorted(result['jobs'], key=lambda x: x['name'])

    return result


_ci_fetchers = {
    'travis': fetch_travis_ci,
    'jenkins': fetch_jenkins_ci
}


def fetch_build_status(build):
    build_type = build['type'].lower()

    if build_type in _ci_fetchers:
        return _ci_fetchers[build_type](build)
    else:
        teamboard_logger().warning('Unhandled CI type: %s' % build['type'])


@ci_app.route("/<repo>")
def index(repo):
    """
    :type repo: str
    """
    settings = current_app.config.get('TEAMBOARD_SETTINGS')
    build = None
    ci_list = settings['ci']
    for ci in ci_list:
        if repo.lower() == ci['name'].lower():
            build = dict(ci)

    if build is None:
        abort(404)
    else:
        build['status'] = fetch_build_status(build)
        return render_template('ci.html', build=build)
