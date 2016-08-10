import StringIO

from framework import PSDFileReader
from utils import constants


__author__ = 'brhoades'


def validate(label, value, validator):
    assert label is not None

    if isinstance(validator, list):
        if len(validator) > 2:
            # option-type validator
            if value not in validator:
                raise BaseException('{0} should be one of {1}'.format(value, ', '.join(validator)))
        else:
            # range-type validator
            if value < validator[0] or value > validator[1]:
                raise BaseException('{0} should be between {1} and {2}'.format(value, validator[0], validator[1]))
    elif isinstance(validator, dict):
        if value not in validator.keys():
            raise BaseException('{0} should be one of {1}, but is {2}'.format(label,
                                                                              ', '.join(str(i) for i in validator.keys()),
                                                                              value))
    else:
        if value != validator:
            raise BaseException('{0} should be {1}'.format(value, validator))


class PSDHeader(PSDFileReader):

    def __init__(self, stream):

        # init variables
        self.signature = None
        self.version = None
        self.channels = None
        self.height = None
        self.width = None
        self.depth = None
        self.mode = None

        # parse() is called in __init__ of PSDFileReader which causes PSDHeader __init__ to overwrite the value
        # if super before declaration of variables
        super(PSDHeader, self).__init__(stream)

    def parse(self):
        """
        Read the header
        Header contains the basic properties of the image. Length: 26 bytes
        :return:
        """

        self.logger.debug('parse {0} object at {1:#018x}'.format(self.__class__.__name__, id(self)))

        # Signature
        # 4 bytes.
        # Always equal to 8BPS.
        self.signature = self.read_string(4)
        validate('Signature', self.signature, constants.SIGNATURE)

        # Version
        # 2 bytes
        # Always equal to 1
        self.version = self.read_short_int()
        validate('Version', self.version, constants.VERSION)

        # Reserved
        # 6 bytes
        # Must be zero
        self.skip(6)

        # Channels
        # 2 bytes
        # Between 1 and 56
        self.channels = self.read_short_int()
        validate('Channels', self.channels, constants.CHANNELS_RANGE)

        # Height
        # 4 bytes
        # Between 1 and 30,000
        self.height = self.read_int()
        validate('Height', self.height, constants.SIZE_RANGE)

        # Width
        # 4 bytes
        # Between 1 and 30,000
        self.width = self.read_int()
        validate('Width', self.width, constants.SIZE_RANGE)

        # Bit depth
        # 2 bytes
        # Supported values are 1, 8, 16, 32
        self.depth = self.read_short_int()
        validate('Depth', self.depth, constants.DEPTH_LIST)

        # Color mode
        # 2 bytes
        # Bitmap = 0, Grayscale = 1, Indexed = 2, RBG = 3, CMYK = 4, Multichannel = 8, Duotone = 8, Lab = 9
        self.mode = self.read_short_int()
        validate('Mode', self.mode, constants.MODE_LIST)
        self.mode = constants.MODE_LIST[self.mode]


class PSDColorMode(PSDFileReader):
    """
    Only indexed color and duotone (see the mode field in the File header section) have color mode data.
    For all other modes, this section is just the 4-byte length field, which is set to zero.

    Indexed color images: length is 768; color data contains the color table for the image, in non-interleaved order.

    Duotone images: color data contains the duotone specification (the format of which is not documented).
    Other applications that read Photoshop files can treat a duotone image as a gray image, and just preserve the
    contents of the duotone information when reading and writing the file.
    """

    def __init__(self, stream):
        super(PSDColorMode, self).__init__(stream)

    def parse(self):

        # for now, skip this section
        self.skip(4)


class PSDImageResources(PSDFileReader):
    """
    The third section of the file contains image resources.
    It starts with a length field, followed by a series of resource blocks.
    """

    def __init__(self, stream):
        super(PSDImageResources, self).__init__(stream)

    def parse(self):

        length = self.read_int()
        self.logger.debug(length)

        # Signature
        # 4 bytes
        # Must be 8BIM
        signature = self.read_string(4)
        validate('Signature', signature, constants.SIGNATURE_8BIM)

if __name__ == '__main__':
    s = None
    try:
        s = open(constants.TEST_CASE, 'rb')
        s = StringIO.StringIO(s.read())

        header = PSDHeader(s)
        color_mode = PSDColorMode(s)
        image_resources = PSDImageResources(s)
    finally:
        if s:
            s.close()
