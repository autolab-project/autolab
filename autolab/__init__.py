# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""
import os

# VERSION
with open(os.path.join(os.path.dirname(__file__), 'version.txt')) as version_file:
    __version__ = version_file.read().strip()
del version_file

# PATHS
from .core import paths

# CONFIG
from .core import stats as _stats
from .core import config as _config
_config.check()

# STATS
from .core.stats import set_stats_enabled, is_stats_enabled
_stats.startup()

# DRIVERS
from .core.drivers import *

# DEVICES
from .core.devices import *

# WEBBROWSER FUNCTIONS
from .core.web import *

# RECORDER (to be removed at some point)
from .core.recorder import Recorder, Recorder_V2

# GUI
from .core.gui import start as gui


