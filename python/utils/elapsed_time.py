__author__ = 'brhoades'

import time
import random
import math
from deploy import logger


class ElapsedTimeCalc(object):
    """
    # monte carlo system
    1. Calculate time of currently completed tasks
    2. Take a randomly selected representative percentage of the completed tasks as compared to the remaining tasks
    3. Repeat this 20 times and get a median time
    4. Multiply this median time against the remaining tasks to find estimated time
    """

    def __init__(self, total):
        self._task_start_time = 0
        self._num_of_completed_tasks = 0
        self._scaling = 0  # (total_steps - elapsed_steps) / elapsed_steps
        self._elapsed_time = 0
        self._stored_times = list()
        self._total_tasks = total
        self.logger = logger.init_logging(self)

    def start(self):
        self._task_start_time = time.time()

    def end(self):  # calculate elapsed time
        self._elapsed_time += time.time() - self._task_start_time

        # store unique id with duration of task
        self._stored_times.append(time.time() - self._task_start_time)

        self._num_of_completed_tasks += 1

    def reset(self):
        self._stored_times = list()
        self._scaling = 0
        self._task_start_time = 0
        self._num_of_completed_tasks = 0
        self._task_start_time = 0

    def update_time(self):
        remaining_tasks = self._total_tasks - self._num_of_completed_tasks
        self.logger.debug('remaining_tasks: {0}'.format(remaining_tasks))
        return self._perform_median_calc() * remaining_tasks

    def nice_display(self, granularity=2):
        intervals = (('weeks', 604800),  # 60 * 60 * 24 * 7
                     ('days', 86400),    # 60 * 60 * 24
                     ('hours', 3600),    # 60 * 60
                     ('minutes', 60),
                     ('seconds', 1))

        seconds = self.update_time()
        result = list()

        for name, count in intervals:
            value = seconds // count
            if value:
                seconds %= count
                if value == 1:
                    name = name.rstrip('s')
                result.append("{0} {1}".format(value, name))
        return ', '.join(result[:granularity])

    def _perform_median_calc(self):
        number_of_checks = int(math.floor(self._calculate_sample_size() * len(self._stored_times)))

        self.logger.debug('number of checks: {0}'.format(number_of_checks))

        if number_of_checks < 1:
            return 0

        averages = list()
        for _ in range(20):  # repeat n times for more accuracy
            # randomly selected entries of stored times equal to number of checks
            total = 0
            for x in range(number_of_checks):
                total += random.choice(self._stored_times)

            # calculated average of selected times
            averages.append(total / number_of_checks)
        # calculate median of task
        # when the number of data points is odd, return middle data point
        # when the number is even, return the average of middle two values
        averages = sorted(averages)
        self.logger.debug('averages: {0}'.format(averages))
        is_odd = len(averages) % 2 == 1
        if is_odd:
            median = averages[int(math.floor(len(averages) / 2))]
        else:  # even
            median = float((averages[int(math.floor(len(averages) / 2))]
                            + averages[int(math.floor(len(averages) / 2) + 1)])) / 2.0

        self.logger.debug('median: {0}'.format(median))

        return median

    def _calculate_sample_size(self):
        percentage = (self._total_tasks - self._num_of_completed_tasks) / float(self._total_tasks)
        self.logger.debug('total tasks: {0}'.format(self._total_tasks))
        self.logger.debug('completed tasks: {0}'.format(self._num_of_completed_tasks))
        self.logger.debug('percentage: {0}'.format(percentage))
        return percentage