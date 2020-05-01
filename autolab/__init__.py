# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""
import os

# Load current version in version file
with open(os.path.join(os.path.dirname(__file__), 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
del version_file

# Process updates from previous versions
from .core import version_adapter
version_adapter.process_all_changes()
del version_adapter

# Load user config
from .core import config
config.initialize_local_directory()
config.check_autolab_config()
del config

# Statistics
from .core import stats
stats.startup()
del stats

# infos
from .core.infos import *

# Devices
from .core.devices import get_device

# WEBBROWSER FUNCTIONS
from .core.web import *

# RECORDER (to be removed at some point)
from .core.recorder import Recorder, Recorder_V2

# GUI
from .core.gui import start as gui
