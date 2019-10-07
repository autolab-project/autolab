# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

# VERSION
import os
with open(os.path.join(os.path.dirname(__file__), 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
del os,version_file

# USER FOLDER CONFIGURATION
from .core.config import check
check()
del check

# DRIVERS
from .core.drivers import DriverManager
drivers = DriverManager()
del DriverManager

# DEVICES
from .core.devices import DeviceManager
devices = DeviceManager()
del DeviceManager

# WEBBROWSER
from .core.web import report,help

# RECORDER
from .core.recorder import Recorder, Recorder_V2

# GUI
from .gui import gui

#raise ValueError()
    
