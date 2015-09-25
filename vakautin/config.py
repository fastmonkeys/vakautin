import os
import logging
import yaml
from schema import Use, Schema, SchemaError, Optional


class InvalidConfig(Exception):
    pass


class MissingConfig(Exception):
    pass


default_config = {
    'debug': False
}
schema = Schema({
    'tracked_repositories': [Use(str)],
    'unstable_tests': [Use(str)],
    'api_key': Use(str),
    'max_attempts': Use(int),
    'debug': Use(bool)
})


def get_config_path():
    current_directory = os.getcwd()
    while True:
        try:
            with open(
                os.path.join(current_directory, 'vakautin.yaml'),
                'rb'
            ) as fp:
                return os.path.join(current_directory, 'vakautin.yaml')
        except IOError:
            pass

        current_directory = os.path.abspath(
            os.path.join(current_directory, '..')
        )
        if current_directory == '/':
            return None


def load_config():
    config = {}
    current_directory = os.getcwd()
    while True:
        try:
            with open(
                os.path.join(current_directory, 'vakautin.yaml'),
                'rb'
            ) as fp:
                config = yaml.safe_load(fp)
                break
        except IOError:
            pass
        current_directory = os.path.abspath(
            os.path.join(current_directory, '..')
        )

        if current_directory == '/':
            break

    if not config:
        raise MissingConfig()

    for k, v in default_config.items():
        if k not in config:
            config[k] = v

    try:
        return schema.validate(config)
    except SchemaError as e:
        raise InvalidConfig(e)


def save_config(config):
    logging.getLogger(__name__).debug('save_config()')
    with open(get_config_path(), "w") as fp:
        yaml.dump(config, fp)
