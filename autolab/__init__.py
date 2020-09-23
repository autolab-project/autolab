# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

@author: quentin.chateiller
"""

__version__ = 2.0
# # Load current version in version file
# from .core import paths as _paths
# with open(_paths.VERSION) as version_file:
#     __version__ = version_file.read().strip()
# del version_file

# Process updates from previous versions
from .core import updater
updater.process_all_changes()
del updater

# Load user config
from .core import config
config.check_local_directory()
config.check_autolab_config()
del config

# Telemetry
from .core import telemetry
#telemetry.startup()
del telemetry

# # infos
# from .core.infos import list_devices, list_drivers, infos, config_help, statistics

# # Devices
# from .core.devices import get_device

# Webbrowser shortcuts
from .core.web import community, docs

# # Server
# from .core.server import Server as server

# # GUI
# from .core.gui import start as gui
