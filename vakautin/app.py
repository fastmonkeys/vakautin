from .api import CircleAPI
from .config import load_config
import os
import time

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
        for repository in config['tracked_repositories']:
            print("Checking repository %s" % repository)
            username, project = repository.split('/')
            builds = api.builds_for_project(username, project)
            tracked_builds = [build for build in builds]
            failed_builds = [
                build for build in tracked_builds
                if build['status'] == 'failed'
            ]
            unique_failed_builds = set()
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
                times_attempted = not_failed_build_revs.count(
                    build['vcs_revision']
                )
                if not is_running and times_attempted <= config['max_attempts']:
                    unstable_build = is_unstable_build(username, project, build)
                    if unstable_build:
                        print("Retrying build...")
                        print(build['branch'], build['build_url'])
                        if config['debug']:
                            print("Simulating retry...")
                        else:
                            api.retry(username, project, build['build_num'])
        time.sleep(60)
