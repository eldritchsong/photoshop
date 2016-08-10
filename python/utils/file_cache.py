__author__ = 'brhoades'

import os
import string
import random
import inspect

from utils import yaml_cache


def generate_unique_id():
    return ''.join([random.choice(string.digits + string.ascii_lowercase) for _ in range(4)])


class FileCache(object):
    def __init__(self):
        self._cache = dict()

        app_list = yaml_cache.g_yaml_cache.get('apps', dict())
        for k, v in app_list.iteritems():
            self._cache[k.lower()] = v

    @property
    def id(self):
        stack = inspect.stack()  # inspect stack to find caller
        caller = stack[1][1]  # get file name of the caller
        module = inspect.getmodule(stack[1][0])
        file_key, _ = os.path.splitext(os.path.basename(caller))

        # check to see module has a port
        if file_key not in self._cache.keys() or self._cache.get(file_key, dict()).get('port') is None:
            # does not have port, set it
            self._cache.setdefault(file_key.lower(), dict())['port'] = getattr(module, '__port__', None)
            update_yaml_cache()

        if file_key not in self._cache.keys() or self._cache.get(file_key, dict()).get('id') is None:
            # key does not exist
            self._cache.setdefault(file_key.lower(), dict())['id'] = generate_unique_id()
            update_yaml_cache()

        return self._cache[file_key.lower()]['id']

    @property
    def cache(self):
        return self._cache


def update_yaml_cache():
    app_list = yaml_cache.g_yaml_cache.get('apps')

    if app_list is None:
        yaml_cache.g_yaml_cache['apps'] = dict()
        app_list = yaml_cache.g_yaml_cache['apps']

    for k, v in g_file_cache.cache.iteritems():
        if app_list.get(k) is None:
            app_list[k] = v

    yaml_cache.write_yaml_data(yaml_cache.config_location, yaml_cache.g_yaml_cache)


g_file_cache = FileCache()
__id__ = g_file_cache.id


if __name__ == '__main__':
    print __id__
