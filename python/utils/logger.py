__author__ = 'Ben'

import logging
import logging.handlers
import os


def init_logging():
    logger = logging.getLogger(__name__)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    log_path = os.path.realpath(os.path.join(__file__, '..', '..', '..', 'logs'))

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, 'photoshop.log'),
                                                             when='midnight',
                                                             backupCount=10)
    file_handler.setLevel(logging.DEBUG)

    logger.addHandler(handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger