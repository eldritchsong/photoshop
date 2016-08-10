__author__ = 'brhoades'

import logging
import logging.handlers
import sys
import re
import os
import time
import inspect
from functools import wraps

from utils import constants
from utils.yaml_cache import g_yaml_cache


def logged(*args, **kwargs):

    def nested_decorator(some_func, log_record=None, unique=False, socket=False):
        log_object = init_logging(some_func, log_record=log_record, unique=unique, socket=socket)

        @wraps(some_func)
        def wrapper(*args, **kwargs):
            return some_func(log=log_object, *args, **kwargs)

        return wrapper

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return nested_decorator(args[0])
    else:
        return lambda func: nested_decorator(func, *args, **kwargs)


def timed(some_func):
    log_object = init_logging(some_func)

    @wraps(some_func)
    def wrapper(*args, **kwargs):
        start = time.time()
        log_object.debug('entering func {0}'.format(some_func))
        ret = some_func(*args, **kwargs)
        log_object.debug('exiting func {0}, elapsed time {1}'.format(some_func, time.time() - start))
        return ret

    return wrapper


def init_logging(obj=None, log_record=None, socket=False, unique=False):

    if not unique and not log_record:  # if sharing same log file, should share same logging instance
        logger = logging.getLogger(__name__)
    else:
        if not obj:  # module level logger
            stack = inspect.stack()  # inspect stack to find caller
            module = inspect.getmodule(stack[1][0])
            filename, _ = os.path.splitext(os.path.basename(module.__file__))
            logger = logging.getLogger('{filename}.{module}'.format(filename=filename,
                                                                    module=module.__name__))
        else:
            if not log_record:  # no log record object passed to logger
                if not inspect.isroutine(obj) and inspect.isclass(type(obj)):
                    filename, _ = os.path.splitext(os.path.basename(inspect.getfile(obj.__class__)))
                    logger = logging.getLogger('{filename}.{module}.{name}'.format(filename=filename,
                                                                                   module=obj.__module__,
                                                                                   name=obj.__class__.__name__))
                else:
                    filename, _ = os.path.splitext(os.path.basename(inspect.getfile(obj)))
                    logger = logging.getLogger('{filename}.{module}.{name}'.format(filename=filename,
                                                                                   module=inspect.getmodule(obj).__name__,
                                                                                   name=obj.__name__))
            else:  # log record passed via socket, create logger based on name
                logger = logging.getLogger(log_record.name)

    if logger.handlers != list():
        return logger

    logger.propagate = False

    tool_name = replace_non_alphanumeric(g_yaml_cache.get('name'))

    # validate directory
    log_path = validate_directory(os.path.join(constants.OS_MAPPINGS[sys.platform],
                                               'dwtv/hub/Pipeline/logs/{tool}/{user}'
                                               .format(tool=tool_name,
                                                       user=constants.CURRENT_USER)))

    if log_path:
        if unique:
            if not log_record:  # no log record object passed to logger
                if not inspect.isroutine(obj) and inspect.isclass(type(obj)):
                    unique_name, _ = os.path.splitext(os.path.basename(inspect.getfile(obj.__class__)))
                else:
                    unique_name, _ = os.path.splitext(os.path.basename(inspect.getfile(obj)))
            else:  # log record passed via socket, grab name of the module for unique name
                unique_name = log_record.module

            if g_yaml_cache.get('debug'):  # separate log file for local debug
                file_handler_path = os.path.join(log_path, '{tool}.{unique}.debug.log'.format(tool=tool_name,
                                                                                              unique=unique_name))
            else:
                file_handler_path = os.path.join(log_path, '{tool}.{unique}.log'.format(tool=tool_name,
                                                                                        unique=unique_name))
        else:
            if g_yaml_cache.get('debug'):  # separate log file for local debug
                file_handler_path = os.path.join(log_path, '{tool}.debug.log'.format(tool=tool_name))
            else:
                file_handler_path = os.path.join(log_path, '{tool}.log'.format(tool=tool_name))

        if not socket:
            hdlr = logging.handlers.TimedRotatingFileHandler(file_handler_path,
                                                             when='midnight',
                                                             backupCount=3,
                                                             delay=True)
        else:
            hdlr = logging.handlers.SocketHandler(constants.REMOTE[g_yaml_cache.get('debug')], 5018)

        hdlr.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(module)s.%(funcName)s %(levelname)s: %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(g_yaml_cache.get('logging_level'))  # console set to info after deployment
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.setLevel(logging.DEBUG)

    return logger


def validate_directory(log_path):
    try:
        if not os.path.isdir(log_path):
            os.makedirs(log_path)

        return log_path

    except OSError, e:
        print 'Unable to create log file, {0}'.format(e)
        return


def replace_non_alphanumeric(value):
    regex = re.compile('[\s]')
    new_value = regex.sub('_', value)
    return new_value.lower()
