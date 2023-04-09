# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

# Load current version in version file
from .core import paths as _paths
with open(_paths.VERSION) as version_file:
    __version__ = version_file.read().strip()
del version_file

# Process updates from previous versions
from .core import version_adapter
version_adapter.process_all_changes()
del version_adapter

# Load user config
from .core import config as _config
_config.initialize_local_directory()
_config.check_autolab_config()

# Statistics
from .core import stats as _stats
_stats.startup()

# infos
from .core.infos import list_devices, list_drivers, infos, config_help, statistics

# Devices
from .core.devices import get_device

# Webbrowser shortcuts
from .core.web import report, doc

# Server
from .core.server import Server as server

# GUI
from .core.gui import start as gui

from .core.devices import close
