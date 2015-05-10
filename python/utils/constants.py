__author__ = 'brhoades'

import os

SIGNATURE = '8BPS'
SIGNATURE_8BIM = '8BIM'
VERSION = 1
CHANNELS_RANGE = [1, 56]
SIZE_RANGE = [1, 30000]
DEPTH_LIST = [1, 8, 16, 32]
OPACITY_RANGE = [0, 255]
MODE_LIST = {0: 'Bitmap', 1: 'Grayscale', 2: 'Indexed', 3: 'RGB', 4: 'CMYK', 7: 'Multichannel', 8: 'Duotone', 9: 'Lab'}

TEST_CASE = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'simple_file.psd'))
