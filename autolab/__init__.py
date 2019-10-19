# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""
import os, shutil

# VERSION
with open(os.path.join(os.path.dirname(__file__), 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
del version_file

# PATHS
from .core import paths

# LOCAL STRUCTURE
if os.path.exists(paths.USER_FOLDER) is False :    # LOCAL FOLDER
    os.mkdir(paths.USER_FOLDER)
    print(f'INFORMATION: The local folder AUTOLAB has been created : {paths.USER_FOLDER_PATH}')

if os.path.exists(paths.LOCAL_CONFIG) is False : # LOCAL CONFIG
    shutil.copyfile(paths.LOCAL_CONFIG_TEMPLATE,paths.LOCAL_CONFIG)
    print(f'INFORMATION: The configuration file devices_index.ini has been created : {paths.LOCAL_CONFIG}')
    
if os.path.exists(paths.DRIVER_SOURCES['local']) is False : # lOCAL CUSTOM DRIVER FOLDER
    os.mkdir(paths.DRIVER_SOURCES['local'])


# DRIVERS
from .core.drivers import *

# DEVICES
from .core.devices import *

# WEBBROWSER FUNCTIONS
from .core.web import report,help

# RECORDER (to be removed at some point)
from .core.recorder import Recorder, Recorder_V2

# GUI
from .gui import gui

    
del os, shutil