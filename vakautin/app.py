from .api import CircleAPI, CircleAPIError
from .config import load_config

import os
from dateutil.tz import tzlocal
from dateutil import parser
from datetime import datetime, timedelta
import time
import requests

__version__ = '0.1.0'


def main():
    print("Vakautin %s" % __version__)
    config = load_config()
    api = CircleAPI(config['api_key'])

    def is_unstable_build(username, project, build):
        build_details = api.build(username, project, build['build_num'])
        for step in build_details['steps']:
            step_statuses = {x['status'] for x in step['actions']}
            if (
                step['name'] not in config['unstable_tests'] and
                step_statuses != {'success'}
            ):
                return False
        return True

    # TODO: webhooks
    print("Running in pull mode...")

    while True:
        sleep_time = 3600

        try:
            for repository in config['tracked_repositories']:
                print("Checking repository %s" % repository)
                username, project = repository.split('/')
                builds = api.builds_for_project(username, project)
                tracked_builds = [build for build in builds]

                last_build = parser.parse(tracked_builds[0]['author_date'])
                if (datetime.now(tzlocal()) - last_build) < timedelta(hours=1):
                    sleep_time = 60

                failed_builds = [
                    build for build in tracked_builds
                    if build['status'] in {'failed', 'timedout'}
                ]
                unique_failed_builds = set()
                failed_build_revs = [
                    build['vcs_revision'] for build in failed_builds
                ]
                not_failed_build_revs = [
                    build['vcs_revision'] for build in tracked_builds
                    if build not in failed_builds
                ]
                checked_branches = set()

                for build in failed_builds:
                    if build['branch'] in checked_branches:
                        continue

                    checked_branches.add(build['branch'])

                    is_running = build['vcs_revision'] in not_failed_build_revs
                    times_attempted = failed_build_revs.count(
                        build['vcs_revision']
                    )
                    if not is_running and times_attempted < config['max_attempts']:
                        unstable_build = is_unstable_build(username, project, build)
                        if unstable_build:
                            print("Retrying build...")
                            print(build['branch'], build['build_url'])
                            if config['debug']:
                                print("Simulating retry...")
                            else:
                                api.retry(username, project, build['build_num'])
        except CircleAPIError as e:
            print(e)
            sleep_time = 1800
        except requests.exceptions.RequestException as e:
            print(e)

        time.sleep(sleep_time)
