# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

# Initializing
#from . import core
#core.checkConfig()

__version__ = '1.0'

from . import drivers

from . import core
core.checkConfig()
core.devices.index = core.devices.loadIndex()

devices = core.devices.DeviceManager()

from .core.gui import gui,_run

from .core._report import report
from .core.recorder_old.recorder import Recorder, Recorder_V2

# User folder and devices_index.ini



# Import moldules
#from .core.drivers.drivers import driverManager as drivers
#from .core.devices.devices import deviceManager as devices
#from .core.recorder_old.recorder import Recorder, Recorder_V2
#from .core.gui import main as gui
#
#from .core.report.main import report
#from .core.scanner import main as scanner
#from .core.toolbox import toolbox

    
    
    