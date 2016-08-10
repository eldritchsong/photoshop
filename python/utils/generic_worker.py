__author__ = 'brhoades'

from PySide.QtCore import *

import uuid

from deploy import logger
from utils.yaml_cache import g_yaml_cache


class WorkerThread(QThread):

    work_completed = Signal(str, dict)
    work_failure = Signal(str, str)

    def __init__(self):
        super(WorkerThread, self).__init__()
        self._stop = False
        self._queue = list()
        self._queue_mutex = QMutex()
        self._wait_condition = QWaitCondition()
        self._logger = logger.init_logging(self, unique=True)

        self._logger.info('Initializing {0} {1}'.format(self, g_yaml_cache.get('version')))

    def stop(self):
        self._stop = True
        self._logger.info('Attempting to stop the thread')
        self.wait()

    def clear(self):
        self._queue_mutex.lock()
        try:
            self._queue = list()
            self._logger.info('Cleared the queue')
        finally:
            self._queue_mutex.unlock()

    def queue_work(self, some_func, data):

        uid = uuid.uuid4().hex

        work = {'data': data, 'id': uid, 'fn': some_func}
        self._queue_mutex.lock()
        try:
            self._queue.append(work)
            # self._logger.debug('Adding {0} to queue'.format(work))
        finally:
            self._queue_mutex.unlock()

        self._wait_condition.wakeAll()

        return uid

    def run(self):
        while not self._stop:

            self._queue_mutex.lock()
            try:
                if len(self._queue) == 0:  # wait for work
                    self._wait_condition.wait(self._queue_mutex)

                    if len(self._queue) == 0:
                        continue

                job_to_process = self._queue.pop(0)  # pop the last item from the queue
            finally:
                self._queue_mutex.unlock()

            if self._stop:
                break

            try:
                data = job_to_process.get('data')
                # self._logger.debug(data)
                ret = job_to_process['fn'](data)
            except Exception, e:
                if not self._stop:
                    self._logger.exception('An error occurred: {0}'.format(e))
                    self.work_failure.emit(job_to_process['id'], e)
            else:
                if not self._stop:
                    # self._logger.debug('Processed {0}, ret {1}'.format(job_to_process, type(ret)))
                    self.work_completed.emit(job_to_process['id'], ret)
