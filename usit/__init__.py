# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

# Define the path of the drivers
import os as _os
_DRIVERS_PATH = _os.path.join(_os.path.dirname(__file__),'drivers')
_USER_FOLDER_PATH = _os.path.join(_os.path.expanduser('~'),'usit')


# User folder and devices_index.ini
from .core.config import config as _config
_config.checkConfig()



# Import moldules
from .core.drivers.drivers import driverManager as drivers
from .core.devices.devices import deviceManager as devices
from .core.recorder_old.recorder import Recorder, Recorder_V2
#from .core.toolbox import toolbox

    
    
    