__author__ = 'brhoades'
__ver__ = '1.00'

import utils.logger
from utils import constants
from sections import PSDHeader, PSDColorMode, PSDImageResources
import StringIO


class PSDFile(object):

    def __init__(self, filename=None, stream=None):

        # init variables
        self.header = None
        self.color_mode = None
        self.image_resources = None

        self.size = None
        self._cur_line = 0
        self.stream = stream
        self.filename = filename

        self.logger = utils.logger.init_logging(self)
        self.logger.info('Initialized <{0}.{1} v{2} object at {3:#018x}>'.format(__name__,
                                                                                 self.__class__.__name__,
                                                                                 __ver__,
                                                                                 id(self)))

        if not self.stream:
            s = open(self.filename, 'rb')
            self.stream = StringIO.StringIO(s.read())

        self.stream.seek(0, 2)  # go to end of file to get size
        self.size = self.stream.tell()  # inform of current location
        self.stream.seek(0)  # return to beginning of file
        self._cur_line = 0  # default to start of file

    def parse(self):
        """
        Parse the psd file
        :return:
        """

        self.header = PSDHeader(self.stream)
        self.color_mode = PSDColorMode(self.stream)
        self.image_resources = PSDImageResources(self.stream)

        self.logger.debug(self.header.__dict__)

if __name__ == '__main__':
    main = PSDFile(constants.TEST_CASE)
    main.parse()