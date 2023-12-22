# -*- coding: utf-8 -*-
"""
Created on Fri May 17 15:04:04 2019

Python package for scientific experiments automation

The purpose of this package it to provide easy and efficient tools to deal with your scientific instruments, and to run automated experiments with them, by command line instructions or through a graphical user interface (GUI).

Created by Quentin Chateiller, Python drivers from Quentin Chateiller and Bruno Garbin, for the C2N-CNRS (Center for Nanosciences and Nanotechnologies, Palaiseau, France) ToniQ team.
New drivers and autolab updates created by Jonathan Peltier, for the C2N, Minaphot team.

Visit https://autolab.readthedocs.io/ for the full documentation of this package.
"""
import numpy  # OPTIMIZE: temporary fix to an infinite loading on some computer following the master merge (commit 25fd4d6)
import socket  # OPTIMIZE: temporary fix to an infinite loading on some computer

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
_config.check_plotter_config()
_config.set_temp_folder()

# infos
from .core.infos import list_devices, list_drivers, infos, config_help

# Devices
from .core.devices import get_device, close
from .core import devices as _devices

# Drivers
from .core.drivers import get_driver, explore_driver
from .core import drivers as _drivers

# Webbrowser shortcuts
from .core.web import report, doc

# Server
from .core.server import Server as server

# GUI
from .core.gui import start as gui

# Repository
from .core.repository import install_drivers
from .core import repository as _repository
_repository._check_empty_driver_folder()

del numpy
del socket
