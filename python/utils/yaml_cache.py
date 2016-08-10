__author__ = 'brhoades'

import yaml
import os
import sys


def get_yaml_cache(path):

    try:
        with open(path, "r") as fh:
            cache = yaml.load(fh)
    except IOError:
        return None

    return cache


def write_yaml_data(path, data):
    with open(path, "wt") as fh:
        yaml.dump(data, fh)

# walk up the path until config folder
cur_path = __file__
config_location = None
while True:
    config_location = os.path.join(cur_path, 'config', 'environment.yml')
    if os.path.exists(config_location):
        # found config location
        break
    parent_path = os.path.dirname(cur_path)
    if parent_path == cur_path:
        raise OSError('Unable to location config/environment.yml')

    cur_path = parent_path

g_yaml_cache = get_yaml_cache(config_location)