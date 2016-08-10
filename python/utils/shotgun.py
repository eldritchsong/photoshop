__author__ = 'brhoades'

import sys

from utils import constants

if sys.platform == 'win32':
    sys.path.append('T:/dwtv/hub/Pipeline/archive/python/site-packages')
else:
    sys.path.append('/mnt/dwtv/hub/Pipeline/archive/python/site-packages')
import shotgun_api3


def get_shotgun_api_instance():
    return shotgun_api3.Shotgun(constants.SERVER, constants.SCRIPT, constants.KEY)

shotgun_data = get_shotgun_api_instance()

Fault = shotgun_api3.shotgun.Fault  # shotgun exception

FileDownloadError = shotgun_api3.ShotgunFileDownloadError  # shotgun exception
