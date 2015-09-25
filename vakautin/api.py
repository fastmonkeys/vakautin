import requests


class CircleAPIError(Exception):
    pass

class CiCLIError(Exception):
    pass


def json_request(request):
    if request.status_code == 200:
        return request.json()
    else:
        raise CircleAPIError(request.json()['message'])


class CircleAPI:
    def __init__(self, api_key):
        assert api_key, "API Key should be defined"
        self.api_key = api_key
        self.rootURL = 'https://circleci.com/api/v1/project/'

    def post_action(
        self,
        username,
        project,
        build_id,
        action=''
    ):
        return json_request(requests.post(
            self.rootURL +
            '%s/%s/%s/%s?circle-token=%s' %
            (
                username,
                project,
                build_id,
                action,
                self.api_key,
            ),
            headers={
                'Accept': 'application/json'
            }
        ))

    def builds(self, limit=100, offset=0):
        return json_request(requests.get(
            'https://circleci.com/api/v1/recent-builds?circle-token=%s'
            '&limit=%s&offset=%s' % (
                self.api_key,
                limit,
                offset
            ),
            headers={
                'Accept': 'application/json'
            }
        ))

    def builds_for_project(
        self,
        username,
        project,
        limit=100,
        offset=0,
        filter_by_status=''
    ):
        return json_request(requests.get(
            self.rootURL +
            '%s/%s?circle-token=%s&limit=%s&offset=%s&filter=%s' %
            (
                username,
                project,
                self.api_key,
                limit,
                offset,
                filter_by_status
            ),
            headers={
                'Accept': 'application/json'
            }
        ))

    def build(self, username, project, build_id):
        return json_request(requests.get(
            'https://circleci.com/api/v1/project/'
            '%s/%s/%s?circle-token=%s' % (
                username,
                project,
                build_id,
                self.api_key
            ),
            headers={
                'Accept': 'application/json'
            }
        ))

    def cancel(self, username, project, build_id):
        return self.post_action(username, project, build_id, 'cancel')

    def retry(self, username, project, build_id):
        return self.post_action(username, project, build_id, 'retry')

    def get_output(self, action):
        return requests.get(action['output_url']).json()[0]['message']
