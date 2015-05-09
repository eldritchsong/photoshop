__author__ = 'brhoades'
__ver__ = '1.00'

import os
import utils.logger
import StringIO


def int_to_binary(n):

    b_string = ''
    if n < 0:
        raise ValueError("must be a positive integer")
    if n == 0:
        return '0'
    while n > 0:
        b_string += str(n % 2)
        n >>= 1

    return b_string


class PSDFileReader(object):

    def __init__(self, stream):
        """
        Byte reader for Photoshop files
        Photoshop file structure as follows:
        -File Header
        -Color Mode Data
        -Image Resources
        -Layer and Mask Information
        -Image Data
        :return:
        """

        # logging
        self.logger = utils.logger.init_logging()
        self.logger.debug('Initialized <{0}.{1} v{2} object at {3:#018x}>'.format(__name__,
                                                                                  self.__class__.__name__,
                                                                                  __ver__,
                                                                                  id(self)))

        self.stream = stream

        self.stream.seek(0, 2)  # go to end of file to get size
        self.size = self.stream.tell()  # inform of current location
        self.stream.seek(0)  # return to beginning of file
        self._cur_line = 0  # default to start of file

        # start parse
        self.parse()

    def parse(self):
        pass

    def bytes_to_int(self, line):
        bb = reversed(line)
        value = 0
        shift = 0

        for b in bb:
            b = ord(b)
            value += (b << shift)
            shift += 8

        self.logger.debug('bytes_to_int. In: {0}, out: {1}'.format(line, value))
        return value

    def read_short_int(self):
        """
        Read short int (2 bytes)
        :return:
        """
        value = self.stream.read(2)
        value = self.bytes_to_int(value)
        self.logger.debug('readShortInt, value: {0}'.format(value))
        return value

    def read_int(self):
        """
        Read int (4 bytes)
        :return:
        """
        value = self.stream.read(4)
        value = self.bytes_to_int(value)
        self.logger.debug('readInt, value: {0}'.format(value))
        return value

    def read_string(self, size):
        """
        Reads string from file
        :return:
        """
        data = self.stream.read(size)
        value = str(data)
        value = ''.join((s for s in value if ord(s) != 0))  # remove padding characters
        self.logger.debug('readString, size: {0}, value: {1}'.format(size, value))
        return value

    def skip(self, size):
        self.stream.seek(size, 1)  # relative from the current position
        self.logger.debug('skip, size: {0}'.format(size))

    def read_line(self):
        """
        Read bytes of photoshop file
        :return:
        """
        self.logger.debug('stream.tell(): {0}'.format(self.stream.tell()))
        self.logger.debug('stream.size(): {0}'.format(self.size))

        line = ''
        while line == '':
            line = self.stream.readline().strip()
            self._cur_line += 1

        self.logger.debug(line)
        self.logger.debug(self._cur_line)
        height = line[14:18]
        width = line[18:22]
        self.logger.debug(self.bytes_to_int(width))
        self.logger.debug(self.bytes_to_int(height))