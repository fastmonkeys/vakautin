# Vakautin

A tool when you have to deal with unstable continuous integration tests. Retries failed builds until they pass or reach maximum number of attempts.

## Configuration

Create `vakautin.yaml` file:

````yaml
unstable_tests:
   - 'name of the test that is unstable'
   - 'if any other tests fail, they are not retried'
tracked_repositories:
   - 'organization/repo'
max_attempts: 3
api_key: 'api_key_from_circleci'
````

## Usage

1. Configure Vakautin
2. Install requirements: `pip install requirements.txt`
3. Run `python3 -m vakautin`
