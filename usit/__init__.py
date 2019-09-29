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

    